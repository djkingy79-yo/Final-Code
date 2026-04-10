# DO NOT UNDO — staged verification pipeline. Additive module.
from services.llm_service import call_llm_for_json
from services.legitimacy_engine import calculate_ground_rating
from services.pipeline_models import IssueVerification


def _validate_issue_verification(payload: dict) -> bool:
    return (
        isinstance(payload, dict)
        and isinstance(payload.get("supporting_items"), list)
        and isinstance(payload.get("undermining_items"), list)
        and isinstance(payload.get("missing_items"), list)
    )


async def verify_issue(case: dict, issue: dict, supporting_context: dict) -> IssueVerification:
    state = case.get('state', '') or ''
    state_key = state.lower().strip()

    # Inject legislative framework so the LLM has real acts/sections to cite
    from services.offence_helpers import _build_state_framework_context
    legislation_reference = ""
    if state_key:
        legislation_reference = _build_state_framework_context(state_key)

    system_prompt = f"""You are a senior Australian appellate lawyer verifying a candidate ground of appeal.
Assess the identified issue against the extracted record.
Return supporting, undermining, and missing material.
Do not overstate the issue.
Do not state that the issue is made out unless clearly supported.

CRITICAL RULES:
- Use forensic appellate language: "It is arguable that the trial judge erred...", "It is contended that...", "There is a tenable argument that..." — NOT bare declarations like "The trial judge erred" (too definitive at this stage). NOT hedging like "may have", "could potentially" (too weak).

LAW SECTIONS — CRITICAL DISTINCTION:
- The "appellate_pathway" field already records WHICH ACT GIVES THE RIGHT TO APPEAL (e.g. s 6(1) Criminal Appeal Act 1912). Do NOT repeat the appellate act in law_sections.
- law_sections must identify the SUBSTANTIVE legislation that was allegedly breached, misapplied, or engaged by this ground. These are the laws about the OFFENCE, SENTENCING, EVIDENCE, PROCEDURE, or RIGHTS — NOT the appeal provision itself.
- Examples of CORRECT law_sections:
  * For a sentencing error ground: Crimes (Sentencing Procedure) Act 1999 (NSW), s 21A (aggravating/mitigating factors) or s 44 (standard non-parole periods)
  * For a murder conviction safety ground: Crimes Act 1900 (NSW), s 18 (murder definition) or s 23A (substantial impairment by abnormality of mind)
  * For an evidence admissibility ground: Evidence Act 1995 (NSW/Cth), s 137 (exclusion of prejudicial evidence) or s 138 (improperly obtained evidence)
  * For a procedural fairness ground: Criminal Procedure Act 1986 (NSW), s 132 (judge alone election) or Jury Act 1977 (NSW), s 53C
  * For an ineffective counsel ground: Criminal Appeal Act 1912, s 6(1) is the APPELLATE PATHWAY (already recorded) — the law_section should instead be the specific substantive provision the counsel failed to raise or misapplied
- Do NOT include entries with "Act name" or "section" as placeholders. If the exact section number is NOT known with confidence, do NOT include that entry AT ALL. An empty law_sections array is better than guesswork.

{legislation_reference}

- For similar_cases: ONLY include cases with REAL, complete citations (e.g. "R v Falconer [1990] HCA 49"). Do NOT use "[Surname]", "[Year]", or "citation verification needed". If no verified case citation is known, return an empty similar_cases array. Unverified cases damage professional credibility.
- Use AUSTRALIAN ENGLISH ONLY (analyse, organise, defence, offence, behaviour, favour, honour, centre, specialise, recognise, authorise, emphasise, summarise, counselling). Do NOT use American spellings.
- GROUND FRAMING RULES:
  * If this issue involves psychiatric/mental state evidence undermining intent → frame the verification around whether mens rea was properly determined (this is a CONVICTION SAFETY argument, not merely evidentiary criticism).
  * If this issue involves ineffective counsel → include a note that this ground is "Contingent — requires evidentiary support (affidavit from accused, evidence of advice given, transcript confirmation)" since the threshold is extremely high.
  * If this issue involves sentencing → frame around proportionality and moral culpability — whether the sentence reflects true culpability, not just "the judge got it wrong."
Return JSON only."""

    user_prompt = f"""Verify this candidate appellate issue.

CASE:
- Title: {case.get('title', 'Unknown')}
- State: {state.upper()}
- Offence Category: {case.get('offence_category', 'unknown')}

ISSUE:
- Title: {issue.get('title')}
- Ground Type: {issue.get('ground_type')}
- Description: {issue.get('description')}
- Appellate Pathway: {issue.get('appellate_pathway', 'Not specified')}

SUPPORTING CONTEXT:
{supporting_context}

Return ONLY valid JSON:
{{
  "supporting_items": [
    {{
      "document_id": "optional",
      "filename": "optional",
      "quote": "supporting quote from the case material",
      "page_reference": "optional",
      "role": "supports",
      "confidence": "strong|moderate|weak"
    }}
  ],
  "undermining_items": [
    {{
      "document_id": "optional",
      "filename": "optional",
      "quote": "undermining quote from the case material",
      "page_reference": "optional",
      "role": "undermines",
      "confidence": "strong|moderate|weak"
    }}
  ],
  "missing_items": ["description of missing transcript, evidence, or proof item needed"],
  "law_sections": [
    {{
      "act": "Full SUBSTANTIVE Act name (e.g. Crimes Act 1900 (NSW), Evidence Act 1995 (NSW), Crimes (Sentencing Procedure) Act 1999 (NSW)) — NOT the Criminal Appeal Act",
      "section": "actual section number e.g. 18 or 23A or 137 or 21A",
      "jurisdiction": "{state.upper() if state else 'UNSPECIFIED'}",
      "title": "what this section covers (e.g. 'definition of murder', 'substantial impairment', 'exclusion of prejudicial evidence')",
      "verification_status": "unverified"
    }}
  ],
  "similar_cases": [
    {{
      "case_name": "R v Surname [Year]",
      "citation": "Full citation e.g. [2015] NSWCCA 123",
      "jurisdiction": "{state.upper() if state else 'UNSPECIFIED'}",
      "relevance_note": "brief note on how this case is relevant to this ground",
      "verification_status": "unverified"
    }}
  ],
  "verification_status": "reviewed",
  "requires_human_review": true
}}

STRICT RULES:
- law_sections must contain SUBSTANTIVE legislation (Crimes Act, Evidence Act, Sentencing Act, Criminal Procedure Act, etc.) — NOT the appellate act (Criminal Appeal Act, Criminal Code appeal provisions). The appellate pathway is already recorded separately. Each ground should reference which specific section of substantive law was breached or engaged.
- ONLY include entries where you can provide an ACTUAL section number. If unsure of the section number, OMIT that entry entirely. An empty array is acceptable.
- similar_cases: ONLY include cases where you can provide a REAL case name and citation. If unsure, OMIT. An empty array is acceptable. Never use placeholder names like "[Surname]".
- supporting_items quotes must be actual text from the case material, not generalised statements.
- All analysis must use Australian English spelling."""

    parsed = await call_llm_for_json(
        system_prompt,
        user_prompt,
        session_id=f"verify_{issue.get('issue_id', 'issue')}",
        task_type="issue_verification",
        validation_fn=_validate_issue_verification,
    )

    # DO NOT UNDO — Post-process: strip any law sections without real section numbers
    # Also strip entries that are just the appellate act (not substantive legislation)
    clean_law_sections = []
    for ls in parsed.get("law_sections", []):
        section = (ls.get("section") or "").strip()
        act = (ls.get("act") or "").strip()
        if not section or not act:
            continue
        # Strip placeholder/generic entries
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
        # Skip if it's just the appellate pathway act repeated
        if "Criminal Appeal Act" in act and "6(1)" in section:
            continue
        clean_law_sections.append(ls)

    # DO NOT UNDO — Post-process: strip any similar cases with placeholder names
    clean_similar_cases = []
    for sc in parsed.get("similar_cases", []):
        name = sc.get("case_name", "")
        citation = sc.get("citation", "")
        if not name or "[Surname]" in name or "[Year]" in name or "Case name" in name:
            continue
        if citation and ("verification needed" in citation.lower() or "not available" in citation.lower()):
            sc["citation"] = None
        clean_similar_cases.append(sc)

    # DO NOT UNDO — Enforce forensic language in verification text fields
    from services.offence_helpers import enforce_forensic_language
    supporting_items = parsed.get("supporting_items", [])
    undermining_items = parsed.get("undermining_items", [])
    for item_list in [supporting_items, undermining_items]:
        for item in item_list:
            if isinstance(item, dict):
                for key in ["analysis", "significance", "detail", "description", "note"]:
                    if key in item and isinstance(item[key], str):
                        item[key] = enforce_forensic_language(item[key])

    scores = calculate_ground_rating({
        "ground_type": issue.get("ground_type", "other"),
        "supporting_evidence": parsed.get("supporting_items", []),
        "undermining_items": parsed.get("undermining_items", []),
    })

    return IssueVerification(
        issue_id=issue["issue_id"],
        case_id=case["case_id"],
        user_id=case["user_id"],
        supporting_items=parsed.get("supporting_items", []),
        undermining_items=parsed.get("undermining_items", []),
        missing_items=parsed.get("missing_items", []),
        law_sections=clean_law_sections,
        similar_cases=clean_similar_cases,
        legitimacy_scores=scores,
        verification_status=parsed.get("verification_status", "reviewed"),
        requires_human_review=bool(parsed.get("requires_human_review", True)),
    )
