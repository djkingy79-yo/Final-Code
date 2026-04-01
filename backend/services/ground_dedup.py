# DO_NOT_UNDO — Legal ground deduplication utility.
# Prevents grounds from multiplying by using topic-based classification + fuzzy matching.
# Previous approaches (word overlap only, fuzzywuzzy only) let grounds multiply from 6 to 41.

from fuzzywuzzy import fuzz

# DO_NOT_UNDO — Legal topic keywords. If two titles share ANY topic, they are duplicates.
# Keywords must cover all common word variants (e.g. "juror"/"jury", "manifest"/"manifestly").
LEGAL_TOPICS = {
    "judge_alone_trial": {"judge-alone", "judge alone", "trial application", "judge trial"},
    "psychiatric_evidence": {"psychiatric", "psychological", "mental health", "mental impairment", "psychosis", "mental illness", "psychiatric report", "psychiatric opinion", "mitigation due to mental", "chronic psycho"},
    "media_coverage": {"media coverage", "prejudicial media", "media bias", "juror bias from media", "pretrial publicity"},
    "jury_misconduct": {"juror misconduct", "jury misconduct", "jury irregularity", "juror bias", "jury bias", "jury impartial", "juror impartial", "juror prejudic", "jury prejudic", "juror behavio", "jury behavio"},
    "sentencing_error": {"sentencing error", "sentencing disparity", "non-parole", "manifestly excessive", "manifest excessive", "sentencing above", "excessive sentence", "sentencing: manifest", "potential sentencing"},
    "ineffective_counsel": {"ineffective counsel", "counsel regarding", "representation", "legal representation"},
    "mental_defences": {"mental health defence", "mental impairment defence", "diminished responsibility", "mental health defences"},
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


def is_ground_duplicate(new_title: str, existing_title: str, threshold: int = 55) -> bool:
    """Check if two ground/issue titles are about the same legal topic.
    
    Uses three methods:
    1. Legal topic classification (most reliable — catches semantic duplicates)
    2. fuzzywuzzy token_set_ratio (catches word-reordered variants)
    3. Bidirectional word overlap (catches partial matches)
    
    Returns True if ANY method identifies a duplicate.
    """
    if not new_title or not existing_title:
        return False
    
    new_title = new_title.strip()
    existing_title = existing_title.strip()
    
    # Method 1: Topic-based matching (most reliable)
    new_topics = _extract_topics(new_title)
    existing_topics = _extract_topics(existing_title)
    if new_topics and existing_topics and new_topics & existing_topics:
        return True
    
    # Method 2: fuzzywuzzy token_set_ratio
    score = fuzz.token_set_ratio(new_title.lower(), existing_title.lower())
    if score >= threshold:
        return True
    
    # Method 3: Bidirectional word overlap
    new_words = set(w.lower() for w in new_title.split() if len(w) > 3)
    existing_words = set(w.lower() for w in existing_title.split() if len(w) > 3)
    if new_words and existing_words:
        overlap = new_words & existing_words
        if overlap:
            ratio = max(
                len(overlap) / max(len(new_words), 1),
                len(overlap) / max(len(existing_words), 1)
            )
            if ratio > 0.45:
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
import re
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
