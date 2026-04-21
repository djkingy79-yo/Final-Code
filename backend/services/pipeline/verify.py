# DO NOT UNDO — staged verification pipeline. Additive module.
import logging
from services.llm_service import call_llm_for_json
from services.legitimacy_engine import calculate_ground_rating
from services.pipeline_models import IssueVerification

logger = logging.getLogger(__name__)


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

    # DO NOT UNDO — inject landmark authorities so the LLM has REAL, verified
    # citations to draw from. Previously the prompt told the LLM to omit when
    # "unsure", which made every investigation return 0 comparable cases even
    # though landmark High Court authorities are directly on point. Now the
    # LLM is seeded with the registered landmark cases for the ground_type
    # (plus closely related categories) and instructed to use them.
    from frameworks import LANDMARK_CASES
    ground_type = (issue.get("ground_type") or "other").lower()
    # Map ground_type to the closest framework category. Multiple categories
    # can be relevant (e.g. an unsafe verdict case might also engage the
    # proviso). Supply all that plausibly apply so the model has options.
    category_aliases = {
        "unsafe_verdict": ["unsafe_verdict", "proviso"],
        "proviso": ["proviso", "unsafe_verdict"],
        "sentencing_error": ["sentencing_manifest_excess", "sentencing_totality"],
        "sentencing_manifest_excess": ["sentencing_manifest_excess", "sentencing_totality"],
        "sentencing_totality": ["sentencing_totality", "sentencing_manifest_excess"],
        "fresh_evidence": ["fresh_evidence", "unsafe_verdict"],
        "ineffective_counsel": ["ineffective_counsel", "misdirection"],
        "misdirection": ["misdirection", "unsafe_verdict"],
        "jury_irregularity": ["misdirection", "unsafe_verdict"],
        "prosecution_misconduct": ["prosecution_misconduct", "misdirection"],
        "procedural_fairness": ["misdirection", "unsafe_verdict"],
    }
    picked = category_aliases.get(ground_type, ["unsafe_verdict", "misdirection", "proviso"])
    landmark_lines = []
    seen_cases = set()
    for cat in picked:
        for entry in LANDMARK_CASES.get(cat, []):
            key = entry.get("case")
            if key and key not in seen_cases:
                seen_cases.add(key)
                landmark_lines.append(f"- {entry['case']} — {entry['principle']}")
    landmark_reference = (
        "\n\nLANDMARK AUSTRALIAN AUTHORITIES for this ground type (use these in "
        "similar_cases where genuinely on point — they are verified High Court / "
        "intermediate appellate decisions):\n" + "\n".join(landmark_lines)
    ) if landmark_lines else ""

    system_prompt = f"""You are a senior Australian appellate lawyer verifying a candidate ground of appeal.
Assess the identified issue against the extracted record.
Return supporting, undermining, and missing material.
Do not overstate the issue.
Do not state that the issue is made out unless clearly supported.

CRITICAL RULES:
- Use forensic appellate language: "It is arguable that the trial judge erred...", "It is contended that...", "There is a tenable argument that..." — NOT bare declarations like "The trial judge erred" (too definitive at this stage). NOT hedging like "may have", "could potentially" (too weak).

LAW SECTIONS — CRITICAL DISTINCTION:

ANTI-HALLUCINATION — ABSOLUTE:
- Do NOT invent or fabricate any legislation, Act names, section numbers, case citations, dates, or facts not supported by the extracted record.
- If uncertain about any detail, flag that verification is required rather than guessing.

- The "appellate_pathway" field already records WHICH ACT GIVES THE RIGHT TO APPEAL (e.g. s 6(1) Criminal Appeal Act 1912). PREFER substantive legislation in law_sections over repeating the appellate act.
- law_sections should identify the SUBSTANTIVE legislation that was allegedly breached, misapplied, or engaged by this ground. These are the laws about the OFFENCE, SENTENCING, EVIDENCE, PROCEDURE, or RIGHTS.
- HOWEVER, if no specific substantive section is directly applicable (e.g. for fresh evidence, ineffective counsel, jury irregularity, constitutional violation, or prosecution misconduct grounds), you MUST STILL include the relevant appellate provision sections or the most closely related procedural/constitutional sections. An empty law_sections array is NOT acceptable — every ground must reference at least one legislative provision.
- Examples of CORRECT law_sections (use the CORRECT Acts for the case jurisdiction — do NOT default to NSW Acts for non-NSW cases):
  * For a sentencing error ground: the jurisdiction's Sentencing Act (e.g. Sentencing Act 1991 (Vic), Penalties and Sentences Act 1992 (Qld), Sentencing Act 2017 (SA))
  * For a conviction safety ground: the jurisdiction's Criminal Code/Act (e.g. Crimes Act 1958 (Vic), Criminal Code Act 1899 (Qld), Criminal Law Consolidation Act 1935 (SA))
  * For an evidence admissibility ground: the jurisdiction's Evidence Act (e.g. Evidence Act 2008 (Vic), Evidence Act 1977 (Qld), Evidence Act 1929 (SA))
  * For a procedural fairness ground: the jurisdiction's Criminal Procedure Act (e.g. Criminal Procedure Act 2009 (Vic))
  * For an ineffective counsel ground: the law_section should be the specific substantive provision the counsel failed to raise or misapplied — NOT the appellate pathway act
- Do NOT include entries with "Act name" or "section" as placeholders. If the exact section number is NOT known with high confidence, use the most relevant general section (e.g. "Part VI" or "Division 3") rather than omitting entirely. Every ground MUST have at least one law_sections entry.

{legislation_reference}{landmark_reference}

- For similar_cases: Include AT LEAST TWO real authorities drawn from the LANDMARK list above where genuinely applicable to this ground type, PLUS any additional well-known Australian appellate decisions you can cite with confidence (full case name + neutral citation e.g. "R v Falconer [1990] HCA 49", or law-report cite e.g. "M v The Queen (1994) 181 CLR 487"). Each entry MUST have both case_name and citation populated with real data — NEVER "[Surname]", "[Year]", or "citation verification needed". If a landmark from the list above is on point, USE it; its citation is already verified. An empty similar_cases array is UNACCEPTABLE unless the ground type has no analogous authorities in Australian appellate jurisprudence.
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
      "act": "Full SUBSTANTIVE Act name for THIS jurisdiction (e.g. Crimes Act 1958 (Vic), Criminal Code Act 1899 (Qld)) — NOT the Criminal Appeal Act — do NOT default to NSW Acts",
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
- law_sections must contain legislation relevant to the ground — preferably SUBSTANTIVE legislation (Crimes Act, Evidence Act, Sentencing Act, Criminal Procedure Act, etc.). If no substantive section is applicable, include the relevant appellate act section, procedural act section, or the constitutional/common law principle engaged. Every ground MUST have at least one law_section entry.
- Include entries where you can identify a relevant act and section (even if the section is general, e.g. "Part X" or "Division 3"). Only omit if you truly cannot identify ANY relevant legislation.
- similar_cases: MUST contain AT LEAST TWO entries. Draw from the LANDMARK AUSTRALIAN AUTHORITIES list in the system prompt — those citations are verified and ready to use. Add any further well-known authorities you are confident in. Use real case_name and real citation for every entry. Empty arrays are only acceptable if this ground_type has no analogous appellate authority, which is extremely rare — think about the appellate test and the principle engaged, and cite the authority that established that test.
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
        # Skip if it's just the appellate pathway act repeated AND there are other substantive entries
        # Allow appellate act if it's the ONLY law section available
        if "Criminal Appeal Act" in act and "6(1)" in section:
            # Only skip if there are other entries to keep
            other_valid = [ls2 for ls2 in parsed.get("law_sections", []) if ls2 is not ls and (ls2.get("section") or "").strip() and (ls2.get("act") or "").strip() and "Criminal Appeal Act" not in (ls2.get("act") or "")]
            if other_valid:
                continue
        clean_law_sections.append(ls)

    # DO NOT UNDO — Post-process: strip any similar cases with placeholder names
    # Enhanced with citation hallucination detection
    from services.case_validation import validate_citation
    clean_similar_cases = []
    for sc in parsed.get("similar_cases", []):
        name = sc.get("case_name", "")
        citation = sc.get("citation", "")
        if not name or "[Surname]" in name or "[Year]" in name or "Case name" in name:
            continue
        if citation and ("verification needed" in citation.lower() or "not available" in citation.lower()):
            sc["citation"] = None
        # Validate citation format against known Australian court abbreviations
        full_ref = f"{name} {citation or ''}".strip()
        result = validate_citation(full_ref)
        if not result["valid"]:
            logger.info(f"Stripped hallucinated similar case in verify: {full_ref[:80]} ({result['reason']})")
            continue
        sc["verification_status"] = "unverified — check on AustLII"
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
