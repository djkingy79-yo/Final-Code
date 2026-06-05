#  — Legal ground deduplication utility.
# Prevents grounds from multiplying by using topic-based classification + fuzzy matching.
# Previous approaches (word overlap only, fuzzywuzzy only) let grounds multiply from 6 to 41.
# LEGAL_TOPICS expanded massively on 2 Apr 2026 to cover ALL real-world title variants.
#  — Keywords for "manifest excess", "inadequate defence", "failure to file" etc. added 2 Apr 2026.
#  — "failure to file/lodge/appeal" is in ineffective_counsel, NOT procedural_error (prevents false merge with judge-alone trial)

from fuzzywuzzy import fuzz
import re
import logging

logger = logging.getLogger(__name__)

#  — Legal topic keywords. If two titles share ANY topic, they are duplicates.
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

     — Uses THREE methods (topic matching RE-ENABLED 3 Apr 2026):
    1. fuzzywuzzy token_set_ratio (threshold=85 — catches near-identical titles)
    2. Bidirectional word overlap >60% (catches rephrased identical titles)
    3. Shared legal topic + fuzzy score >= 55 (catches same-argument-different-wording)

    Method 3 was removed previously due to over-merging, but its absence caused grounds
    to multiply from ~8 to 15+ because rephrased titles like "Juror Misconduct" vs
    "Jury Irregularity and Possible Misconduct" were not caught. The fix is to require
    BOTH a shared topic AND a meaningful fuzzy score (55+), so titles from completely
    different arguments stay separate.

    Returns True only if the titles are essentially the same argument rephrased.
    """
    if not new_title or not existing_title:
        return False

    new_title = new_title.strip()
    existing_title = existing_title.strip()

    new_lower = new_title.lower()
    existing_lower = existing_title.lower()

    # Method 1: fuzzywuzzy token_set_ratio — high bar for near-identical
    score = fuzz.token_set_ratio(new_lower, existing_lower)
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

    # Method 3: Shared legal topic + moderate fuzzy score (55+)
    # This catches "Juror Misconduct" vs "Jury Irregularity and Possible Misconduct"
    # which share the jury_misconduct topic but have low word overlap.
    # The fuzzy score floor (55) prevents merging titles that only share a topic
    # by coincidence (e.g. different sentencing arguments).
    if score >= 55:
        new_topics = _extract_topics(new_title)
        existing_topics = _extract_topics(existing_title)
        if new_topics and existing_topics and (new_topics & existing_topics):
            return True

    return False


def find_matching_ground(new_title: str, existing_grounds: list) -> dict | None:
    """Find an existing ground that matches the new title. Returns the match or None."""
    for eg in existing_grounds:
        eg_title = (eg.get("title") or "").strip()
        if is_ground_duplicate(new_title, eg_title):
            return eg
    return None


#  — Australian spelling normaliser for ground titles.
# Applied when grounds are created/synced so titles always use Australian English.
_AU_REPLACEMENTS = [
    (re.compile(r'\bcharacterization\b', re.I), lambda m: 'Characterisation' if m.group()[0].isupper() else 'characterisation'),
    (re.compile(r'\bmischaracterization\b', re.I), lambda m: 'Mischaracterisation' if m.group()[0].isupper() else 'mischaracterisation'),
    (re.compile(r'\bbehavior\b', re.I), lambda m: 'Behaviour' if m.group()[0].isupper() else 'behaviour'),
    (re.compile(r'\borganization\b', re.I), lambda m: 'Organisation' if m.group()[0].isupper() else 'organisation'),
    (re.compile(r'\brecognize\b', re.I), lambda m: 'Recognise' if m.group()[0].isupper() else 'recognise'),
    (re.compile(r'\brecognized\b', re.I), lambda m: 'Recognised' if m.group()[0].isupper() else 'recognised'),
    (re.compile(r'\brecognizing\b', re.I), lambda m: 'Recognising' if m.group()[0].isupper() else 'recognising'),
    (re.compile(r'\banalyze\b', re.I), lambda m: 'Analyse' if m.group()[0].isupper() else 'analyse'),
    (re.compile(r'\banalyzed\b', re.I), lambda m: 'Analysed' if m.group()[0].isupper() else 'analysed'),
    (re.compile(r'\banalyzing\b', re.I), lambda m: 'Analysing' if m.group()[0].isupper() else 'analysing'),
    (re.compile(r'\bdefense\b', re.I), lambda m: 'Defence' if m.group()[0].isupper() else 'defence'),
    (re.compile(r'\boffense\b', re.I), lambda m: 'Offence' if m.group()[0].isupper() else 'offence'),
    (re.compile(r'\bfavoring\b', re.I), lambda m: 'Favouring' if m.group()[0].isupper() else 'favouring'),
    (re.compile(r'\bfavor\b', re.I), lambda m: 'Favour' if m.group()[0].isupper() else 'favour'),
    (re.compile(r'\bfavorable\b', re.I), lambda m: 'Favourable' if m.group()[0].isupper() else 'favourable'),
    (re.compile(r'\bhonor\b', re.I), lambda m: 'Honour' if m.group()[0].isupper() else 'honour'),
    (re.compile(r'\blabor\b', re.I), lambda m: 'Labour' if m.group()[0].isupper() else 'labour'),
    (re.compile(r'\bcenter\b', re.I), lambda m: 'Centre' if m.group()[0].isupper() else 'centre'),
    (re.compile(r'\bcolored\b', re.I), lambda m: 'Coloured' if m.group()[0].isupper() else 'coloured'),
    (re.compile(r'\bcounseling\b', re.I), lambda m: 'Counselling' if m.group()[0].isupper() else 'counselling'),
    (re.compile(r'\bspecialize\b', re.I), lambda m: 'Specialise' if m.group()[0].isupper() else 'specialise'),
    (re.compile(r'\bspecialized\b', re.I), lambda m: 'Specialised' if m.group()[0].isupper() else 'specialised'),
    (re.compile(r'\bauthorize\b', re.I), lambda m: 'Authorise' if m.group()[0].isupper() else 'authorise'),
    (re.compile(r'\bauthorized\b', re.I), lambda m: 'Authorised' if m.group()[0].isupper() else 'authorised'),
    (re.compile(r'\bemphasize\b', re.I), lambda m: 'Emphasise' if m.group()[0].isupper() else 'emphasise'),
    (re.compile(r'\bemphasized\b', re.I), lambda m: 'Emphasised' if m.group()[0].isupper() else 'emphasised'),
    (re.compile(r'\bsummarize\b', re.I), lambda m: 'Summarise' if m.group()[0].isupper() else 'summarise'),
    (re.compile(r'\bsummarized\b', re.I), lambda m: 'Summarised' if m.group()[0].isupper() else 'summarised'),
    (re.compile(r'\butilize\b', re.I), lambda m: 'Utilise' if m.group()[0].isupper() else 'utilise'),
    (re.compile(r'\butilized\b', re.I), lambda m: 'Utilised' if m.group()[0].isupper() else 'utilised'),
    (re.compile(r'\borganize\b', re.I), lambda m: 'Organise' if m.group()[0].isupper() else 'organise'),
    (re.compile(r'\borganized\b', re.I), lambda m: 'Organised' if m.group()[0].isupper() else 'organised'),
    (re.compile(r'\bcriminalize\b', re.I), lambda m: 'Criminalise' if m.group()[0].isupper() else 'criminalise'),
    (re.compile(r'\brealize\b', re.I), lambda m: 'Realise' if m.group()[0].isupper() else 'realise'),
    (re.compile(r'\brealized\b', re.I), lambda m: 'Realised' if m.group()[0].isupper() else 'realised'),
    (re.compile(r'\brealizing\b', re.I), lambda m: 'Realising' if m.group()[0].isupper() else 'realising'),
    (re.compile(r'\bpenalize\b', re.I), lambda m: 'Penalise' if m.group()[0].isupper() else 'penalise'),
    (re.compile(r'\bpenalized\b', re.I), lambda m: 'Penalised' if m.group()[0].isupper() else 'penalised'),
    (re.compile(r'\bpenalizing\b', re.I), lambda m: 'Penalising' if m.group()[0].isupper() else 'penalising'),
    (re.compile(r'\bstandardize\b', re.I), lambda m: 'Standardise' if m.group()[0].isupper() else 'standardise'),
    (re.compile(r'\bstandardized\b', re.I), lambda m: 'Standardised' if m.group()[0].isupper() else 'standardised'),
    (re.compile(r'\blegitimize\b', re.I), lambda m: 'Legitimise' if m.group()[0].isupper() else 'legitimise'),
    (re.compile(r'\blegitimized\b', re.I), lambda m: 'Legitimised' if m.group()[0].isupper() else 'legitimised'),
    (re.compile(r'\bcharacterize\b', re.I), lambda m: 'Characterise' if m.group()[0].isupper() else 'characterise'),
    (re.compile(r'\bcharacterized\b', re.I), lambda m: 'Characterised' if m.group()[0].isupper() else 'characterised'),
    (re.compile(r'\bcharacterizing\b', re.I), lambda m: 'Characterising' if m.group()[0].isupper() else 'characterising'),
    (re.compile(r'\boptimize\b', re.I), lambda m: 'Optimise' if m.group()[0].isupper() else 'optimise'),
    (re.compile(r'\boptimized\b', re.I), lambda m: 'Optimised' if m.group()[0].isupper() else 'optimised'),
    (re.compile(r'\bvisualize\b', re.I), lambda m: 'Visualise' if m.group()[0].isupper() else 'visualise'),
    (re.compile(r'\bvisualized\b', re.I), lambda m: 'Visualised' if m.group()[0].isupper() else 'visualised'),
    (re.compile(r'\bjudgment\b', re.I), lambda m: 'Judgement' if m.group()[0].isupper() else 'judgement'),
    (re.compile(r'\bpracticing\b', re.I), lambda m: 'Practising' if m.group()[0].isupper() else 'practising'),
    (re.compile(r'\bneighbor\b', re.I), lambda m: 'Neighbour' if m.group()[0].isupper() else 'neighbour'),
    (re.compile(r'\bneighboring\b', re.I), lambda m: 'Neighbouring' if m.group()[0].isupper() else 'neighbouring'),
    (re.compile(r'\bminimize\b', re.I), lambda m: 'Minimise' if m.group()[0].isupper() else 'minimise'),
    (re.compile(r'\bminimized\b', re.I), lambda m: 'Minimised' if m.group()[0].isupper() else 'minimised'),
    (re.compile(r'\bmaximize\b', re.I), lambda m: 'Maximise' if m.group()[0].isupper() else 'maximise'),
    (re.compile(r'\bmaximized\b', re.I), lambda m: 'Maximised' if m.group()[0].isupper() else 'maximised'),
    (re.compile(r'\bprioritize\b', re.I), lambda m: 'Prioritise' if m.group()[0].isupper() else 'prioritise'),
    (re.compile(r'\bprioritized\b', re.I), lambda m: 'Prioritised' if m.group()[0].isupper() else 'prioritised'),
    (re.compile(r'\bcategorize\b', re.I), lambda m: 'Categorise' if m.group()[0].isupper() else 'categorise'),
    (re.compile(r'\bcategorized\b', re.I), lambda m: 'Categorised' if m.group()[0].isupper() else 'categorised'),
    (re.compile(r'\bfinaliz', re.I), lambda m: m.group().replace('liz', 'lis').replace('LIZ', 'LIS')),
    (re.compile(r'\bcriticize\b', re.I), lambda m: 'Criticise' if m.group()[0].isupper() else 'criticise'),
    (re.compile(r'\bcriticized\b', re.I), lambda m: 'Criticised' if m.group()[0].isupper() else 'criticised'),
    (re.compile(r'\bjeopardize\b', re.I), lambda m: 'Jeopardise' if m.group()[0].isupper() else 'jeopardise'),
    (re.compile(r'\bjeopardized\b', re.I), lambda m: 'Jeopardised' if m.group()[0].isupper() else 'jeopardised'),
    (re.compile(r'\bapologize\b', re.I), lambda m: 'Apologise' if m.group()[0].isupper() else 'apologise'),
    (re.compile(r'\bapologized\b', re.I), lambda m: 'Apologised' if m.group()[0].isupper() else 'apologised'),
    # Criminal/legal context conversions
    (re.compile(r'\btraumatize\b', re.I), lambda m: 'Traumatise' if m.group()[0].isupper() else 'traumatise'),
    (re.compile(r'\btraumatized\b', re.I), lambda m: 'Traumatised' if m.group()[0].isupper() else 'traumatised'),
    (re.compile(r'\btraumatizing\b', re.I), lambda m: 'Traumatising' if m.group()[0].isupper() else 'traumatising'),
    (re.compile(r'\bvictimize\b', re.I), lambda m: 'Victimise' if m.group()[0].isupper() else 'victimise'),
    (re.compile(r'\bvictimized\b', re.I), lambda m: 'Victimised' if m.group()[0].isupper() else 'victimised'),
    (re.compile(r'\bvictimizing\b', re.I), lambda m: 'Victimising' if m.group()[0].isupper() else 'victimising'),
    (re.compile(r'\bterrorize\b', re.I), lambda m: 'Terrorise' if m.group()[0].isupper() else 'terrorise'),
    (re.compile(r'\bterrorized\b', re.I), lambda m: 'Terrorised' if m.group()[0].isupper() else 'terrorised'),
    (re.compile(r'\bscrutinize\b', re.I), lambda m: 'Scrutinise' if m.group()[0].isupper() else 'scrutinise'),
    (re.compile(r'\bscrutinized\b', re.I), lambda m: 'Scrutinised' if m.group()[0].isupper() else 'scrutinised'),
    (re.compile(r'\bscrutinizing\b', re.I), lambda m: 'Scrutinising' if m.group()[0].isupper() else 'scrutinising'),
    (re.compile(r'\bhypothesiz', re.I), lambda m: m.group().replace('siz', 'sis').replace('SIZ', 'SIS')),
    (re.compile(r'\brationalize\b', re.I), lambda m: 'Rationalise' if m.group()[0].isupper() else 'rationalise'),
    (re.compile(r'\brationalized\b', re.I), lambda m: 'Rationalised' if m.group()[0].isupper() else 'rationalised'),
    (re.compile(r'\bmarginalize\b', re.I), lambda m: 'Marginalise' if m.group()[0].isupper() else 'marginalise'),
    (re.compile(r'\bmarginalized\b', re.I), lambda m: 'Marginalised' if m.group()[0].isupper() else 'marginalised'),
    (re.compile(r'\bmarginalizing\b', re.I), lambda m: 'Marginalising' if m.group()[0].isupper() else 'marginalising'),
    (re.compile(r'\bweaponize\b', re.I), lambda m: 'Weaponise' if m.group()[0].isupper() else 'weaponise'),
    (re.compile(r'\bweaponized\b', re.I), lambda m: 'Weaponised' if m.group()[0].isupper() else 'weaponised'),
    (re.compile(r'\bsympathize\b', re.I), lambda m: 'Sympathise' if m.group()[0].isupper() else 'sympathise'),
    (re.compile(r'\bsympathized\b', re.I), lambda m: 'Sympathised' if m.group()[0].isupper() else 'sympathised'),
    (re.compile(r'\bneutralize\b', re.I), lambda m: 'Neutralise' if m.group()[0].isupper() else 'neutralise'),
    (re.compile(r'\bneutralized\b', re.I), lambda m: 'Neutralised' if m.group()[0].isupper() else 'neutralised'),
    (re.compile(r'\bmobilize\b', re.I), lambda m: 'Mobilise' if m.group()[0].isupper() else 'mobilise'),
    (re.compile(r'\bmobilized\b', re.I), lambda m: 'Mobilised' if m.group()[0].isupper() else 'mobilised'),
    (re.compile(r'\bmemorize\b', re.I), lambda m: 'Memorise' if m.group()[0].isupper() else 'memorise'),
    (re.compile(r'\bmemorized\b', re.I), lambda m: 'Memorised' if m.group()[0].isupper() else 'memorised'),
    # Noun/misc
    (re.compile(r'\bpretense\b', re.I), lambda m: 'Pretence' if m.group()[0].isupper() else 'pretence'),
    (re.compile(r'\bdialog\b', re.I), lambda m: 'Dialogue' if m.group()[0].isupper() else 'dialogue'),
    (re.compile(r'\bcatalog\b', re.I), lambda m: 'Catalogue' if m.group()[0].isupper() else 'catalogue'),
    (re.compile(r'\bcanceled\b', re.I), lambda m: 'Cancelled' if m.group()[0].isupper() else 'cancelled'),
    (re.compile(r'\bcanceling\b', re.I), lambda m: 'Cancelling' if m.group()[0].isupper() else 'cancelling'),
    (re.compile(r'\blabeled\b', re.I), lambda m: 'Labelled' if m.group()[0].isupper() else 'labelled'),
    (re.compile(r'\blabeling\b', re.I), lambda m: 'Labelling' if m.group()[0].isupper() else 'labelling'),
    (re.compile(r'\baging\b', re.I), lambda m: 'Ageing' if m.group()[0].isupper() else 'ageing'),
    (re.compile(r'\bfulfill\b', re.I), lambda m: 'Fulfil' if m.group()[0].isupper() else 'fulfil'),
    (re.compile(r'\bfulfilled\b', re.I), lambda m: 'Fulfilled' if m.group()[0].isupper() else 'fulfilled'),
    (re.compile(r'\bmaneuver\b', re.I), lambda m: 'Manoeuvre' if m.group()[0].isupper() else 'manoeuvre'),
    (re.compile(r'\bwillful\b', re.I), lambda m: 'Wilful' if m.group()[0].isupper() else 'wilful'),
    (re.compile(r'\bskillful\b', re.I), lambda m: 'Skilful' if m.group()[0].isupper() else 'skilful'),
    # -or → -our
    (re.compile(r'\brumor\b', re.I), lambda m: 'Rumour' if m.group()[0].isupper() else 'rumour'),
    (re.compile(r'\bhumor\b', re.I), lambda m: 'Humour' if m.group()[0].isupper() else 'humour'),
    (re.compile(r'\bflavor\b', re.I), lambda m: 'Flavour' if m.group()[0].isupper() else 'flavour'),
    # -er → -re
    (re.compile(r'\bfiber\b', re.I), lambda m: 'Fibre' if m.group()[0].isupper() else 'fibre'),
    (re.compile(r'\btheater\b', re.I), lambda m: 'Theatre' if m.group()[0].isupper() else 'theatre'),
    (re.compile(r'\b(?<!para|ther|baro)meter\b', re.I), lambda m: 'Metre' if m.group()[0].isupper() else 'metre'),
    # Medical/forensic
    (re.compile(r'\bhemorrhage\b', re.I), lambda m: 'Haemorrhage' if m.group()[0].isupper() else 'haemorrhage'),
    (re.compile(r'\banesthetic\b', re.I), lambda m: 'Anaesthetic' if m.group()[0].isupper() else 'anaesthetic'),
    (re.compile(r'\bpediatric\b', re.I), lambda m: 'Paediatric' if m.group()[0].isupper() else 'paediatric'),
    # judgment → judgement
    (re.compile(r'\bjudgment\b', re.I), lambda m: 'Judgement' if m.group()[0].isupper() else 'judgement'),
]

def normalise_au_spelling(text: str) -> str:
    """Convert American English to Australian English in ground titles."""
    if not text:
        return text
    for pattern, replacement in _AU_REPLACEMENTS:
        text = pattern.sub(replacement, text)
    return text


async def cleanup_duplicate_grounds(db, case_id: str, user_id: str) -> dict:
    """ — Scan and merge duplicate grounds for a case.

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
        # Archive-before-delete safety layer (added 24 Feb 2026). Matching
        # and deletion semantics are unchanged; this writes a full copy of
        # every row into `dedup_archive` before the delete fires so the
        # records remain recoverable. See services/dedup_archive.py.
        from services.dedup_archive import archive_records_before_delete, new_dedup_run_id
        dedup_run_id = new_dedup_run_id()
        docs_to_archive = [g for g in all_grounds if g.get("ground_id") in set(duplicate_ids)]
        await archive_records_before_delete(
            db,
            source_collection="grounds_of_merit",
            records=docs_to_archive,
            id_field="ground_id",
            reason="cleanup_duplicate_grounds",
            dedup_run_id=dedup_run_id,
        )
        result = await db.grounds_of_merit.delete_many({"ground_id": {"$in": duplicate_ids}})
        logger.info(f"Dedup cleanup for case {case_id}: removed {result.deleted_count} duplicate grounds ({len(all_grounds)} → {len(unique_grounds)}); archive run_id={dedup_run_id}")

    return {
        "before": len(all_grounds),
        "after": len(unique_grounds),
        "removed": len(duplicate_ids),
        "removed_ids": duplicate_ids,
    }


async def cleanup_duplicate_issues(db, case_id: str, user_id: str) -> dict:
    """ — Scan and merge duplicate issue_classifications for a case."""
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
        # Archive-before-delete safety layer (added 24 Feb 2026). Matching
        # and deletion semantics are unchanged; this writes a full copy of
        # every issue into `dedup_archive` before the delete fires.
        from services.dedup_archive import archive_records_before_delete, new_dedup_run_id
        dedup_run_id = new_dedup_run_id()
        docs_to_archive = [i for i in all_issues if i.get("issue_id") in set(duplicate_ids)]
        await archive_records_before_delete(
            db,
            source_collection="issue_classifications",
            records=docs_to_archive,
            id_field="issue_id",
            reason="cleanup_duplicate_issues",
            dedup_run_id=dedup_run_id,
        )
        await db.issue_classifications.delete_many({"issue_id": {"$in": duplicate_ids}})
        logger.info(f"Issue dedup cleanup for case {case_id}: removed {len(duplicate_ids)} duplicates ({len(all_issues)} → {len(unique_issues)}); archive run_id={dedup_run_id}")

    return {
        "before": len(all_issues),
        "after": len(unique_issues),
        "removed": len(duplicate_ids),
    }
