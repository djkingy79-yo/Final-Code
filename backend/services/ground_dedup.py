# DO_NOT_UNDO — Legal ground deduplication utility.
# Prevents grounds from multiplying by using topic-based classification + fuzzy matching.
# Previous approaches (word overlap only, fuzzywuzzy only) let grounds multiply from 6 to 41.
# LEGAL_TOPICS expanded massively on 2 Apr 2026 to cover ALL real-world title variants.
# DO NOT UNDO — Keywords for "manifest excess", "inadequate defence", "failure to file" etc. added 2 Apr 2026.
# DO NOT UNDO — "failure to file/lodge/appeal" is in ineffective_counsel, NOT procedural_error (prevents false merge with judge-alone trial)

from fuzzywuzzy import fuzz
import re
import logging

logger = logging.getLogger(__name__)

# DO_NOT_UNDO — Legal topic keywords. If two titles share ANY topic, they are duplicates.
# Keywords must cover ALL common word variants. Each keyword is checked as a substring (case-insensitive).
# NEVER remove keywords. Only add new ones. Missing variants cause grounds to multiply.
LEGAL_TOPICS = {
    "judge_alone_trial": {
        "judge-alone", "judge alone", "trial application", "judge trial",
    },
    "psychiatric_evidence": {
        "psychiatric", "psychological", "mental health", "mental impairment",
        "psychosis", "mental illness", "psychiatric report", "psychiatric opinion",
        "mitigation due to mental", "chronic psycho", "mitigation", "mitigating",
        "diminished responsibility", "mental capacity", "cognitive impairment",
        "mental state", "psychiatric assessment", "psychological report",
        "mental condition", "psychiatric evidence", "psychological evidence",
        "mental defence", "mental defences", "mental disorder",
    },
    "media_coverage": {
        "media coverage", "prejudicial media", "media bias",
        "juror bias from media", "pretrial publicity", "media influence",
        "media on jury", "jury media", "media prejudic", "media impact",
        "publicity bias", "pre-trial publicity", "pre-trial media",
        "media saturation", "press coverage", "public attention",
    },
    "jury_misconduct": {
        "juror misconduct", "jury misconduct", "jury irregularity",
        "juror bias", "jury bias", "jury impartial", "juror impartial",
        "juror prejudic", "jury prejudic", "juror behavio", "jury behavio",
        "jury contamination", "juror contact", "jury deliberation",
        "jury non-sequestration", "non-sequestration", "jury sequester",
        "jury irregulari",
    },
    "sentencing_error": {
        "sentencing error", "sentencing disparity", "non-parole",
        "manifestly excessive", "manifest excessive", "manifest excess",
        "sentencing above",
        "excessive sentence", "sentencing: manifest", "potential sentencing",
        "sentencing excess", "sentence manifest", "sentence excessive",
        "sentencing inadequa", "manifestly inadequate", "manifest inadequa",
        "sentence disproportion", "disproportionate sentence",
        "sentencing discretion", "sentencing principles",
        "penalty excessive", "penalty manifest", "sentence severity",
        "parity in sentencing", "sentencing parity",
        "double-counting", "double counting", "overstatement of aggravat",
        "aggravating features", "sentencing approach", "moral culpability",
        "sentencing: possible", "possible error in", "error in approach to",
        "sentence: ", "adequacy of reasons",
        "excess in sentencing", "excessive in sentencing",
    },
    "ineffective_counsel": {
        "ineffective counsel", "ineffective assistance", "counsel regarding",
        "representation", "legal representation", "incompetent counsel",
        "incompetence", "failure to call", "failure to adduce",
        "failure to object", "failure to cross-examine", "failure to advise",
        "inadequate representation", "inadequate legal",
        "counsel failure", "counsel error", "counsel competence",
        "counsel incompeten", "defence counsel", "defense counsel",
        "trial counsel", "appellate counsel",
        "inadequate defence", "inadequate defense",
        "defence advocacy", "defense advocacy",
        "inadequate advocacy", "inadequate counsel",
        "failure to file", "failure to lodge", "failure to appeal",
    },
    "evidence_admissibility": {
        "admissibility", "inadmissible", "improperly admitted",
        "wrongful admission", "exclusion of evidence", "evidence exclusion",
        "evidence admiss", "hearsay", "prejudicial evidence",
        "unfairly obtained", "improper admission", "admission of evidence",
        "wrongful exclusion", "evidence improperly", "evidence wrongful",
        "chain of custody", "continuity of evidence", "illegally obtained",
        "evidence reliability", "unreliable evidence", "tainted evidence",
        "evidence integrity", "evidence handling", "evidence contamina",
        "dna evidence", "forensic evidence", "expert evidence",
    },
    "fresh_evidence": {
        "fresh evidence", "new evidence", "additional evidence",
        "newly discovered", "post-trial evidence", "uncalled witness",
        "new witness", "new forensic", "post-conviction evidence",
        "after-discovered", "previously unavailable",
    },
    "prosecutorial_misconduct": {
        "prosecutorial misconduct", "prosecution misconduct",
        "crown misconduct", "prosecution error", "prosecutorial error",
        "prosecution improper", "crown conduct", "prosecutor conduct",
        "prosecution failure", "crown failure", "dpp misconduct",
        "dpp error", "prosecution duty",
    },
    "judicial_direction": {
        "judicial direction", "judge direction", "misdirection",
        "jury direction", "direction to jury", "judicial error",
        "judge error", "summing up", "jury instruction",
        "inadequate direction", "erroneous direction", "wrong direction",
        "failure to direct", "inadequate jury", "jury charge",
        "judicial misconduct", "judicial conduct", "judge conduct",
        "prejudicial comments", "judge bias", "judicial bias",
        "trial judge", "judge remark", "judicial remark",
        "unfair trial", "trial fairness", "fair trial",
    },
    "unreasonable_verdict": {
        "unreasonable verdict", "unsafe verdict", "unsatisfactory verdict",
        "verdict cannot be supported", "verdict unsupported",
        "verdict against weight", "verdict against evidence",
        "weight of evidence", "unsafe and unsatisfactory",
        "unreasonable: ", "verdict unreasonable",
        "verdict not supported", "insufficient evidence for verdict",
        "perverse verdict", "inconsistent verdict",
        "identification evidence", "identification: ",
        "unreliable identification", "witness inconsisten",
        "eyewitness", "timeline conflict",
    },
    "procedural_error": {
        "procedural error", "procedural irregularity", "procedural unfairness",
        "procedural fairness", "procedural breach", "procedural defect",
        "due process", "natural justice", "process error",
        "trial procedure", "trial process", "procedural failure",
        "refusal of", "trial application refused",
        "failure to comply", "late filing", "time limitation",
    },
}


def _extract_topics(title: str) -> set:
    """Extract legal topic tags from a ground/issue title."""
    t = title.lower()
    topics = set()
    for topic, keywords in LEGAL_TOPICS.items():
        for kw in keywords:
            if kw in t:
                topics.add(topic)
                break
    return topics


def is_ground_duplicate(new_title: str, existing_title: str, threshold: int = 85) -> bool:
    """Check if two ground/issue titles are near-identical duplicates.
    
    DO_NOT_UNDO — Uses TWO methods only (topic matching removed to prevent over-merging):
    1. fuzzywuzzy token_set_ratio (threshold=85 — only catches near-identical titles)
    2. Bidirectional word overlap >60% (catches rephrased but essentially identical titles)
    
    This is deliberately permissive to keep all distinct legal arguments separate.
    Two grounds about the same broad topic (e.g. two different sentencing errors)
    are NOT duplicates if they argue different legal points.
    
    Returns True only if the titles are essentially the same argument rephrased.
    """
    if not new_title or not existing_title:
        return False
    
    new_title = new_title.strip()
    existing_title = existing_title.strip()
    
    # Method 1: fuzzywuzzy token_set_ratio — very high bar (85) to only catch near-identical
    score = fuzz.token_set_ratio(new_title.lower(), existing_title.lower())
    if score >= threshold:
        return True
    
    # Method 2: Bidirectional word overlap — only merge if >60% overlap
    new_words = set(w.lower() for w in new_title.split() if len(w) > 3)
    existing_words = set(w.lower() for w in existing_title.split() if len(w) > 3)
    if new_words and existing_words:
        overlap = new_words & existing_words
        if overlap:
            ratio = max(
                len(overlap) / max(len(new_words), 1),
                len(overlap) / max(len(existing_words), 1)
            )
            if ratio > 0.60:
                return True
    
    return False


def find_matching_ground(new_title: str, existing_grounds: list) -> dict | None:
    """Find an existing ground that matches the new title. Returns the match or None."""
    for eg in existing_grounds:
        eg_title = (eg.get("title") or "").strip()
        if is_ground_duplicate(new_title, eg_title):
            return eg
    return None


# DO_NOT_UNDO — Australian spelling normaliser for ground titles.
# Applied when grounds are created/synced so titles always use Australian English.
_AU_REPLACEMENTS = [
    (re.compile(r'\bcharacterization\b', re.I), lambda m: 'Characterisation' if m.group()[0].isupper() else 'characterisation'),
    (re.compile(r'\bmischaracterization\b', re.I), lambda m: 'Mischaracterisation' if m.group()[0].isupper() else 'mischaracterisation'),
    (re.compile(r'\bbehavior\b', re.I), lambda m: 'Behaviour' if m.group()[0].isupper() else 'behaviour'),
    (re.compile(r'\borganization\b', re.I), lambda m: 'Organisation' if m.group()[0].isupper() else 'organisation'),
    (re.compile(r'\brecognize\b', re.I), lambda m: 'Recognise' if m.group()[0].isupper() else 'recognise'),
    (re.compile(r'\brecognized\b', re.I), lambda m: 'Recognised' if m.group()[0].isupper() else 'recognised'),
    (re.compile(r'\banalyze\b', re.I), lambda m: 'Analyse' if m.group()[0].isupper() else 'analyse'),
    (re.compile(r'\banalyzing\b', re.I), lambda m: 'Analysing' if m.group()[0].isupper() else 'analysing'),
    (re.compile(r'\bdefense\b', re.I), lambda m: 'Defence' if m.group()[0].isupper() else 'defence'),
    (re.compile(r'\boffense\b', re.I), lambda m: 'Offence' if m.group()[0].isupper() else 'offence'),
    (re.compile(r'\bfavoring\b', re.I), lambda m: 'Favouring' if m.group()[0].isupper() else 'favouring'),
    (re.compile(r'\butilize\b', re.I), lambda m: 'Utilise' if m.group()[0].isupper() else 'utilise'),
    (re.compile(r'\butilized\b', re.I), lambda m: 'Utilised' if m.group()[0].isupper() else 'utilised'),
]

def normalise_au_spelling(text: str) -> str:
    """Convert American English to Australian English in ground titles."""
    if not text:
        return text
    for pattern, replacement in _AU_REPLACEMENTS:
        text = pattern.sub(replacement, text)
    return text


async def cleanup_duplicate_grounds(db, case_id: str, user_id: str) -> dict:
    """DO_NOT_UNDO — Scan and merge duplicate grounds for a case.
    
    Keeps the FIRST ground (by created_at) and deletes later duplicates.
    Uses the same is_ground_duplicate() logic as all sync paths.
    Returns stats about what was cleaned up.
    """
    all_grounds = await db.grounds_of_merit.find(
        {"case_id": case_id, "user_id": user_id},
        {"_id": 0}
    ).sort("created_at", 1).to_list(500)

    if len(all_grounds) <= 1:
        return {"before": len(all_grounds), "after": len(all_grounds), "removed": 0}

    # Build unique list — keep first occurrence, mark later duplicates for deletion
    unique_grounds = []
    duplicate_ids = []

    for ground in all_grounds:
        title = (ground.get("title") or "").strip()
        is_dup = False
        for ug in unique_grounds:
            ug_title = (ug.get("title") or "").strip()
            if is_ground_duplicate(title, ug_title):
                is_dup = True
                # If the duplicate has richer data (investigated, has evidence), merge it into the keeper
                if ground.get("status") == "investigated" and ug.get("status") != "investigated":
                    # Promote the duplicate's data into the keeper
                    merge_fields = {}
                    if ground.get("supporting_evidence") and not ug.get("supporting_evidence"):
                        merge_fields["supporting_evidence"] = ground["supporting_evidence"]
                    if ground.get("deep_analysis") and not ug.get("deep_analysis"):
                        merge_fields["deep_analysis"] = ground["deep_analysis"]
                    if ground.get("law_sections") and not ug.get("law_sections"):
                        merge_fields["law_sections"] = ground["law_sections"]
                    if ground.get("similar_cases") and not ug.get("similar_cases"):
                        merge_fields["similar_cases"] = ground["similar_cases"]
                    if ground.get("legitimacy_scores") and not ug.get("legitimacy_scores"):
                        merge_fields["legitimacy_scores"] = ground["legitimacy_scores"]
                        merge_fields["strength"] = ground.get("strength", ug.get("strength"))
                    if merge_fields:
                        merge_fields["status"] = "investigated"
                        await db.grounds_of_merit.update_one(
                            {"ground_id": ug["ground_id"]},
                            {"$set": merge_fields}
                        )
                        ug.update(merge_fields)
                break

        if is_dup:
            duplicate_ids.append(ground["ground_id"])
            logger.info(f"Dedup cleanup: removing duplicate ground '{title[:60]}' (id={ground['ground_id']})")
        else:
            unique_grounds.append(ground)

    # Delete duplicates
    if duplicate_ids:
        result = await db.grounds_of_merit.delete_many({"ground_id": {"$in": duplicate_ids}})
        logger.info(f"Dedup cleanup for case {case_id}: removed {result.deleted_count} duplicate grounds ({len(all_grounds)} → {len(unique_grounds)})")

    return {
        "before": len(all_grounds),
        "after": len(unique_grounds),
        "removed": len(duplicate_ids),
        "removed_ids": duplicate_ids,
    }


async def cleanup_duplicate_issues(db, case_id: str, user_id: str) -> dict:
    """DO_NOT_UNDO — Scan and merge duplicate issue_classifications for a case."""
    all_issues = await db.issue_classifications.find(
        {"case_id": case_id, "user_id": user_id},
        {"_id": 0}
    ).sort("created_at", 1).to_list(500)

    if len(all_issues) <= 1:
        return {"before": len(all_issues), "after": len(all_issues), "removed": 0}

    unique_issues = []
    duplicate_ids = []

    for issue in all_issues:
        title = (issue.get("title") or "").strip()
        is_dup = False
        for ui in unique_issues:
            ui_title = (ui.get("title") or "").strip()
            if is_ground_duplicate(title, ui_title):
                is_dup = True
                break
        if is_dup:
            duplicate_ids.append(issue["issue_id"])
        else:
            unique_issues.append(issue)

    if duplicate_ids:
        await db.issue_classifications.delete_many({"issue_id": {"$in": duplicate_ids}})
        logger.info(f"Issue dedup cleanup for case {case_id}: removed {len(duplicate_ids)} duplicates ({len(all_issues)} → {len(unique_issues)})")

    return {
        "before": len(all_issues),
        "after": len(unique_issues),
        "removed": len(duplicate_ids),
    }
