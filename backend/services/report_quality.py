# ===========================================================================
# Report Quality & Text Processing Utilities
# Extracted from server.py — pure utility functions for report text cleaning
# ===========================================================================

import re
from services.offence_helpers import enforce_forensic_language


def _normalise_text(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", (value or "").lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def _token_set(value: str) -> set:
    return {token for token in _normalise_text(value).split(" ") if len(token) > 3}


def _jaccard_similarity(set_a: set, set_b: set) -> float:
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return 0.0 if union == 0 else intersection / union


def _build_anchor_terms(case: dict, documents: list, timeline: list, grounds: list) -> set:
    terms = set()

    def add_terms(value):
        if not value:
            return
        for token in re.split(r"[^a-z0-9]+", str(value).lower()):
            if len(token) > 3:
                terms.add(token)

    for field in ["title", "defendant_name", "case_number", "court", "judge", "sentence", "state", "offence_type", "offence_category"]:
        add_terms(case.get(field))

    for doc in documents or []:
        add_terms(doc.get("filename"))
        add_terms(doc.get("category"))
        add_terms(doc.get("document_type"))

    for event in timeline or []:
        add_terms(event.get("title"))
        add_terms(event.get("event_type"))
        add_terms(event.get("event_date"))

    for ground in grounds or []:
        add_terms(ground.get("title"))
        add_terms(ground.get("ground_type"))

    return terms


def _paragraph_quality_score(paragraph: str, anchor_terms: set) -> float:
    if not paragraph:
        return 0.0
    score = 0.0
    if re.search(r"\b\d{2,}\b", paragraph):
        score += 1.1
    if re.search(r"\b(s\.|section)\s*\d+", paragraph, re.I):
        score += 1.2
    if re.search(r"\bAct\s+\d{4}\b", paragraph, re.I):
        score += 1.0
    if re.search(r"\bR\s+v\b", paragraph) or re.search(r"\bNSWCCA\b", paragraph):
        score += 0.9

    word_set = _token_set(paragraph)
    if anchor_terms and word_set:
        anchor_hits = sum(1 for word in word_set if word in anchor_terms)
        score += min(2.0, anchor_hits * 0.25)

    score += min(1.4, len(paragraph) / 1200)
    return score


def _split_report_sections(text: str) -> list:
    parts = re.split(r"(^##\s+\d+\.\s+.+$)", text, flags=re.M)
    if len(parts) <= 1:
        return [("", text.strip())]

    sections = []
    lead = parts[0].strip()
    if lead:
        sections.append(("", lead))

    for index in range(1, len(parts), 2):
        heading = parts[index].strip()
        content = parts[index + 1] if index + 1 < len(parts) else ""
        sections.append((heading, content.strip()))

    return sections


def _enforce_forensic_language(text: str) -> str:
    """Wrapper — delegates to shared enforce_forensic_language in offence_helpers."""
    return enforce_forensic_language(text)



def _dedupe_report_content(text: str, report_type: str, anchor_terms: set) -> str:
    """DO_NOT_UNDO — Dedup thresholds are FINAL. 0.97 for multi-pass, 0.90 for single-pass.
    Previous 0.82 threshold stripped ~50% of valid report content. NEVER lower below 0.90."""
    if not text:
        return text

    # DO_NOT_UNDO — Multi-pass reports must NOT be deduped aggressively
    if report_type in ("full_detailed", "extensive_log"):
        similarity_threshold = 0.97
    else:
        similarity_threshold = 0.90

    sections = _split_report_sections(text)
    cleaned_sections = []

    for heading, content in sections:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", content) if p.strip()]
        kept = []
        seen_sets = []
        seen_texts = []

        for paragraph in paragraphs:
            if len(paragraph) < 40:
                kept.append(paragraph)
                continue

            paragraph_set = _token_set(paragraph)
            is_duplicate = False
            for existing_set, existing_text in zip(seen_sets, seen_texts):
                # Only strip if one paragraph is a substring of another (exact containment)
                if paragraph in existing_text or existing_text in paragraph:
                    is_duplicate = True
                    break
                if _jaccard_similarity(paragraph_set, existing_set) > similarity_threshold:
                    is_duplicate = True
                    break

            if is_duplicate:
                continue

            kept.append(paragraph)
            seen_sets.append(paragraph_set)
            seen_texts.append(paragraph)

        cleaned_sections.append((heading, "\n\n".join(kept).strip()))

    rebuilt = []
    for heading, content in cleaned_sections:
        if heading:
            rebuilt.append(heading)
        if content:
            rebuilt.append(content)

    return "\n\n".join(rebuilt).strip()


def _strip_report_placeholders(text: str) -> str:
    if not text:
        return text
    cleaned_lines = []
    for line in text.splitlines():
        if re.search(r"\[Your Name\]|\[Your Legal Organisation/Team\]", line, re.I):
            continue
        if re.search(r"Best regards|Prepared by|Prepared for|This report was generated by|Criminal Appeal AI|Justitia AI", line, re.I):
            continue
        if re.search(r"\bDO NOT UNDO\.?\b", line, re.I):
            continue
        cleaned_lines.append(line)
    cleaned = "\n".join(cleaned_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    # Strip \1 artifacts
    cleaned = cleaned.replace("\\1", "")
    cleaned = cleaned.replace("\x01", "")
    # Strip prompt instruction text from section headings
    cleaned = re.sub(r'\s*—\s*keep ALL[^\n]*', '', cleaned)
    cleaned = re.sub(r'\s*—\s*DETAILED PATHWAY ANALYSIS[^\n]*', '', cleaned)
    cleaned = re.sub(r'\s*\(\d+\+?\s*words[^)]*\)', '', cleaned)  # e.g. "(900+ words per ground, flowing paragraphs)"
    cleaned = re.sub(r'\s*\(\d+\+?\s*CASES[^)]*\)', '', cleaned)  # e.g. "(12+ CASES with full citations)"
    cleaned = re.sub(r'(GROUNDS OF MERIT)\s*—\s*DEEP ANALYSIS', r'\1', cleaned)
    # Sanitise "we/us/our" language — convert to third-person educational tone
    we_us_replacements = [
        (r'\bWe are arguing\b', 'The applicant argues'),
        (r'\bwe are arguing\b', 'the applicant argues'),
        (r'\bWe are aiming\b', 'The appeal aims'),
        (r'\bwe are aiming\b', 'the appeal aims'),
        (r'\bWe are filing\b', 'The legal professional is filing'),
        (r'\bwe are filing\b', 'the legal professional is filing'),
        (r'\bWe are taking\b', 'The legal professional is taking'),
        (r'\bwe are taking\b', 'the legal professional is taking'),
        (r'\bWe succeed\b', 'The appeal succeeds'),
        (r'\bwe succeed\b', 'the appeal succeeds'),
        (r'\bwe will gather\b', 'the legal professional will gather'),
        (r'\bWe will gather\b', 'The legal professional will gather'),
        (r'\bwe will craft\b', 'the legal professional will craft'),
        (r'\bWe will craft\b', 'The legal professional will craft'),
        (r'\bwe will file\b', 'the legal professional will file'),
        (r'\bWe will file\b', 'The legal professional will file'),
        (r'\bwe will prepare\b', 'the legal professional will prepare'),
        (r'\bWe will prepare\b', 'The legal professional will prepare'),
        (r'\bwe will submit\b', 'the legal professional will submit'),
        (r'\bWe will submit\b', 'The legal professional will submit'),
        (r'\bwe will seek\b', 'the applicant will seek'),
        (r'\bWe will seek\b', 'The applicant will seek'),
        (r'\bwe will argue\b', 'the applicant will argue'),
        (r'\bWe will argue\b', 'The applicant will argue'),
        (r'\bwe will demonstrate\b', 'the appeal will demonstrate'),
        (r'\bWe will demonstrate\b', 'The appeal will demonstrate'),
        (r'\bwe will show\b', 'the appeal will show'),
        (r'\bWe will show\b', 'The appeal will show'),
        (r'\bcontact with us\b', 'contact with the legal professional'),
        (r'\bContact us\b', 'Contact the legal professional'),
        (r'\bcontact us\b', 'contact the legal professional'),
        (r'\bour submissions\b', 'the submissions'),
        (r'\bOur submissions\b', 'The submissions'),
        (r'\bour claims\b', "the applicant's claims"),
        (r'\bOur claims\b', "The applicant's claims"),
        (r'\bour arguments\b', "the applicant's arguments"),
        (r'\bOur arguments\b', "The applicant's arguments"),
        (r'\bour position\b', "the applicant's position"),
        (r'\bOur position\b', "The applicant's position"),
        (r'\bour case\b', "the applicant's case"),
        (r'\bOur case\b', "The applicant's case"),
        (r'\bour strategy\b', 'the legal strategy'),
        (r'\bOur strategy\b', 'The legal strategy'),
        (r'\bour analysis\b', 'this analysis'),
        (r'\bOur analysis\b', 'This analysis'),
        (r'\bon our behalf\b', 'on behalf of the applicant'),
        (r'\bback our\b', "support the applicant's"),
        (r'\bensuring our\b', 'ensuring the'),
        (r', we are\b', ', the legal professional is'),
        (r', we will\b', ', the legal professional will'),
        (r', we have\b', ', the legal professional has'),
        (r'\bWe have identified\b', 'This analysis has identified'),
        (r'\bwe have identified\b', 'this analysis has identified'),
        (r'\bWe have reviewed\b', 'This analysis has reviewed'),
        (r'\bwe have reviewed\b', 'this analysis has reviewed'),
        (r'\bWe have analysed\b', 'This analysis has examined'),
        (r'\bwe have analysed\b', 'this analysis has examined'),
        (r'\bWe have analyzed\b', 'This analysis has examined'),
        (r'\bwe have analyzed\b', 'this analysis has examined'),
    ]
    for pattern, replacement in we_us_replacements:
        cleaned = re.sub(pattern, replacement, cleaned)
    
    # Catch-all: replace remaining "we " patterns at sentence boundaries
    cleaned = re.sub(r'\bwe facilitate\b', 'this analysis facilitates', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe recommend\b', 'it is recommended', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe note\b', 'it is noted', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe observe\b', 'it is observed', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe consider\b', 'it is considered', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe conclude\b', 'it is concluded', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe suggest\b', 'it is suggested', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe assess\b', 'this analysis assesses', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe examine\b', 'this analysis examines', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe highlight\b', 'this analysis highlights', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe identify\b', 'this analysis identifies', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe believe\b', 'it is assessed', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe find\b', 'this analysis finds', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe can see\b', 'it can be seen', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe can\b', 'the applicant can', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe must\b', 'the legal professional must', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe should\b', 'the legal professional should', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe need\b', 'the legal professional needs', cleaned, flags=re.I)
    cleaned = re.sub(r', we \b', ', the analysis ', cleaned)
    cleaned = re.sub(r'\. We \b', '. This analysis ', cleaned)
    # Catch remaining "our" possessives
    cleaned = re.sub(r'\bour client\b', 'the applicant', cleaned, flags=re.I)
    cleaned = re.sub(r'\bour focus\b', 'the focus', cleaned, flags=re.I)
    cleaned = re.sub(r'\bour team\b', 'the legal professional', cleaned, flags=re.I)
    cleaned = re.sub(r'\bour review\b', 'this review', cleaned, flags=re.I)
    cleaned = re.sub(r'\bour assessment\b', 'this assessment', cleaned, flags=re.I)
    cleaned = re.sub(r'\bour examination\b', 'this examination', cleaned, flags=re.I)
    
    # Strip "you/your" language — third-person only
    you_your_replacements = [
        (r'\byour opportunity\b', 'the opportunity'),
        (r'\bYour opportunity\b', 'The opportunity'),
        (r'\byour conviction\b', 'the conviction'),
        (r'\bYour conviction\b', 'The conviction'),
        (r'\bgiven to you\b', 'imposed'),
        (r'\bGiven to you\b', 'Imposed'),
        (r'\byour sentence\b', 'the sentence'),
        (r'\bYour sentence\b', 'The sentence'),
        (r'\byour appeal\b', 'the appeal'),
        (r'\bYour appeal\b', 'The appeal'),
        (r'\byour case\b', 'the case'),
        (r'\bYour case\b', 'The case'),
        (r'\byour trial\b', 'the trial'),
        (r'\bYour trial\b', 'The trial'),
        (r'\byour lawyer\b', 'the legal representative'),
        (r'\bYour lawyer\b', 'The legal representative'),
        (r'\byour barrister\b', 'the barrister'),
        (r'\bYour barrister\b', 'The barrister'),
        (r'\byour solicitor\b', 'the solicitor'),
        (r'\bYour solicitor\b', 'The solicitor'),
        (r'\byour legal team\b', 'the legal team'),
        (r'\bYour legal team\b', 'The legal team'),
        (r'\byour legal representative\b', 'the legal representative'),
        (r'\bYour legal representative\b', 'The legal representative'),
        (r'\byour defence\b', 'the defence'),
        (r'\bYour defence\b', 'The defence'),
        (r'\byour rights\b', 'the rights of the applicant'),
        (r'\bYour rights\b', 'The rights of the applicant'),
        (r'\byour circumstances\b', 'the circumstances'),
        (r'\bYour circumstances\b', 'The circumstances'),
        (r'\byour situation\b', 'the situation'),
        (r'\bYour situation\b', 'The situation'),
        (r'\byour matter\b', 'this matter'),
        (r'\bYour matter\b', 'This matter'),
        (r'\byour prospects\b', 'the prospects'),
        (r'\bYour prospects\b', 'The prospects'),
        (r'\byour grounds\b', 'the grounds'),
        (r'\bYour grounds\b', 'The grounds'),
        (r'\byour documents\b', 'the documents'),
        (r'\bYour documents\b', 'The documents'),
        (r'\byou may\b', 'the applicant may'),
        (r'\bYou may\b', 'The applicant may'),
        (r'\byou can\b', 'the applicant can'),
        (r'\bYou can\b', 'The applicant can'),
        (r'\byou should\b', 'the applicant should'),
        (r'\bYou should\b', 'The applicant should'),
        (r'\byou must\b', 'the applicant must'),
        (r'\bYou must\b', 'The applicant must'),
        (r'\byou will\b', 'the applicant will'),
        (r'\bYou will\b', 'The applicant will'),
        (r'\byou need\b', 'the applicant needs'),
        (r'\bYou need\b', 'The applicant needs'),
        (r'\byou have\b', 'the applicant has'),
        (r'\bYou have\b', 'The applicant has'),
        (r'\byou are\b', 'the applicant is'),
        (r'\bYou are\b', 'The applicant is'),
        (r'\byou were\b', 'the applicant was'),
        (r'\bYou were\b', 'The applicant was'),
        (r'\bfor you\b', 'for the applicant'),
        (r'\bFor you\b', 'For the applicant'),
        (r'\bto you\b', 'to the applicant'),
        (r'\bTo you\b', 'To the applicant'),
        (r'\bagainst you\b', 'against the applicant'),
        (r'\bAgainst you\b', 'Against the applicant'),
        (r'\bif you\b', 'if the applicant'),
        (r'\bIf you\b', 'If the applicant'),
        (r'\bwhen you\b', 'when the applicant'),
        (r'\bWhen you\b', 'When the applicant'),
    ]
    for pattern, replacement in you_your_replacements:
        cleaned = re.sub(pattern, replacement, cleaned)
    # Catch remaining "your" as possessive — broad catch-all
    cleaned = re.sub(r'\byour\b', "the applicant's", cleaned)
    cleaned = re.sub(r'\bYour\b', "The applicant's", cleaned)
    
    # Strip placeholder/future-tense filler text
    cleaned = re.sub(r'(?:The |This )?(?:comparative sentencing |sentencing )?table (?:below )?will (?:reference|provide|include|contain|show|list|detail|present|outline|cover)\b', 'The table references', cleaned, flags=re.I)
    cleaned = re.sub(r'(?:Details|Information|Data|Analysis|Content),?\s*(?:including [^,]+,?\s*)?will be provided\b', 'Details are provided', cleaned, flags=re.I)
    
    # Fix broken markdown links: <Text> [Text](url) → just [Text](url)
    cleaned = re.sub(r'<([^>]+)>\s*\[([^\]]+)\]\(([^)]+)\)', r'[\2](\3)', cleaned)
    # Fix raw angle-bracket links: <Text> without markdown
    cleaned = re.sub(r'<(Search [^>]+)>', r'\1', cleaned)
    
    # Enforce forensic appellate language — catch over-assertive declarations
    cleaned = _enforce_forensic_language(cleaned)
    
    return cleaned


def _sanitise_suspect_authorities(text: str) -> str:
    """Post-processing gate that flags or strips suspect LLM-fabricated case citations.
    
    DO NOT UNDO — Prevents fabricated authorities from landing in saved/exported reports.
    Catches:
    - Placeholder citations: [Surname] [Year], [Year] NSWCCA [Number]
    - Obviously templated citations: "R v [Name]", "citation verification needed"
    - Suspiciously round paragraph numbers: at [100], at [200]
    - "section not provided" placeholders
    
    Does NOT strip citations that look real (e.g. "R v Smith [2015] NSWCCA 123 at [45]").
    Instead of removing suspect citations entirely, wraps them in a caveat so the user
    knows to verify, preserving the analytical context.
    """
    if not text:
        return text
    
    # Strip obvious placeholder citations
    text = re.sub(
        r'\[Surname\]|\[Name\]|\[Year\]|\[Number\]|\[Citation\]|\[Court\]',
        '[citation verification required]',
        text,
        flags=re.I
    )
    # Strip "citation verification needed" or "citation pending" as standalone lines
    text = re.sub(
        r'\n[^\n]*(?:citation verification needed|citation pending|citation to be confirmed|citation unavailable)[^\n]*\n',
        '\n',
        text,
        flags=re.I
    )
    # Strip "section not provided" placeholders
    text = re.sub(
        r'(?:section|s\.?)\s+not\s+provided',
        '[section number to be confirmed]',
        text,
        flags=re.I
    )
    # Flag obviously templated case references: "R v [anything in brackets]"
    text = re.sub(
        r'R\s+v\s+\[([A-Z][a-z]+)\]\s*\[(\d{4})\]',
        r'R v \1 [\2] [citation unverified]',
        text
    )
    # Flag suspiciously perfect paragraph references like "at [100]", "at [200]", "at [300]"
    text = re.sub(
        r'at\s+\[([1-9]00)\]',
        r'at [\1] [paragraph number unverified]',
        text
    )
    # Strip AustLII links that are clearly templated (contain placeholder segments)
    text = re.sub(
        r'https?://www\.austlii\.edu\.au/[^\s\)]*\[(?:Year|Number|Citation)\][^\s\)]*',
        '[AustLII link to be verified]',
        text,
        flags=re.I
    )
    
    return text



def _clean_sentence_candidate(value: str) -> str:
    cleaned = (value or "")
    cleaned = re.sub(r"\s*\[.*$", "", cleaned)
    cleaned = re.sub(r"\s*\(https?:.*$", "", cleaned)
    cleaned = re.sub(r"\s*[|•].*$", "", cleaned)
    cleaned = re.sub(r"[,;:]?\s*(?:appeal|conviction|leave|outcome)\b.*$", "", cleaned, flags=re.I)
    cleaned = re.sub(r"[,;:]?\s*(?:dismissed|upheld|refused|granted)\b.*$", "", cleaned, flags=re.I)
    # DO NOT UNDO — Strip crime narrative like "for murdering pregnant girlfriend"
    cleaned = re.sub(r"\s+for\s+(?:the\s+)?(?:murder|killing|manslaughter|assault|robbery|rape|kidnapping|abuse|stabbing|supplying|dealing|trafficking)[a-z\s,'-]*(?=\s+with\b|,|$)", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s+for\s+[a-z\s'-]+(?=,|\s+with\b|$)", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\bminimum\s+non[- ]?parole\s+period\b", "non-parole period", cleaned, flags=re.I)
    cleaned = re.sub(r"\bwith\s+a\s+minimum\s+non[- ]?parole\s+period\b", "with a non-parole period", cleaned, flags=re.I)
    cleaned = re.sub(r"imprisonment,\s+with", "imprisonment with", cleaned, flags=re.I)
    return re.sub(r"\s+", " ", cleaned).strip()


def _is_valid_sentence_candidate(value: str) -> bool:
    if not value:
        return False
    if not re.search(r"(life|year|month|non[- ]?parole|imprisonment|gaol|custody|sentence)", value, re.I):
        return False
    if re.search(r"\b(reduced|reduce|precedent|appeal|submissions|could|should|potentially|perhaps|would|adequacy|seek|sought|relief)\b", value, re.I):
        return False
    return len(value) < 140
