# DO NOT UNDO — staged classification pipeline. Additive module.
from services.llm_service import call_llm_for_json
from services.pipeline_models import IssueClassification

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
}


async def classify_case_issues(case: dict, case_extract: dict) -> list[IssueClassification]:
    system_prompt = """You are a specialist Australian appellate lawyer conducting a thorough issue-spot for criminal appeal preparation.
Your task is to identify ALL potential grounds of appeal that are supported by the case material.
Be thorough and exhaustive — identify every distinct legal issue, procedural error, evidential problem,
sentencing concern, and rights violation that could form a ground of appeal.
Do NOT merge different issues together. Each distinct legal argument deserves its own ground.
For example, a sentencing error based on double-counting is DIFFERENT from a sentencing error based
on manifest excess. A failure to call witnesses is DIFFERENT from a failure to object to evidence.

CRITICAL RULES FOR APPELLATE GROUNDING:
- Every ground MUST be tied to a specific appellate pathway (e.g. miscarriage of justice, unsafe verdict, misdirection, procedural unfairness, fresh evidence, sentencing error).
- Do NOT overuse constitutional framing (e.g. s 80 Constitution). In state criminal appeals, the primary pathways are: miscarriage of justice, unsafe verdict, misdirection, procedural unfairness, fresh evidence, and sentencing error under the relevant Criminal Appeal Act.
- Constitutional grounds should only appear when genuinely and specifically engaged.
- Use assertive language: "The trial judge erred in...", "It is contended that...", "The primary judge failed to...". Do NOT use "may have", "could potentially", "it is possible that".
- For law sections: provide ACTUAL section numbers. If the exact section number is not known, do NOT include the law section at all. Never write "section not provided" or leave placeholders.
- For similar cases: only cite cases if a real citation is known. Do NOT use "[Surname]" or "[Year]" placeholders. If no verified citation exists, omit the field entirely."""

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

    state = case.get("state", "nsw")
    offence_cat = case.get("offence_category", "unknown")
    appellate_act = APPELLATE_PATHWAYS.get(state, APPELLATE_PATHWAYS["nsw"])

    user_prompt = f"""Based on the extracted record below, identify ALL potential grounds of appeal.
Be thorough — examine every aspect of the case for possible appealable issues.

Jurisdiction: {state.upper()}
Offence category: {offence_cat}
Offence type: {case.get('offence_type', 'Not specified')}
Primary appellate legislation: {appellate_act}

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
      "linked_fact_ids": ["fact_xxx"],
      "linked_event_ids": ["xevt_xxx"],
      "linked_finding_ids": ["find_xxx"],
      "classification_confidence": "<strong|moderate|weak>"
    }}
  ]
}}

STRICT RULES:
- Identify as many distinct grounds as the evidence supports. Aim for 8-15 grounds if the case material warrants it.
- Do NOT merge different legal arguments into one ground. Each distinct issue gets its own entry.
- Each ground MUST include an appellate_pathway field identifying the specific statutory provision engaged.
- Use assertive appellate language: "The trial judge erred in failing to...", "It is contended that...", not "may have" or "could potentially".
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
        issues.append(IssueClassification(
            case_id=case["case_id"],
            user_id=case["user_id"],
            title=raw.get("title", "Untitled issue"),
            ground_type=_norm_ground_type(raw.get("ground_type")),
            description=raw.get("description", ""),
            linked_fact_ids=raw.get("linked_fact_ids", []),
            linked_event_ids=raw.get("linked_event_ids", []),
            linked_finding_ids=raw.get("linked_finding_ids", []),
            classification_confidence=raw.get("classification_confidence", "moderate"),
            jurisdiction=state,
            appellate_pathway=raw.get("appellate_pathway", ""),
            error_identified=raw.get("error_identified", ""),
            materiality=raw.get("materiality", ""),
        ))

    # DO NOT UNDO — Post-classification: merge overlapping grounds into sub-issues
    issues = _merge_overlapping_grounds(issues)

    return issues


def _merge_overlapping_grounds(issues: list) -> list:
    """Merge grounds that address the same underlying theme into a single ground with sub-issues.
    E.g. 'psychiatric conflict', 'behavioural evidence + intent', 'mental illness not reducing culpability'
    are all sub-issues of 'Failure to Properly Evaluate Psychiatric Evidence'.
    """
    if len(issues) <= 3:
        return issues

    # Theme clusters — grounds that should be merged
    THEME_KEYWORDS = {
        "psychiatric_evidence": ["psychiatric", "psychosis", "mental health", "mental illness", "mental state", "mental impairment", "psychological"],
        "intent_mens_rea": ["intent", "mens rea", "state of mind", "cognitive capacity", "volition"],
        "sentencing": ["sentencing", "manifest excess", "manifestly excessive", "sentence"],
        "procedural": ["procedural", "judge-alone", "judge alone", "jury selection"],
    }

    from collections import defaultdict
    clusters = defaultdict(list)
    unclustered = []

    for issue in issues:
        title_lower = (issue.title or "").lower()
        desc_lower = (issue.description or "").lower()
        combined = f"{title_lower} {desc_lower}"

        matched_theme = None
        for theme, keywords in THEME_KEYWORDS.items():
            if any(kw in combined for kw in keywords):
                if matched_theme is None:
                    matched_theme = theme
                # Don't double-assign

        if matched_theme and len([i for i in issues if any(kw in f"{(i.title or '').lower()} {(i.description or '').lower()}" for kw in THEME_KEYWORDS[matched_theme])]) > 1:
            clusters[matched_theme].append(issue)
        else:
            unclustered.append(issue)

    merged = list(unclustered)
    for theme, cluster_issues in clusters.items():
        if len(cluster_issues) <= 1:
            merged.extend(cluster_issues)
            continue

        # Pick the broadest issue as the parent
        parent = max(cluster_issues, key=lambda i: len(i.description or ""))
        sub_issues = [f"({chr(97 + idx)}) {ci.title}" for idx, ci in enumerate(cluster_issues)]
        sub_desc = "; ".join(sub_issues)

        parent.description = f"{parent.description}\n\nSub-issues: {sub_desc}"
        if not parent.appellate_pathway and cluster_issues[0].appellate_pathway:
            parent.appellate_pathway = cluster_issues[0].appellate_pathway

        merged.append(parent)

    return merged
