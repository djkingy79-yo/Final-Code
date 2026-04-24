# DO NOT UNDO — staged classification pipeline. Additive module.
from services.llm_service import call_llm_for_json
from services.pipeline_models import IssueClassification
from services.offence_helpers import _build_recent_legislation_context, _build_state_framework_context, _build_federal_framework_context

# DO NOT UNDO — Pipeline ground type taxonomy.
#
# The AI prompt accepts a broad vocabulary so the LLM can express fine-grained
# distinctions. After the LLM responds, _remap_to_canonical_bucket() collapses
# every label into one of the five canonical buckets used throughout the rest
# of the system (ground_normaliser, grounds router, reports).
#
# Canonical five buckets (GroundType in services/ground_normaliser.py):
#   conviction | sentence | procedure | evidence | ineffective_counsel
#
# 7-step pipeline:
#   1. Raw AI output          (classify_case_issues -> LLM)
#   2. Extract candidates     (parsed from JSON)
#   3. Classify / remap       (_remap_to_canonical_bucket — this step)
#   4. Split mixed grounds    (ground_normaliser.split_mixed_ground)
#   5. Merge duplicates       (ground_dedup, _merge_overlapping_grounds)
#   6. Reorder by priority    (_issue_priority_rank / TYPE_PRIORITY)
#   7. Render report          (report_generator / barrister_generator)
GROUND_TYPES = {
    "procedural_error",
    "fresh_evidence",
    "miscarriage_of_justice",
    "sentencing_error",
    "judicial_error",
    "ineffective_counsel",
    "prosecution_misconduct",
    "jury_irregularity",
    "constitutional_violation",
    "other",
}

# Five canonical buckets — the only values the normaliser, grounds router,
# and reports understand.
CANONICAL_BUCKETS = frozenset({"conviction", "sentence", "procedure", "evidence", "ineffective_counsel"})

# Mapping from broad AI label -> canonical bucket.
_LABEL_TO_BUCKET: dict[str, str] = {
    "conviction": "conviction",
    "miscarriage_of_justice": "conviction",
    "judicial_error": "conviction",
    "fresh_evidence": "conviction",
    "prosecution_misconduct": "conviction",
    "constitutional_violation": "conviction",
    "sentence": "sentence",
    "sentencing_error": "sentence",
    "procedure": "procedure",
    "procedural_error": "procedure",
    "jury_irregularity": "procedure",
    "evidence": "evidence",
    "evidentiary_error": "evidence",
    "ineffective_counsel": "ineffective_counsel",
    "other": "conviction",  # safest default
}

# Keyword enforcement rules — fired BEFORE label mapping and cannot be
# overridden.  These implement the mandatory legal rules:
#   * s 23A / substantial impairment  -> conviction  (partial defence, not mitigation)
#   * "manifestly excessive" / "House v The King" -> sentence
#   * post-verdict juror conduct -> procedure (NOT conviction)
_CONVICTION_KEYWORDS = frozenset({
    "unsafe verdict", "mens rea", "substantial impairment",
    "mental illness defence", "beyond reasonable doubt",
    "s 23a", "section 23a", "abnormality of mind",
    "diminished responsibility", "mental impairment defence",
    "unsoundness of mind", "partial defence",
})
_SENTENCE_KEYWORDS = frozenset({
    "manifestly excessive", "manifest excess", "rehabilitation",
    "s 21a", "section 21a", "s 3a", "section 3a",
    "house v the king", "house v king",
    "non-parole", "totality", "moral culpability",
})
_PROCEDURE_KEYWORDS = frozenset({
    "judge-alone", "judge alone", "jury misconduct",
    "juror bias", "jury integrity", "pretrial publicity",
    "pre-trial publicity", "mode of trial",
})
_EVIDENCE_KEYWORDS = frozenset({
    "admissibility", "inadmissible", "wrongly admitted",
    "wrongly excluded", "wrongful admission", "wrongful exclusion",
    "prejudicial evidence", "probative value",
})
_INEFFECTIVE_COUNSEL_KEYWORDS = frozenset({
    "ineffective counsel", "ineffective assistance",
    "failed to call", "failed to object", "failure of counsel",
    "incompetent representation",
})


def _remap_to_canonical_bucket(raw_type: str, title: str = "", description: str = "") -> str:
    """Step 3 of the 7-step pipeline: map any ground type label to one of the
    five canonical buckets.

    Priority:
      1. Hard keyword rules — partial-defence terms force 'conviction';
         sentencing terms force 'sentence'; etc.  Cannot be overridden.
      2. Label-to-bucket mapping for anything not caught by keywords.

    Enforces:
      - s 23A / substantial impairment -> conviction (NOT sentence/mitigation)
      - "manifestly excessive", "House v The King" -> sentence
      - A single ground cannot be both conviction and sentence; split
        grounds are handled downstream by ground_normaliser.split_mixed_ground.
    """
    combined = f"{(title or '').lower()} {(description or '').lower()}"

    # Partial-defence / mens rea terms are hard-coded to conviction.
    if any(kw in combined for kw in _CONVICTION_KEYWORDS):
        return "conviction"
    if any(kw in combined for kw in _SENTENCE_KEYWORDS):
        return "sentence"
    if any(kw in combined for kw in _INEFFECTIVE_COUNSEL_KEYWORDS):
        return "ineffective_counsel"
    if any(kw in combined for kw in _EVIDENCE_KEYWORDS):
        return "evidence"
    if any(kw in combined for kw in _PROCEDURE_KEYWORDS):
        return "procedure"

    # No keyword match — use label mapping.
    v = str(raw_type or "other").strip().lower()
    return _LABEL_TO_BUCKET.get(v, "conviction")


def _validate_issue_classification(payload: dict) -> bool:
    if not isinstance(payload, dict):
        return False
    issues = payload.get("issues")
    if not isinstance(issues, list):
        return False
    for issue in issues:
        if not isinstance(issue, dict):
            return False
        if not issue.get("title"):
            return False
    return True


def _norm_ground_type(value: str) -> str:
    v = str(value or "other").strip().lower()
    return v if v in GROUND_TYPES else "other"


# DO NOT UNDO — Appellate pathway mapping per state
APPELLATE_PATHWAYS = {
    "nsw": "s 6(1) Criminal Appeal Act 1912 (NSW)",
    "vic": "s 276 Criminal Procedure Act 2009 (Vic)",
    "qld": "s 668E Criminal Code Act 1899 (Qld)",
    "sa": "s 353 Criminal Law Consolidation Act 1935 (SA)",
    "wa": "s 689 Criminal Code (WA)",
    "tas": "s 401 Criminal Code Act 1924 (Tas)",
    "nt": "s 411 Criminal Code Act 1983 (NT)",
    "act": "s 37 Supreme Court Act 1933 (ACT)",
    "federal": "s 35A Judiciary Act 1903 (Cth) (special leave to High Court); Federal Court of Australia Act 1976 (Cth) (where applicable)",
}


async def classify_case_issues(case: dict, case_extract: dict) -> list[IssueClassification]:
    system_prompt = """You are a specialist Australian appellate lawyer conducting a thorough issue-spot for criminal appeal preparation.
Your task is to identify ALL potential grounds of appeal that are supported by the case material.
Be thorough and exhaustive — identify every distinct legal issue, procedural error, evidential problem,
sentencing concern, and rights violation that could form a ground of appeal.
Do NOT merge different issues together. Each distinct legal argument deserves its own ground.
For example, a sentencing error based on double-counting is DIFFERENT from a sentencing error based
on manifest excess. A failure to call witnesses is DIFFERENT from a failure to object to evidence.

You MUST use Australian English spelling throughout (e.g. analyse, defence, offence, behaviour, honour).

CRITICAL RULES FOR APPELLATE GROUNDING:
- Every ground MUST be tied to a specific appellate pathway (e.g. miscarriage of justice, unsafe verdict, misdirection, procedural unfairness, fresh evidence, sentencing error).
- Do NOT overuse constitutional framing (e.g. s 80 Constitution). In state criminal appeals, the primary pathways are: miscarriage of justice, unsafe verdict, misdirection, procedural unfairness, fresh evidence, and sentencing error under the relevant Criminal Appeal Act.
- Constitutional grounds should only appear when genuinely and specifically engaged.
- Use forensic appellate language: "It is arguable that the trial judge erred in...", "It is contended that...", "There is a tenable argument that...". Do NOT use bare declarations like "The trial judge erred" (too definitive at appellate preparation stage). Do NOT use "may have", "could potentially", "it is possible that" (too weak).
- For law sections: provide ACTUAL section numbers from the CORRECT jurisdiction's legislation. If the exact section number is not known, do NOT include the law section at all. Never write "section not provided" or leave placeholders.
- For similar cases: only cite cases if a real citation is known. Do NOT use "[Surname]" or "[Year]" placeholders. If no verified citation exists, omit the field entirely.

JURISDICTION FIDELITY — ABSOLUTE:
- Use ONLY legislation from the case's jurisdiction. Do NOT default to NSW legislation for non-NSW cases.
- Reference the correct Criminal Code/Act, Sentencing Act, Evidence Act, and Appeal Act for the jurisdiction.
- Commonwealth legislation (Criminal Code Act 1995 (Cth), Crimes Act 1914 (Cth)) may be cited where relevant to any jurisdiction.

STRICT NO-HALLUCINATION:
- Do NOT invent case names, citations, section numbers, Act names, or penalty amounts.
- Do NOT fabricate facts not in the supplied material.
- If uncertain about a section number, reference the Act by name only.

- GROUND FRAMING BY TYPE:
  * If psychiatric/mental health evidence undermines intent → frame as "Miscarriage of Justice: Failure to Properly Determine Mental State (Mens Rea)" — this is a CONVICTION SAFETY attack, not merely evidentiary criticism.
  * If jury/trial procedure issues → cluster related issues (judge-alone refusal, jury reduction, juror conduct) under a single "Procedural Unfairness" ground with sub-particulars.
  * If sentencing error → tie to proportionality and moral culpability ("the sentence does not reflect true culpability"), not just "the judge got it wrong".
  * If ineffective counsel → mark clearly as "Contingent — requires evidentiary support (affidavit, transcript confirmation)" since this ground has an extremely high threshold."""

    facts_text = "\n".join([
        f"[{f.get('fact_id', '')}] ({f.get('type', 'general')}) {f.get('text', '')}"
        for f in case_extract.get("merged_facts", [])
    ])
    events_text = "\n".join([
        f"[{e.get('extracted_event_id', e.get('event_id', ''))}] {e.get('title', '')} ({e.get('event_date', 'unknown')})"
        for e in case_extract.get("merged_events", [])
    ])
    findings_text = "\n".join([
        f"[{f.get('finding_id', '')}] ({f.get('type', 'general')}) {f.get('text', '')}"
        for f in case_extract.get("merged_findings", [])
    ])

    state = str(case.get("state") or "").strip()
    offence_cat = case.get("offence_category") or "unknown"
    state_key = state.lower() if state else ''
    appellate_act = APPELLATE_PATHWAYS.get(state_key, "the relevant Criminal Appeal Act for the jurisdiction")
    jurisdiction_note = f"Jurisdiction: {state.upper()}" if state else "Jurisdiction: NOT CONFIRMED — flag this in every ground"

    # Build legislative framework context for grounds classification
    legislation_context = ""
    if state_key:
        recent_leg = _build_recent_legislation_context(state_key, offence_cat)
        state_fw = _build_state_framework_context(state_key)
        federal_fw = _build_federal_framework_context()
        legislation_context = f"{recent_leg}\n{state_fw}\n{federal_fw}"

    user_prompt = f"""Based on the extracted record below, identify ALL potential grounds of appeal.
Be thorough — examine every aspect of the case for possible appealable issues.

{jurisdiction_note}
Offence category: {offence_cat}
Offence type: {case.get('offence_type') or 'Not specified'}
Primary appellate legislation: {appellate_act}
{legislation_context}
EXTRACTED FACTS:
{facts_text[:15000]}

EXTRACTED EVENTS:
{events_text[:5000]}

EXTRACTED FINDINGS:
{findings_text[:10000]}

Return ONLY valid JSON:
{{
  "issues": [
    {{
      "title": "<concise issue title — framed as an appellate ground, e.g. 'Failure to Properly Evaluate Psychiatric Evidence'>",
      "ground_type": "<procedural_error|fresh_evidence|miscarriage_of_justice|sentencing_error|judicial_error|ineffective_counsel|prosecution_misconduct|jury_irregularity|constitutional_violation|other>",
      "description": "<2-3 sentence description asserting the error and its significance>",
      "appellate_pathway": "<the specific legal mechanism, e.g. 'Miscarriage of justice under {appellate_act}'>",
      "error_identified": "<what specifically went wrong at trial or sentencing>",
      "materiality": "<why this error matters to the outcome>",
      "law_sections": [
        {{
          "act": "<SUBSTANTIVE Act name — the Crimes Act, Evidence Act, Sentencing Act, etc. that was breached or engaged — NOT the Criminal Appeal Act>",
          "section": "<actual section number e.g. 18, 23A, 137, 21A>",
          "jurisdiction": "<state abbreviation>",
          "title": "<what this section covers, e.g. 'definition of murder', 'exclusion of prejudicial evidence', 'aggravating/mitigating factors'>",
          "verification_status": "unverified"
        }}
      ],
      "linked_fact_ids": ["fact_xxx"],
      "linked_event_ids": ["xevt_xxx"],
      "linked_finding_ids": ["find_xxx"],
      "classification_confidence": "<strong|moderate|weak>"
    }}
  ]
}}

STRICT RULES:
- **NEVER MERGE CONVICTION GROUNDS WITH SENTENCING GROUNDS UNDER ANY CIRCUMSTANCE.** Conviction grounds attack the verdict (miscarriage of justice, unsafe verdict). Sentencing grounds attack the penalty (House v The King error, manifest excess). Mixing them will be attacked on appeal as "impermissibly conflating distinct appellate pathways". If a candidate ground spans both, output TWO separate grounds.
- **s 23A Crimes Act 1900 (NSW), substantial impairment, diminished responsibility (QLD), mental impairment defence (VIC/SA/ACT), unsoundness of mind (WA), insanity (TAS), mental impairment / criminal responsibility (NT), mental impairment (ACT), mental impairment under s 7.3 Criminal Code (Cth) — these are PARTIAL DEFENCES operating on LIABILITY (reducing murder to manslaughter, or negating fault elements). They are NEVER sentencing mitigation. Classify them as conviction grounds, never as sentence grounds.**
- **For mens rea / unsafe verdict grounds, EXPLICITLY articulate the M v The Queen formulation** — frame the core legal question as: "Could the jury, acting reasonably, have excluded a reasonable hypothesis consistent with lack of intent given the competing psychiatric evidence?" This is the appellate threshold; omitting it makes the ground defective.
- **Post-verdict juror conduct** (e.g. waving at victim's family AFTER the verdict) has MINIMAL probative value on deliberative bias. Do NOT inflate such grounds to "arguable — moderate" unless there is contemporaneous trial-record material AND a juror affidavit.
- ALWAYS preserve the case jurisdiction ({state.upper() if state else 'UNSPECIFIED'}). NEVER default to NSW — use the correct Acts and pathway provisions for the actual case jurisdiction.
- Identify as many distinct grounds as the evidence supports. Aim for 8-15 grounds if the case material warrants it.
- However, CLUSTER related factual issues under a single ground with sub-particulars where they share the same underlying legal matrix (e.g. jury-related issues under "Procedural Unfairness (Jury Integrity)"). The Court of Criminal Appeal prefers "one ground, multiple particulars" — this makes the appeal cleaner, stronger, and more persuasive.
- Each ground MUST include an appellate_pathway field identifying the specific statutory provision engaged.
- law_sections: identify the SUBSTANTIVE legislation the ground relates to — the Crimes Act/Criminal Code, Evidence Act, Sentencing Act, Criminal Procedure Act, Mental Health Act, etc. for THIS case's jurisdiction ({state.upper() if state else 'UNSPECIFIED'}). Do NOT put the Criminal Appeal Act or appellate pathway act here (that is already recorded in appellate_pathway). Do NOT default to NSW Acts for non-NSW cases. Use the correct Acts for the case jurisdiction. For example:
  * Sentencing error → the jurisdiction's Sentencing Act (e.g. Sentencing Act 1991 (Vic), Penalties and Sentences Act 1992 (Qld), NOT Crimes (Sentencing Procedure) Act 1999 (NSW) unless the case IS from NSW)
  * Conviction safety → the jurisdiction's Criminal Code/Act (e.g. Crimes Act 1958 (Vic), Criminal Code Act 1899 (Qld), Criminal Law Consolidation Act 1935 (SA))
  * Evidence admissibility → the jurisdiction's Evidence Act (e.g. Evidence Act 2008 (Vic), Evidence Act 1977 (Qld))
  * If the exact section is not known, OMIT that law_section entry entirely. An empty array is acceptable.
  * Do NOT invent section numbers. If uncertain, reference the Act by name only.
- Use forensic appellate language: "It is arguable that the trial judge erred in failing to...", "It is contended that...", NOT bare declarations like "The trial judge erred" and NOT hedging like "may have" or "could potentially".
- Where psychiatric/mental health evidence undermines intent (mens rea), frame as a CONVICTION SAFETY ground attacking the determination of mental state, not merely an evidentiary criticism.
- Where multiple jury-related issues exist (judge-alone refusal, jury reduction, juror bias/conduct), cluster under a single procedural unfairness ground with sub-particulars labelled (a), (b), (c).
- Where ineffective counsel is identified, include a note: "Contingent — requires evidentiary support before advancement (affidavit from accused, evidence of advice, transcript confirmation)."
- Where sentencing error is identified, frame around proportionality and moral culpability: "the sentence does not reflect true culpability" rather than merely "the judge got it wrong."
- Link each issue to specific extracted fact/event/finding IDs.
- ground_type MUST be from the listed values.
- AUSTRALIAN ENGLISH ONLY — use "analyse", "organise", "defence", "offence", "behaviour", "colour", "favour", "honour", "centre", "specialise", "recognise", "authorise", "emphasise", "summarise", "counselling". Do NOT use any American spellings.
- supporting_evidence MUST be plain text strings, NOT objects or dictionaries.
- similar_cases: ONLY cite cases with REAL Australian citations (e.g. "R v Smith [2015] NSWCCA 123"). Do NOT use placeholders. If no verified case is known, omit similar_cases entirely.
- classification_confidence should reflect genuine assessment:
  * "strong" = clear factual/legal basis in the record, likely arguable
  * "moderate" = some supporting evidence, warrants further investigation
  * "weak" = only a marginal indicator, limited evidence in the record
- Only classify issues genuinely supported by the extracted record.
- Do NOT overuse constitutional grounds (s 80). Focus on statutory appellate pathways."""

    parsed = await call_llm_for_json(
        system_prompt,
        user_prompt,
        session_id=f"classify_{case['case_id']}",
        task_type="issue_classification",
        validation_fn=_validate_issue_classification,
    )

    issues = []
    for raw in parsed.get("issues", [])[:15]:
        # Clean law_sections — strip placeholder and appellate-act-only entries
        raw_law_sections = raw.get("law_sections", [])
        clean_law_sections = []
        for ls in raw_law_sections:
            if not isinstance(ls, dict):
                continue
            act = (ls.get("act") or "").strip()
            section = (ls.get("section") or "").strip()
            if not act or not section:
                continue
            section_lower = section.lower()
            act_lower = act.lower()
            skip_phrases = [
                "not provided", "unknown", "n/a", "section not", "relevant section",
                "section specific", "identically associated", "applicable section",
                "associated section", "corresponding section", "appropriate section",
            ]
            if any(phrase in section_lower for phrase in skip_phrases):
                continue
            if any(phrase in act_lower for phrase in ["act name", "relevant act", "applicable act"]):
                continue
            # Skip if it's just the appellate pathway act, not substantive law
            if "Criminal Appeal Act" in act and "6(1)" in section:
                continue
            clean_law_sections.append(ls)

        issues.append(IssueClassification(
            case_id=case["case_id"],
            user_id=case["user_id"],
            title=raw.get("title", "Untitled issue"),
            # DO NOT UNDO — Step 3 of 7-step pipeline: remap to canonical bucket.
            # _remap_to_canonical_bucket enforces keyword rules BEFORE label mapping:
            #   s 23A / substantial impairment -> conviction (NOT mitigation/sentence)
            #   manifestly excessive / House v The King -> sentence
            # A single ground cannot be both conviction and sentence; split_mixed_ground
            # handles downstream splitting (step 4).
            ground_type=_remap_to_canonical_bucket(
                raw.get("ground_type", ""),
                title=raw.get("title", ""),
                description=raw.get("description", ""),
            ),
            description=raw.get("description", ""),
            linked_fact_ids=raw.get("linked_fact_ids", []),
            linked_event_ids=raw.get("linked_event_ids", []),
            linked_finding_ids=raw.get("linked_finding_ids", []),
            classification_confidence=raw.get("classification_confidence", "moderate"),
            jurisdiction=state.upper(),
            appellate_pathway=raw.get("appellate_pathway", ""),
            error_identified=raw.get("error_identified", ""),
            materiality=raw.get("materiality", ""),
            law_sections=clean_law_sections,
        ))

    # DO NOT UNDO — Post-classification: merge overlapping grounds into sub-issues
    issues = _merge_overlapping_grounds(issues)

    return issues


def _merge_overlapping_grounds(issues: list) -> list:
    """Merge grounds that address the same underlying legal matrix into a single ground with sub-particulars.
    
    DO NOT UNDO — Barrister-approved: The Court of Criminal Appeal prefers
    "one ground, multiple particulars". This makes the appeal cleaner, stronger,
    and more persuasive. E.g. judge-alone refusal + jury reduction + juror conduct
    all become sub-particulars under "Procedural Unfairness (Jury Integrity)".
    """
    if len(issues) <= 3:
        return issues

    # Theme clusters — grounds that should be merged under a single legal matrix
    THEME_KEYWORDS = {
        "psychiatric_mens_rea": {
            "keywords": ["psychiatric", "psychosis", "mental health", "mental illness", "mental state",
                         "mental impairment", "psychological", "mens rea", "intent", "state of mind",
                         "cognitive capacity", "volition", "intoxication", "drug-induced", "chronic"],
            "parent_title": "Miscarriage of Justice: Failure to Properly Determine Mental State (Mens Rea)",
            "parent_type": "miscarriage_of_justice",
        },
        "jury_integrity": {
            "keywords": ["jury", "juror", "judge-alone", "judge alone", "jury selection",
                         "jury reduction", "juror bias", "juror conduct", "jury irregularity",
                         "jury direction", "misdirection"],
            "parent_title": "Procedural Unfairness (Jury Integrity)",
            "parent_type": "jury_irregularity",
        },
        "sentencing": {
            "keywords": ["sentencing", "manifest excess", "manifestly excessive", "sentence",
                         "non-parole", "proportionality", "moral culpability", "parity"],
            "parent_title": "Sentencing Error: Disproportionate to True Culpability",
            "parent_type": "sentencing_error",
        },
    }

    from collections import defaultdict
    clusters = defaultdict(list)
    unclustered = []

    # Pre-compute cluster membership counts per theme to avoid nested comprehensions
    theme_member_counts = {}
    for theme, config in THEME_KEYWORDS.items():
        count = sum(
            1 for i in issues
            if any(kw in f"{(i.title or '').lower()} {(i.description or '').lower()}" for kw in config["keywords"])
        )
        theme_member_counts[theme] = count

    for issue in issues:
        combined = f"{(issue.title or '').lower()} {(issue.description or '').lower()}"

        matched_theme = None
        for theme, config in THEME_KEYWORDS.items():
            if any(kw in combined for kw in config["keywords"]):
                matched_theme = theme
                break

        if matched_theme and theme_member_counts[matched_theme] > 1:
            clusters[matched_theme].append(issue)
        else:
            unclustered.append(issue)

    # Confidence rank for parent selection: prefer strongest classification_confidence
    CONFIDENCE_RANK = {"strong": 3, "moderate": 2, "weak": 1}

    merged = list(unclustered)
    for theme, cluster_issues in clusters.items():
        if len(cluster_issues) <= 1:
            merged.extend(cluster_issues)
            continue

        config = THEME_KEYWORDS[theme]

        # Select parent by classification_confidence first, then description length as tiebreaker
        parent_source = max(
            cluster_issues,
            key=lambda i: (CONFIDENCE_RANK.get(i.classification_confidence, 0), len(i.description or ""))
        )

        sub_issues = [f"({chr(97 + idx)}) {ci.title}" for idx, ci in enumerate(cluster_issues)]
        sub_desc = "\n".join(sub_issues)

        # Merge linked IDs from all sub-issues
        all_fact_ids = set()
        all_event_ids = set()
        all_finding_ids = set()
        for ci in cluster_issues:
            all_fact_ids.update(ci.linked_fact_ids or [])
            all_event_ids.update(ci.linked_event_ids or [])
            all_finding_ids.update(ci.linked_finding_ids or [])

        # Concatenate error_identified and materiality from ALL children
        all_errors = [ci.error_identified for ci in cluster_issues if ci.error_identified]
        all_materiality = [ci.materiality for ci in cluster_issues if ci.materiality]
        merged_error = "\n\n".join(dict.fromkeys(all_errors))  # deduplicate, preserve order
        merged_materiality = "\n\n".join(dict.fromkeys(all_materiality))

        # Create merged parent via model_copy — avoids mutating the original Pydantic instance
        parent = parent_source.model_copy(update={
            "title": config["parent_title"],
            "ground_type": config["parent_type"],
            "description": f"{parent_source.description}\n\nSub-particulars:\n{sub_desc}",
            "appellate_pathway": parent_source.appellate_pathway or (cluster_issues[0].appellate_pathway if cluster_issues else ""),
            "error_identified": merged_error or parent_source.error_identified,
            "materiality": merged_materiality or parent_source.materiality,
            "linked_fact_ids": list(all_fact_ids),
            "linked_event_ids": list(all_event_ids),
            "linked_finding_ids": list(all_finding_ids),
        })

        merged.append(parent)

    return merged
