# ===========================================================================
# Barrister View Generation Engine
# Extracted from server.py — generate_barrister_brief and utilities
# ===========================================================================

import re
from datetime import datetime, timezone
from typing import List

from fastapi import HTTPException

from config import db, logger
from services.llm_service import call_llm_with_fallback
from services.offence_helpers import (
    _build_recent_legislation_context, _build_state_framework_context,
    _build_federal_framework_context,
    enforce_forensic_language,
)
from services.report_quality import (
    _strip_report_placeholders,
)
from models import ReportMetadata

BARRISTER_SOURCE_TYPES = ["quick_summary", "full_detailed", "extensive_log"]
BARRISTER_GENERATION_TIMEOUT_MINUTES = 40


def _coerce_utc_datetime(value):
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str) and value:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def _generated_at_sort_value(report: dict) -> str:
    return str(report.get("generated_at") or "")


async def _get_latest_standard_reports(case_id: str, user_id: str) -> List[dict]:
    reports = await db.reports.find(
        {
            "case_id": case_id,
            "user_id": user_id,
            "report_type": {"$in": BARRISTER_SOURCE_TYPES},
            "status": "completed",
            "content.aggressive_mode": {"$ne": True},
        },
        {"_id": 0},
    ).sort("generated_at", -1).to_list(50)

    latest_by_type = {}
    for report in reports:
        report_type = report.get("report_type")
        if report_type not in latest_by_type:
            latest_by_type[report_type] = report

    missing_types = [report_type for report_type in BARRISTER_SOURCE_TYPES if report_type not in latest_by_type]
    if missing_types:
        missing_labels = ", ".join(missing_types)
        raise HTTPException(status_code=409, detail=f"Barrister View remains locked until all 3 standard reports are completed. Missing: {missing_labels}")

    selected = [latest_by_type[report_type] for report_type in BARRISTER_SOURCE_TYPES]
    selected.sort(key=_generated_at_sort_value, reverse=True)
    return selected


def _build_barrister_source_signature(reports: List[dict]) -> str:
    ordered = sorted(
        reports,
        key=lambda report: BARRISTER_SOURCE_TYPES.index(report.get("report_type")) if report.get("report_type") in BARRISTER_SOURCE_TYPES else 99,
    )
    return "|".join(
        f"{report.get('report_type')}::{report.get('report_id')}::{report.get('generated_at')}"
        for report in ordered
    )


def _build_barrister_report_source_text(reports: List[dict]) -> str:
    type_labels = {
        "quick_summary": "Quick Summary",
        "full_detailed": "Full Detailed Report",
        "extensive_log": "Extensive Log Report",
    }
    blocks = []
    per_report_limit = 100000
    for report in sorted(
        reports,
        key=lambda item: BARRISTER_SOURCE_TYPES.index(item.get("report_type")) if item.get("report_type") in BARRISTER_SOURCE_TYPES else 99,
    ):
        analysis = _strip_report_placeholders((report.get("content") or {}).get("analysis", ""))
        analysis = re.sub(r"\n{3,}", "\n\n", analysis).strip()
        blocks.append(
            f"===== {type_labels.get(report.get('report_type'), report.get('report_type', 'Report'))} =====\n"
            f"Report ID: {report.get('report_id')}\n"
            f"Generated: {report.get('generated_at')}\n\n"
            f"{analysis[:per_report_limit]}"
        )
    return "\n\n".join(blocks)


def _trim_text_preserving_ends(text: str, max_chars: int) -> str:
    if not text or len(text) <= max_chars:
        return text
    head_chars = int(max_chars * 0.65)
    tail_chars = max_chars - head_chars
    return (
        text[:head_chars].rstrip()
        + "\n\n[Additional detailed source material omitted here for prompt length control]\n\n"
        + text[-tail_chars:].lstrip()
    )


def _build_barrister_group_source_text(reports: List[dict], max_chars_by_type: dict) -> str:
    type_labels = {
        "quick_summary": "Quick Summary",
        "full_detailed": "Full Detailed Report",
        "extensive_log": "Extensive Log Report",
    }
    blocks = []
    for report in sorted(
        reports,
        key=lambda item: BARRISTER_SOURCE_TYPES.index(item.get("report_type")) if item.get("report_type") in BARRISTER_SOURCE_TYPES else 99,
    ):
        report_type = report.get("report_type")
        analysis = _strip_report_placeholders((report.get("content") or {}).get("analysis", ""))
        analysis = re.sub(r"\n{3,}", "\n\n", analysis).strip()
        limited_analysis = _trim_text_preserving_ends(analysis, max_chars_by_type.get(report_type, 18000))
        blocks.append(
            f"===== {type_labels.get(report_type, report_type or 'Report')} =====\n"
            f"Report ID: {report.get('report_id')}\n"
            f"Generated: {report.get('generated_at')}\n\n"
            f"{limited_analysis}"
        )
    return "\n\n".join(blocks)


def _dedupe_barrister_ground_subsections(text: str) -> str:
    section_match = re.search(r"(## Grounds of Merit\n)([\s\S]*?)(?=\n## Statutory Framework)", text)
    if not section_match:
        return text

    grounds_body = section_match.group(2).strip()
    block_pattern = re.compile(r"(### Ground \d+: [^\n]+\n[\s\S]*?)(?=(?:\n### Ground \d+: )|\Z)")
    blocks = [block.strip() for block in block_pattern.findall(grounds_body)]
    if not blocks:
        return text

    deduped_blocks = []
    seen_titles = set()
    for block in blocks:
        heading = block.split("\n", 1)[0].strip()
        title_match = re.match(r"^### Ground \d+: (.+)$", heading)
        title = (title_match.group(1).strip().lower() if title_match else heading.lower())
        if title in seen_titles:
            continue
        seen_titles.add(title)
        deduped_blocks.append(block)

    renumbered_blocks = []
    for index, block in enumerate(deduped_blocks, start=1):
        heading, remainder = (block.split("\n", 1) + [""])[:2]
        title_match = re.match(r"^### Ground \d+: (.+)$", heading.strip())
        title = title_match.group(1).strip() if title_match else heading.replace("### ", "").strip()
        rebuilt = f"### Ground {index}: {title}"
        if remainder.strip():
            rebuilt += f"\n{remainder.strip()}"
        renumbered_blocks.append(rebuilt.strip())

    replacement = "\n\n".join(renumbered_blocks)
    return text[:section_match.start(2)] + replacement + text[section_match.end(2):]


def _normalise_barrister_table_titles(text: str) -> str:
    replacements = {
        "### Table: Comparative Authorities": "### Comparative Authorities Table",
        "### Table: Sentencing Comparison": "### Sentencing Comparison Table",
        "### Table: Evidentiary Pressure Points": "### Evidentiary Pressure Points Table",
        "### Table: Relief Pathways": "### Relief Pathways Matrix",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


#  — Barrister View multi-pass generation engine
async def generate_barrister_brief(case_id: str, user_id: str, report_id: str | None = None) -> dict:
    case = await db.cases.find_one({"case_id": case_id, "user_id": user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    documents = await db.documents.find(
        {"case_id": case_id},
        {"_id": 0}
    ).to_list(300)
    timeline = await db.timeline_events.find({"case_id": case_id}, {"_id": 0}).sort("event_date", 1).to_list(400)
    grounds = await db.grounds_of_merit.find({"case_id": case_id}, {"_id": 0}).to_list(100)
    source_reports = await _get_latest_standard_reports(case_id, user_id)

    timeline_text = "\n".join(
        f"- {event.get('event_date', '')}: {event.get('title', '')} — {event.get('description', '')[:200]}"
        for event in timeline[:25]
    ) or "- No timeline events recorded"
    grounds_text = "\n".join(
        f"- {ground.get('title', 'Untitled ground')} [{ground.get('ground_type', 'other')} / {ground.get('strength', 'unrated')}] — {ground.get('description', '')[:220]}"
        for ground in grounds[:20]
    ) or "- No structured grounds recorded"
    grounds_heading_text = "\n".join(
        f"### Ground {idx}: {ground.get('title', 'Untitled ground')}"
        for idx, ground in enumerate(grounds[:20], start=1)
    ) or "### Ground 1: Grounds identified from source reports"
    documents_text = "\n".join(
        f"- {document.get('filename', 'Untitled document')} ({document.get('category', 'other')})"
        for document in documents[:30]
    ) or "- No documents uploaded"

    case_profile = f"""
CASE TITLE: {case.get('title', 'Unknown case')}
DEFENDANT: {case.get('defendant_name', 'Not recorded')}
CASE NUMBER: {case.get('case_number', 'Not recorded')}
COURT: {case.get('court', 'Not recorded')}
JURISDICTION: {(case.get('state') or 'UNSPECIFIED').upper()}
OFFENCE: {case.get('offence_type') or case.get('offence_category') or 'Not recorded'}
SENTENCE: {case.get('sentence', 'Not recorded')}
DOCUMENT COUNT: {len(documents)}
TIMELINE EVENT COUNT: {len(timeline)}
GROUNDS COUNT: {len(grounds)}
""".strip()

    # Inject recent legislation context for the barrister view
    barrister_state = (case.get('state') or '').lower()
    barrister_offence_cat = case.get('offence_category') or 'general'
    recent_legislation_block = _build_recent_legislation_context(barrister_state, barrister_offence_cat)
    state_framework_block = _build_state_framework_context(barrister_state)
    federal_framework_block = _build_federal_framework_context()

    #  — Barrister View system prompt with strict depth requirements and FORENSIC language
    system_prompt = """You are a senior Australian criminal appeal barrister preparing the definitive barrister brief for a criminal appeal matter. This is the CAPSTONE document that synthesises and BUILDS UPON three earlier analytical reports (Quick Summary, Full Detailed Report, and Extensive Log). The output must read like one coherent, authoritative legal document written by a careful appellate specialist who has thoroughly digested all three source reports and is now producing a comprehensive counsel-ready working brief.

MANDATORY RULES:
- Australian English only.
- Strict third-person educational tone only.
- Never use first-person or second-person language, including: we, us, our, you, your.
- Do not mention that reports were merged, combined, synthesised, tiered, paid, unlocked, or generated by AI.
- Do not include bullet-heavy exposition. Detailed reasoning must be written in flowing paragraphs with concrete factual anchors.
- Minimal bullet points are permitted only for short authority lists, procedural checklists, or document inventories where compact presentation improves clarity.
- No duplication. If the same issue appears across multiple source reports, discuss it once in the most logical section but with GREATER depth than any individual source report achieved.
- No placeholders, meta-commentary, drafting notes, or future-tense filler such as 'will be provided'.
- If the materials are uncertain on a point, say that the available materials indicate or suggest the point rather than asserting unsupported fact.
- Use markdown headings only, with ## for main sections and ### for sub-sections.

FORENSIC APPELLATE LANGUAGE — CRITICAL:
- Appellate work is about ARGUABILITY, not declarations. All conclusions about the current case must be framed forensically.
- Use: "It is arguable that...", "It is contended that...", "There is a tenable argument that...", "On one view of the evidence...", "It is open to the appellant to argue that..."
- Do NOT use bare declarations: "The trial judge erred", "The conviction is unsafe", "The sentence is excessive". These are too definitive at the preparation stage.
- Do NOT use weak hedging: "may have", "could potentially", "it is possible that". These lack the confidence needed for counsel preparation.
- BANNED CHARACTERISATION LANGUAGE: NEVER write "The judge determined that [X]", "The court found that [X]", or "The judge concluded that [X]" when describing a trial-level characterisation of facts, conditions, or mental states. These imply a settled, unchallengeable finding. Use instead: "The judge treated [X] as..." / "The sentencing judge characterised [X] as..." / "The judge approached [X] on the basis that...". CORRECT: "The judge treated the condition as drug-induced and therefore as insufficient to engage the asserted partial defence or materially reduce culpability." WRONG: "The judge determined that the condition was drug-induced and did not mitigate."
- Exception: when citing what a court HAS decided in a precedent case, declarative language is appropriate (e.g. "In R v Smith, the Court held that...").

GROUND FRAMING RULES:
- Where psychiatric/mental state evidence is involved, frame the ground as a CONVICTION SAFETY attack on mens rea — whether the requisite mental state (intent to kill, intent to cause GBH, reckless indifference) was properly determined. This is more powerful than mere evidentiary criticism.
- Where multiple jury/trial procedure issues exist (judge-alone refusal, jury reduction, juror conduct), present as sub-particulars under a single procedural unfairness ground. The CCA prefers "one ground, multiple particulars."
- Where sentencing is challenged, frame around proportionality and moral culpability — whether the sentence reflects true culpability — not merely "the judge got it wrong."
- Where ineffective counsel is advanced, mark clearly as CONTINGENT — requiring evidentiary support (affidavit, transcript confirmation). Note that without this foundation, the ground risks weakening overall appellate credibility.
- **PARTIAL DEFENCES — ABSOLUTE RULE: s 23A Crimes Act 1900 (NSW) (substantial impairment), and equivalent partial defences in other jurisdictions (diminished responsibility (QLD), mental impairment defence (VIC/SA/ACT), unsoundness of mind (WA/TAS)), operate on LIABILITY — they reduce murder to manslaughter. They are NOT sentencing mitigation. NEVER write that s 23A or its equivalents "mitigate mental culpability" or are a sentencing consideration. Frame them ONLY as partial defences at the liability stage.**

DEPTH AND QUALITY MANDATE:
- This brief MUST be substantially MORE detailed than any individual source report. It is NOT a summary — it is an EXPANSION and SYNTHESIS.

JURISDICTION FIDELITY — ABSOLUTE:
- The case jurisdiction is specified in the CASE PROFILE. Use ONLY legislation from THAT jurisdiction.
- Do NOT default to NSW legislation when analysing a case from another jurisdiction.
- Use the correct Criminal Code/Act, Sentencing Act, Evidence Act, Appeal Act, and Criminal Procedure Act for the jurisdiction.
- Commonwealth legislation (Criminal Code Act 1995 (Cth), Crimes Act 1914 (Cth)) applies across ALL jurisdictions and may be cited where relevant.
- If the jurisdiction is UNSPECIFIED, flag this explicitly and state which jurisdiction's legislation is being applied provisionally.

ANTI-HALLUCINATION — ABSOLUTE:
- Do NOT invent case names, citations, section numbers, Act names, judge names, dates, or penalty amounts.
- If the exact citation for a case is not known, do NOT fabricate one. Write: "[citation to be verified by instructing solicitor]".
- If the exact section number is uncertain, reference the Act and Part/Division only.
- Do NOT assume facts not in the supplied case material.
- Do NOT hallucinate sentencing statistics. If uncertain, state: "Sentencing statistics should be verified against Judicial Commission data."
- Every section must incorporate the best material from all 3 source reports AND add original barrister-level analysis that none of the source reports contain: strategic framing, submission structure, cross-examination angles, evidential deployment strategy, likely judicial concerns, and fallback positions.
- Each ground of appeal must be discussed with: factual foundation (citing specific evidence and documents), the applicable legal test (with statutory references), decisive authorities (with paragraph-level citations where available), the strongest argument for the appellant, the likely prosecution response, the reply to that response, fallback positions if the primary argument fails, and how this ground interacts with other grounds.
- The authorities section must not merely list cases. It must explain what each authority establishes, why it applies, how the prosecution might distinguish it, and how counsel should deploy it.
- Sentencing analysis must include specific comparator cases with sentence outcomes, statistical context where available, and analysis of parity, manifest excess, or other applicable principles.
- The strategy sections must be written as if counsel is preparing for a conference with the instructing solicitor: specific questions to address, documents to prepare, hearing structure, time estimates, and priority ordering of grounds.
- Generic observations such as 'this ground has merit' or 'further investigation is recommended' are UNACCEPTABLE without substantial supporting detail.
- The brief is for counsel. Avoid consumer-style explanation and avoid shrinking the material into a simplified note.
"""

    shared_context = f"""CASE PROFILE
{case_profile}

STRUCTURED GROUNDS
{grounds_text}

MANDATORY GROUND LIST
{grounds_heading_text}

TIMELINE SNAPSHOT
{timeline_text}

DOCUMENT INVENTORY
{documents_text}
{recent_legislation_block}
{state_framework_block}
{federal_framework_block}"""

    #  — Section groups with calibrated source limits (larger limits cause 502 proxy errors)
    section_groups = [
        {
            "slug": "counsel-synthesis",
            "target_chars": 6000,
            "source_limits": {"quick_summary": 10000, "full_detailed": 20000, "extensive_log": 28000},
            "required_headings": [
                "## Counsel Synthesis",
            ],
            "instructions": f"""Write ONLY the ## Counsel Synthesis section. This section appears at the VERY TOP of the barrister brief and tells a barrister in 30 seconds: "Where do I attack?"

The section MUST follow this EXACT structure:

## Counsel Synthesis

### Primary Issue
One paragraph (3-4 sentences) identifying the single most important attack vector for the appeal. This should be the ground with the highest appellate viability. Frame it forensically: "It is arguable that..." or "The primary contention is that..."

### Secondary Issue
One paragraph (3-4 sentences) identifying the second strongest line of attack.

### Tertiary Issue
One paragraph (3-4 sentences) identifying the third line of attack.

### Priority Order
A numbered list of ALL grounds in order of priority, with a one-line forensic assessment of each:
1. [Strongest ground] — [one-line assessment]
2. [Second strongest] — [one-line assessment]
3. [Third] — [one-line assessment]
...and so on for all grounds.

Mark any contingent grounds (e.g. ineffective counsel) with: "(Contingent — requires evidentiary support)"

### Overall Appellate Position
One paragraph providing an honest, calibrated assessment of the appeal's overall position. Use viability language (arguable, moderate, strong) — NOT percentages. Frame forensically.

CRITICAL FRAMING RULES:
- Where psychiatric/mental state evidence undermines intent (mens rea), this should typically be the PRIMARY ISSUE — frame as a conviction safety attack on mens rea determination.
- Where jury/procedural issues exist, cluster them as a single ground with sub-particulars.
- Where sentencing is challenged, frame around proportionality and moral culpability.
- Where ineffective counsel appears, flag as contingent and place lower in priority unless strong evidentiary support exists.
- Use ONLY forensic appellate language: "It is arguable that...", "It is contended that...", "There is a tenable argument that..."
- This section must reference the specific grounds from the MANDATORY GROUND LIST below.

There are {len(grounds)} grounds identified for this case.""",
        },
        {
            "slug": "source-synthesis",
            "target_chars": 24000,
            "source_limits": {"quick_summary": 14000, "full_detailed": 28000, "extensive_log": 36000},
            "required_headings": [
                "## Executive Overview for Counsel",
                "## Source Report Synthesis",
                "## Case Background and Procedural History",
                "## Conviction, Offence and Sentence Analysis",
            ],
            "instructions": "Write these sections in full depth. Under ## Executive Overview for Counsel, provide a commanding summary of the appeal's landscape — the conviction, sentence, key vulnerabilities, strongest grounds, and the overall strategic posture. This must be dense enough to brief a senior barrister in one reading. Under ## Source Report Synthesis, create exactly these three sub-headings in this order: ### Quick Summary Synthesis, ### Full Detailed Report Synthesis, ### Extensive Log Synthesis. Under each sub-heading, identify what that source report contributes that is unique, critical, or more developed than the others — do not repeat the same point in all 3 sub-sections. Under ## Case Background and Procedural History, set out the full procedural chronology from charge to sentence with specific dates, courts, and procedural steps. Under ## Conviction, Offence and Sentence Analysis, provide a thorough analysis of the offence elements, the evidence supporting conviction, the sentencing judge's reasoning, statutory framework applied, and any sentencing errors apparent from the materials.",
        },
        {
            "slug": "case-analysis",
            "target_chars": 28000,
            "source_limits": {"quick_summary": 12000, "full_detailed": 28000, "extensive_log": 36000},
            "required_headings": [
                "## Evidentiary Tensions and Appeal Pressure Points",
                "## Grounds of Merit",
                "## Statutory Framework and Governing Tests",
                "## Authorities and Comparative Cases",
            ],
            "instructions": "Write these sections at the highest barrister depth. Under ## Evidentiary Tensions and Appeal Pressure Points, identify every contradiction, gap, procedural irregularity, missing evidence, unreliable testimony, and prosecutorial overreach found across all 3 source reports — organise by issue, explain the appellate significance, and indicate how counsel should exploit each tension point. Under ## Grounds of Merit, create one dedicated ### subsection for EVERY item in the mandatory ground list — do not omit, merge, or collapse any listed ground. Each ground must be explained with: (a) substantial factual support citing specific evidence and documents, (b) the applicable legal test with statutory references, (c) decisive authorities with paragraph-level citations, (d) the strongest argument for the appellant, (e) the likely prosecution response, (f) the reply to that response, (g) weaknesses and fallback positions, (h) strategic implications and interaction with other grounds, and (i) why counsel should care about it in conference and submissions. Under ## Statutory Framework and Governing Tests, set out the relevant legislation, appellate jurisdiction provisions, leave requirements, and the legal tests for each ground type. Under ## Authorities and Comparative Cases, meaningfully compare cases — explain what each authority establishes, why it applies, how the prosecution might distinguish it, and how counsel should deploy it. Include a markdown comparative authorities table.",
        },
        {
            "slug": "strategy",
            "target_chars": 26000,
            "source_limits": {"quick_summary": 10000, "full_detailed": 22000, "extensive_log": 32000},
            "required_headings": [
                "## Sentencing Comparison and Relief Pathways",
                "## Proposed Submissions and Hearing Strategy",
                "## Conference Questions, Filing Priorities and Risks",
                "## Final Appellate Research Briefing Note",
            ],
            "instructions": "Write these sections as an authoritative counsel-facing strategy brief that a barrister would use to prepare for conference and hearing. Under ## Sentencing Comparison and Relief Pathways, analyse specific comparator cases with their sentence outcomes, consider parity, manifest excess, and other sentencing principles, and set out each available relief pathway with its legal basis and likelihood of success. Under ## Proposed Submissions and Hearing Strategy, provide detailed proposed submission themes for each ground, recommended ground ordering, estimated hearing time per ground, oral submission structure, written submission priorities, key documents to include in the appeal book, and how to handle judicial questions. Under ## Conference Questions, Filing Priorities and Risks, list specific questions counsel should address with the instructing solicitor, identify filing deadlines and priority ordering, analyse litigation risk for each ground and the appeal overall, and identify what further material or instructions would strengthen the case. Under ## Final Appellate Research Briefing Note, provide a comprehensive closing analysis that is still detailed rather than compressed — covering the overall assessment, recommended course of action, fallback strategies, costs considerations, and any urgent steps.",
        },
    ]

    section_outputs = []
    resume_index = 0
    if report_id:
        existing_report = await db.reports.find_one(
            {"report_id": report_id},
            {"_id": 0, "content.partial_sections": 1, "content.partial_stage": 1, "content.partial_analysis": 1},
        )
        existing_content = (existing_report or {}).get("content") or {}
        saved_sections = existing_content.get("partial_sections") or []
        if saved_sections:
            section_outputs = list(saved_sections)
            resume_index = min(len(section_outputs), len(section_groups))
            logger.info(f"Resuming barrister brief {report_id} from group {resume_index + 1}")

    for group_index, group in enumerate(section_groups[resume_index:], start=resume_index + 1):
        headings_text = "\n".join(group["required_headings"])
        group_source_text = _build_barrister_group_source_text(source_reports, group["source_limits"])
        group_prompt = f"""Prepare only the following Barrister Brief sections, using the exact headings below and in the exact order:

{headings_text}

Depth requirements:
- Minimum target length for this response: {group['target_chars']} characters.
- Preserve as much useful detail as possible from the source reports.
- Use flowing paragraphs with concrete facts, authorities, procedural detail, and strategy.
- Avoid generic summary language.
- Do not repeat material unless needed for legal continuity.

Specific drafting instruction:
{group['instructions']}

{shared_context}

SOURCE REPORTS
{group_source_text}
"""

        group_response = await call_llm_with_fallback(
            system_prompt,
            group_prompt,
            session_id=f"barrister-{case_id}-{group['slug']}",
            max_tokens=16384,
            timeout_seconds=300,
            task_type="report_generation",
        )
        group_response = _strip_report_placeholders(group_response)
        group_response = re.sub(r"\n{3,}", "\n\n", group_response).strip()
        section_outputs.append(group_response)
        if report_id:
            partial_analysis = "\n\n".join(part for part in section_outputs if part).strip()
            await db.reports.update_one(
                {"report_id": report_id},
                {"$set": {
                    "content.partial_sections": section_outputs,
                    "content.partial_stage": group.get("slug"),
                    "content.partial_analysis": partial_analysis,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                }}
            )

    response = "\n\n".join(part for part in section_outputs if part).strip()

    #  — General expansion DISABLED (causes 502 proxy errors with large payloads)
    # Section-by-section expansion below is more effective and reliable.
    #  — expansion_source_text must remain defined here (used by ground expansion, cross-analysis, strategy, final QA)
    expansion_source_text = _build_barrister_group_source_text(
        source_reports,
        {"quick_summary": 10000, "full_detailed": 24000, "extensive_log": 32000},
    )

    #  — Section-by-section expansion for thin sections
    thin_section_targets = {
        "## Counsel Synthesis": 2000,
        "## Executive Overview for Counsel": 5000,
        "## Source Report Synthesis": 6000,
        "## Case Background and Procedural History": 5000,
        "## Conviction, Offence and Sentence Analysis": 5000,
        "## Evidentiary Tensions and Appeal Pressure Points": 6000,
        "## Statutory Framework and Governing Tests": 5000,
        "## Authorities and Comparative Cases": 5000,
        "## Sentencing Comparison and Relief Pathways": 5000,
        "## Proposed Submissions and Hearing Strategy": 5000,
        "## Conference Questions, Filing Priorities and Risks": 4000,
        "## Final Appellate Research Briefing Note": 4000,
    }
    section_expansion_source = _build_barrister_group_source_text(
        source_reports,
        {"quick_summary": 10000, "full_detailed": 26000, "extensive_log": 32000},
    )
    for section_heading, min_chars in thin_section_targets.items():
        if section_heading not in response:
            # Missing section — generate it fresh
            try:
                missing_prompt = f"""Write only the following section of a Barrister Brief. Output ONLY this one section with its heading:

{section_heading}

Requirements:
- Minimum target length: {min_chars} characters.
- Dense, counsel-facing, case-specific content using the source reports.
- Australian English, strict third-person tone.
- No bullet-heavy exposition — use flowing paragraphs.

SOURCE REPORTS
{section_expansion_source}

CURRENT BARRISTER BRIEF
{response}
"""
                missing_section = await call_llm_with_fallback(
                    system_prompt, missing_prompt,
                    session_id=f"barrister-{case_id}-missing-{section_heading[3:20].lower().replace(' ','-')}",
                    max_tokens=16384, timeout_seconds=300, task_type="report_generation",
                )
                missing_section = _strip_report_placeholders(missing_section)
                missing_section = re.sub(r"\n{3,}", "\n\n", missing_section).strip()
                if missing_section.startswith(section_heading):
                    # Find the right insertion point
                    section_order = list(thin_section_targets.keys())
                    idx = section_order.index(section_heading)
                    inserted = False
                    for later_heading in section_order[idx + 1:]:
                        if later_heading in response:
                            response = response.replace(later_heading, missing_section.rstrip() + "\n\n" + later_heading, 1)
                            inserted = True
                            break
                    if not inserted:
                        # Append before strategy sections
                        if "## Proposed Submissions and Hearing Strategy" in response:
                            response = response.replace("## Proposed Submissions and Hearing Strategy",
                                missing_section.rstrip() + "\n\n## Proposed Submissions and Hearing Strategy", 1)
                        else:
                            response = response.rstrip() + "\n\n" + missing_section
                    logger.info(f"Generated missing section: {section_heading} ({len(missing_section)} chars)")
            except Exception as exc:
                logger.warning(f"Missing section generation skipped for {section_heading}: {exc}")
            continue

        # Existing section — check if it's too thin
        section_match = re.search(
            rf"({re.escape(section_heading)}\n[\s\S]*?)(?=\n## |\Z)",
            response,
        )
        if section_match:
            section_text = section_match.group(1)
            if len(section_text) < min_chars:
                try:
                    expand_prompt = f"""Rewrite and substantially expand the following section of a Barrister Brief. Output ONLY this one section with its heading:

{section_heading}

Current section content (too thin — expand to at least {min_chars} characters):
{section_text}

Requirements:
- Keep ALL existing content and ADD more depth, more factual detail, more legal reasoning.
- Minimum target length: {min_chars} characters.
- Dense, counsel-facing, case-specific content.
- Australian English, strict third-person tone.
- No bullet-heavy exposition — use flowing paragraphs.

SOURCE REPORTS
{section_expansion_source}
"""
                    expanded_section = await call_llm_with_fallback(
                        system_prompt, expand_prompt,
                        session_id=f"barrister-{case_id}-thin-{section_heading[3:20].lower().replace(' ','-')}",
                        max_tokens=16384, timeout_seconds=300, task_type="report_generation",
                    )
                    expanded_section = _strip_report_placeholders(expanded_section)
                    expanded_section = re.sub(r"\n{3,}", "\n\n", expanded_section).strip()
                    if expanded_section.startswith(section_heading) and len(expanded_section) > len(section_text):
                        response = response.replace(section_text, expanded_section, 1)
                        logger.info(f"Expanded thin section: {section_heading} ({len(section_text)} → {len(expanded_section)} chars)")
                except Exception as exc:
                    logger.warning(f"Thin section expansion skipped for {section_heading}: {exc}")

    #  — Ground expansion: rewrites each ground as a ### subsection with deep analysis
    if len(response) < 100000 and grounds:
        try:
            rewritten_ground_sections = []
            for ground_index, ground in enumerate(grounds, start=1):
                ground_title = (ground.get("title") or f"Ground {ground_index}").strip()
                ground_prompt = f"""Write only the following Barrister Brief subsection in this exact heading format:

### {ground_title}

Requirements:
- Minimum target length for this subsection alone: 7000 characters.
- Focus on critical, vital, counsel-useful detail rather than generic explanation.
- Set out the factual foundation for the ground, procedural context, legal test, statutory framework, decisive authorities, documentary anchors, timeline anchors, evidentiary vulnerabilities, likely prosecution answer, reply strategy, fallback positions, relief implications, and how counsel should frame the point in written and oral submissions.
- Do not repeat generic appeal language.
- Keep the tone strictly barrister-facing and case-specific.

STRUCTURED GROUND
TITLE: {ground_title}
DESCRIPTION: {ground.get('description', '')}
LEGAL BASIS: {ground.get('legal_basis', '')}
WHY IT MATTERS: {ground.get('strength_reason', '')}
RISK LEVEL: {ground.get('strength', '')}
SUPPORTING DOCUMENT IDS: {', '.join(ground.get('supporting_documents', []) or [])}

MANDATORY GROUND LIST
{grounds_heading_text}

SOURCE REPORTS
{expansion_source_text}

CURRENT BARRISTER BRIEF
{response}
"""
                subsection = await call_llm_with_fallback(
                    system_prompt,
                    ground_prompt,
                    session_id=f"barrister-{case_id}-ground-{ground_index}-expand",
                    max_tokens=16384,
                    timeout_seconds=300,
                    task_type="report_generation",
                )
                subsection = _strip_report_placeholders(subsection)
                subsection = re.sub(r"\n{3,}", "\n\n", subsection).strip()
                #  — Strip any heading format the LLM used and enforce ### subsection format
                subsection = re.sub(r'^#{1,4}\s*' + re.escape(ground_title) + r'\s*\n+', '', subsection).strip()
                subsection = f"### {ground_title}\n\n{subsection}"
                rewritten_ground_sections.append(subsection)

            rewritten_grounds = "## Grounds of Merit\n\n" + "\n\n".join(rewritten_ground_sections).strip()
            if rewritten_ground_sections:
                response = re.sub(
                    r"## Grounds of Merit\n[\s\S]*?(?=\n## Statutory Framework and Governing Tests)",
                    rewritten_grounds + "\n\n",
                    response,
                    count=1,
                )
        except Exception as exc:
            logger.warning(f"Barrister grounds expansion skipped for {case_id}: {exc}")

    #  — Cross-analysis MUST run BEFORE strategy expansion to avoid content loss
    # Cross-analysis sections insert before Sentencing Comparison, not at end
    # Always run — these are unique sections not generated elsewhere
    if "## Report-to-Report Cross-Analysis" not in response:
        cross_analysis_prompt = f"""Produce only the following sections, in this exact order:

## Report-to-Report Cross-Analysis
## Document and Evidence Deployment for Counsel

Requirements:
- Minimum target length for this response: 28000 characters.
- Use all 3 source reports and identify where they overlap, where they diverge, and what unique critical material each one contributes.
- Do not recycle the same paragraph 3 times. Organise the material by issue and explain which source report adds what.
- Under ## Document and Evidence Deployment for Counsel, explain how specific documents, witnesses, chronology items, psychiatric material, media material, and procedural incidents should be deployed by counsel in conference, written submissions, and oral argument.
- This must be dense, counsel-facing, and case-specific.

SOURCE REPORTS
{expansion_source_text}

CURRENT BARRISTER BRIEF
{response}
"""
        try:
            cross_analysis = await call_llm_with_fallback(
                system_prompt,
                cross_analysis_prompt,
                session_id=f"barrister-{case_id}-cross-analysis",
                max_tokens=16384,
                timeout_seconds=300,
                task_type="report_generation",
            )
            cross_analysis = _strip_report_placeholders(cross_analysis)
            cross_analysis = re.sub(r"\n{3,}", "\n\n", cross_analysis).strip()
            if cross_analysis.startswith("## Report-to-Report Cross-Analysis"):
                #  — Insert before Sentencing Comparison, not at the end
                # This ensures cross-analysis isn't eaten by the strategy expansion regex
                if "## Sentencing Comparison and Relief Pathways" in response:
                    response = response.replace(
                        "## Sentencing Comparison and Relief Pathways",
                        cross_analysis.rstrip() + "\n\n## Sentencing Comparison and Relief Pathways",
                        1,
                    )
                else:
                    response = response.rstrip() + "\n\n" + cross_analysis
        except Exception as exc:
            logger.warning(f"Barrister cross-analysis expansion skipped for {case_id}: {exc}")

    # Strategy expansion — always run to deepen strategy sections
    if "## Proposed Submissions and Hearing Strategy" in response:
        strategy_expansion_prompt = f"""Rewrite only the following sections of the Barrister Brief below, keeping the same headings and making them substantially more detailed:

## Proposed Submissions and Hearing Strategy
## Conference Questions, Filing Priorities and Risks
## Final Appellate Research Briefing Note

Requirements:
- Minimum target length for this rewritten block alone: 30000 characters.
- Expand the oral and written submissions structure greatly.
- Include issue sequencing, fallback positions, framing choices, evidentiary use, likely resistance points, answer lines, and conference questions for counsel.
- The rewritten material must read like a serious barrister working brief, not a summary.
- Avoid repeating the same sentence structure or generic observations.

SOURCE REPORTS
{expansion_source_text}

CURRENT BARRISTER BRIEF
{response}
"""
        try:
            rewritten_strategy = await call_llm_with_fallback(
                system_prompt,
                strategy_expansion_prompt,
                session_id=f"barrister-{case_id}-strategy-expand",
                max_tokens=16384,
                timeout_seconds=300,
                task_type="report_generation",
            )
            rewritten_strategy = _strip_report_placeholders(rewritten_strategy)
            rewritten_strategy = re.sub(r"\n{3,}", "\n\n", rewritten_strategy).strip()
            if rewritten_strategy.startswith("## Proposed Submissions and Hearing Strategy"):
                #  — Regex stops at Attachment A/B, Report-to-Report, or Document and Evidence.
                # Old regex ([\s\S]*$) ate cross-analysis sections that were appended after strategy.
                response = re.sub(
                    r"## Proposed Submissions and Hearing Strategy\n[\s\S]*?(?=\n## (?:Attachment [AB]|Report-to-Report|Document and Evidence)|$)",
                    rewritten_strategy + "\n\n",
                    response,
                    count=1,
                )
        except Exception as exc:
            logger.warning(f"Barrister strategy expansion skipped for {case_id}: {exc}")

    try:
        comparison_tables_prompt = f"""Produce only the following markdown blocks, in this exact order, with no introduction or conclusion:

### Evidentiary Pressure Points Table
Create a markdown table with columns: Issue | Supporting Material | Why it matters on appeal | Vulnerability in the prosecution case

### Comparative Authorities Table
Create a markdown table with columns: Authority | Principle | Relevance to this case | Strategic use in submissions

### Sentencing Comparison Table
Create a markdown table with columns: Comparator | Key facts | Sentence outcome | Relevance to this appeal

### Relief Pathways Matrix
Create a markdown table with columns: Relief pathway | Legal basis | Best supporting features | Main risk or limitation

Requirements:
- Use all 3 source reports and the current barrister brief.
- Make the rows detailed and case-specific.
- Do not repeat the main narrative prose.
- Output only the 4 titled blocks above.

SOURCE REPORTS
{expansion_source_text}

CURRENT BARRISTER BRIEF
{response}
"""
        comparison_tables = await call_llm_with_fallback(
            system_prompt,
            comparison_tables_prompt,
            session_id=f"barrister-{case_id}-comparison-tables",
            max_tokens=16384,
            timeout_seconds=300,
            task_type="report_generation",
        )
        comparison_tables = _strip_report_placeholders(comparison_tables)
        comparison_tables = re.sub(r"\n{3,}", "\n\n", comparison_tables).strip()

        evidence_table_match = re.search(
            r"(### Evidentiary Pressure Points Table[\s\S]*?)(?=\n### Comparative Authorities Table|$)",
            comparison_tables,
        )
        authorities_table_match = re.search(
            r"(### Comparative Authorities Table[\s\S]*?)(?=\n### Sentencing Comparison Table|$)",
            comparison_tables,
        )
        sentencing_table_match = re.search(
            r"(### Sentencing Comparison Table[\s\S]*?)(?=\n### Relief Pathways Matrix|$)",
            comparison_tables,
        )
        relief_table_match = re.search(r"(### Relief Pathways Matrix[\s\S]*)$", comparison_tables)

        if evidence_table_match and "### Evidentiary Pressure Points Table" not in response:
            response = re.sub(
                r"(## Evidentiary Tensions and Appeal Pressure Points\n[\s\S]*?)(?=\n## Grounds of Merit)",
                lambda match: match.group(1).rstrip() + "\n\n" + evidence_table_match.group(1).strip() + "\n\n",
                response,
                count=1,
            )

        if authorities_table_match and "### Comparative Authorities Table" not in response:
            response = re.sub(
                r"(## Authorities and Comparative Cases\n[\s\S]*?)(?=\n## Sentencing Comparison and Relief Pathways)",
                lambda match: match.group(1).rstrip() + "\n\n" + authorities_table_match.group(1).strip() + "\n\n",
                response,
                count=1,
            )

        sentencing_blocks = []
        if sentencing_table_match and "### Sentencing Comparison Table" not in response:
            sentencing_blocks.append(sentencing_table_match.group(1).strip())
        if relief_table_match and "### Relief Pathways Matrix" not in response:
            sentencing_blocks.append(relief_table_match.group(1).strip())
        if sentencing_blocks:
            response = re.sub(
                r"(## Sentencing Comparison and Relief Pathways\n[\s\S]*?)(?=\n## Proposed Submissions and Hearing Strategy)",
                lambda match: match.group(1).rstrip() + "\n\n" + "\n\n".join(sentencing_blocks) + "\n\n",
                response,
                count=1,
            )
    except Exception as exc:
        logger.warning(f"Barrister comparison table enrichment skipped for {case_id}: {exc}")

    if grounds:
        try:
            issue_matrix_prompt = f"""Produce only the following attachment, with no introduction or conclusion before it:

## Attachment A — Barrister Issue Matrix

Requirements:
- This must appear as a barrister attachment at the end of the report.
- Use a markdown table with these columns exactly: Ground | Key facts | Main authorities | Risk level | Likely prosecution response | Oral submission angle.
- One row per ground from the mandatory ground list.
- Keep each cell specific, practical, and counsel-facing.
- Do not use generic filler.

MANDATORY GROUND LIST
{grounds_heading_text}

STRUCTURED GROUNDS
{grounds_text}

SOURCE REPORTS
{expansion_source_text}

CURRENT BARRISTER BRIEF
{response}
"""
            issue_matrix = await call_llm_with_fallback(
                system_prompt,
                issue_matrix_prompt,
                session_id=f"barrister-{case_id}-issue-matrix",
                max_tokens=16384,
                timeout_seconds=300,
                task_type="report_generation",
            )
            issue_matrix = _strip_report_placeholders(issue_matrix)
            issue_matrix = re.sub(r"\n{3,}", "\n\n", issue_matrix).strip()
            if issue_matrix.startswith("## Attachment A — Barrister Issue Matrix"):
                response = response.rstrip() + "\n\n" + issue_matrix
        except Exception as exc:
            logger.warning(f"Barrister issue matrix skipped for {case_id}: {exc}")

    # ── Attachment B — Counsel Conference Preparation ──
    if grounds:
        try:
            conference_prep_prompt = f"""Produce only the following attachment, with no introduction or conclusion before it:

## Attachment B — Counsel Conference Preparation

This attachment is designed for the instructing solicitor to use in preparation for the first barrister conference. It must be practical, specific to THIS case, and counsel-facing.

### B.1 — Key Questions for Conference

Produce a numbered list of 10-15 specific questions that counsel should address during the conference. These must be case-specific (not generic). Group them under sub-headings:
- **Factual Clarification** — questions about facts that are ambiguous, contested, or missing from the materials
- **Strategic Decisions** — questions requiring counsel's judgement on which grounds to advance, abandon, or reframe
- **Evidentiary Gaps** — questions about what additional evidence, affidavits, or expert reports are needed
- **Procedural Matters** — questions about filing deadlines, extension applications, bail, and hearing logistics

### B.2 — Identified Weak Points

Produce a markdown table with these columns: Weak Point | Ground Affected | Risk to Appeal | Suggested Mitigation. List every identified vulnerability in the appellant's case. Be honest and forensic — counsel needs to know where the case is vulnerable BEFORE the prosecution identifies it.

### B.3 — Likely Prosecution Responses

For each ground of appeal, write a paragraph (150+ words) describing the most likely Crown response. Reference specific evidence the Crown will rely on, authorities the Crown will cite, and the strongest version of the respondent's argument. This is essential for counsel to prepare replies.

### B.4 — Document References and Outstanding Materials

Produce a checklist table with columns: Document | Status | Priority | Action Required. List every document referenced in the case materials, note whether it has been obtained and reviewed, and identify any outstanding materials that must be sourced before the hearing (e.g., sentencing remarks, psychiatric reports, police briefs, CCTV, forensic evidence).

### B.5 — Conference Agenda (Suggested)

Draft a structured conference agenda with time estimates, covering: ground-by-ground review, strategic decisions, evidence preparation, witness considerations, filing timeline, and costs discussion.

MANDATORY GROUND LIST
{grounds_heading_text}

STRUCTURED GROUNDS
{grounds_text}

SOURCE REPORTS
{expansion_source_text}

CASE PROFILE
{case_profile}

DOCUMENT INVENTORY
{documents_text}

CURRENT BARRISTER BRIEF
{response[:8000]}
"""
            conference_prep = await call_llm_with_fallback(
                system_prompt,
                conference_prep_prompt,
                session_id=f"barrister-{case_id}-conference-prep",
                max_tokens=16384,
                timeout_seconds=300,
                task_type="report_generation",
            )
            conference_prep = _strip_report_placeholders(conference_prep)
            conference_prep = re.sub(r"\n{3,}", "\n\n", conference_prep).strip()
            if "Attachment B" in conference_prep and "Conference" in conference_prep:
                response = response.rstrip() + "\n\n" + conference_prep
                logger.info(f"Attachment B — Counsel Conference Prep appended for {case_id}")
        except Exception as exc:
            logger.warning(f"Counsel conference prep skipped for {case_id}: {exc}")

    #  — Final quality validation pass: expand any remaining thin sections
    final_min_chars = {
        "## Counsel Synthesis": 1500,
        "## Executive Overview for Counsel": 5000,
        "## Source Report Synthesis": 5000,
        "## Case Background and Procedural History": 4000,
        "## Conviction, Offence and Sentence Analysis": 4000,
        "## Evidentiary Tensions and Appeal Pressure Points": 5000,
        "## Grounds of Merit": 20000,
        "## Statutory Framework and Governing Tests": 4000,
        "## Authorities and Comparative Cases": 4000,
        "## Sentencing Comparison and Relief Pathways": 5000,
        "## Proposed Submissions and Hearing Strategy": 4000,
        "## Conference Questions, Filing Priorities and Risks": 3000,
        "## Final Appellate Research Briefing Note": 3000,
    }
    final_source = _build_barrister_group_source_text(
        source_reports,
        {"quick_summary": 8000, "full_detailed": 20000, "extensive_log": 28000},
    )
    for heading, min_c in final_min_chars.items():
        section_match = re.search(
            rf"({re.escape(heading)}\n[\s\S]*?)(?=\n## |\Z)",
            response,
        )
        if section_match and len(section_match.group(1)) < min_c:
            try:
                current_section = section_match.group(1)
                final_expand_prompt = f"""Rewrite and substantially expand the following section. Output ONLY this one section with its heading.

{current_section}

Requirements:
- Keep ALL existing content and ADD significantly more depth, factual detail, legal reasoning, and practical counsel advice.
- Minimum target: {min_c} characters.
- Dense, counsel-facing, Australian English, strict third-person.
- Use flowing paragraphs with concrete factual anchors, not generic observations.

SOURCE REPORTS
{final_source}
"""
                expanded = await call_llm_with_fallback(
                    system_prompt, final_expand_prompt,
                    session_id=f"barrister-{case_id}-final-{heading[3:15].lower().replace(' ','-')}",
                    max_tokens=16384, timeout_seconds=300, task_type="report_generation",
                )
                expanded = _strip_report_placeholders(expanded)
                expanded = re.sub(r"\n{3,}", "\n\n", expanded).strip()
                if expanded.startswith(heading) and len(expanded) > len(current_section):
                    response = response.replace(current_section, expanded, 1)
                    logger.info(f"Final QA expanded: {heading} ({len(current_section)} → {len(expanded)} chars)")
            except Exception as exc:
                logger.warning(f"Final QA expansion skipped for {heading}: {exc}")

    response = _strip_report_placeholders(response)
    response = _normalise_barrister_table_titles(response)
    response = _dedupe_barrister_ground_subsections(response)

    #  — Strip rogue H2 sections not in the expected structure
    expected_h2s = {
        "## Counsel Synthesis",
        "## Executive Overview for Counsel",
        "## Source Report Synthesis",
        "## Case Background and Procedural History",
        "## Conviction, Offence and Sentence Analysis",
        "## Evidentiary Tensions and Appeal Pressure Points",
        "## Grounds of Merit",
        "## Statutory Framework and Governing Tests",
        "## Authorities and Comparative Cases",
        "## Report-to-Report Cross-Analysis",
        "## Document and Evidence Deployment for Counsel",
        "## Sentencing Comparison and Relief Pathways",
        "## Proposed Submissions and Hearing Strategy",
        "## Conference Questions, Filing Priorities and Risks",
        "## Conference Questions, Filing Priorities, and Risks",
        "## Final Appellate Research Briefing Note",
        "## Attachment A — Barrister Issue Matrix",
        "## Attachment A - Barrister Issue Matrix",
        "## Attachment B — Counsel Conference Preparation",
        "## Attachment B - Counsel Conference Preparation",
    }
    cleaned_lines = []
    skip_section = False
    for line in response.split("\n"):
        if line.startswith("## "):
            if line.strip() in expected_h2s:
                skip_section = False
                cleaned_lines.append(line)
            else:
                skip_section = True
                logger.info(f"Stripped rogue section: {line.strip()}")
        elif skip_section and not line.startswith("## "):
            continue
        else:
            cleaned_lines.append(line)
    response = "\n".join(cleaned_lines)

    response = re.sub(r"\n{3,}", "\n\n", response).strip()

    #  — Runtime forensic language enforcement: rewrites any
    # "determined that / found that / concluded that" characterisation language
    # that slipped through the prompt, and enforces all other forensic appellate
    # language rules defined in enforce_forensic_language (offence_helpers.py).
    response = enforce_forensic_language(response)

    return {
        "analysis": response,
        "case_data": case,
        "document_count": len(documents),
        "event_count": len(timeline),
        "grounds_of_merit": grounds,
        "source_reports": [
            {
                "report_id": report.get("report_id"),
                "report_type": report.get("report_type"),
                "title": report.get("title"),
                "generated_at": report.get("generated_at"),
            }
            for report in source_reports
        ],
        "source_signature": _build_barrister_source_signature(source_reports),
        "metadata": ReportMetadata(
            documents_analyzed=len(documents),
            timeline_events_analyzed=len(timeline),
            grounds_considered=len(grounds),
            verification_status="draft",
            confidence_note="AI-generated barrister brief requiring legal review",
        ).model_dump(),
    }


async def _run_barrister_report_generation(report_id: str, case_id: str, user_id: str):
    """Background task for barrister brief generation — HARDENED with metadata."""
    try:
        # ── Soft metadata validation (warns but does not block) ──
        from services.case_validation import validate_case_metadata, log_metadata_warnings, strip_hallucinated_citations
        case_for_val = await db.cases.find_one({"case_id": case_id, "user_id": user_id}, {"_id": 0})
        if case_for_val:
            meta_val = validate_case_metadata(case_for_val)
            log_metadata_warnings(case_id, meta_val, "barrister_view")

        analysis_result = await generate_barrister_brief(case_id, user_id, report_id=report_id)

        # ── Citation post-processing: strip hallucinated citations from Barrister output ──
        clean_analysis = strip_hallucinated_citations(analysis_result.get("analysis", ""))
        # Normalise markdown BEFORE storing — guarantees every heading, bullet
        # and table has proper blank-line spacing across all export surfaces.
        from services.md_normaliser import normalise_markdown
        clean_analysis = normalise_markdown(clean_analysis)

        await db.reports.update_one(
            {"report_id": report_id},
            {
                "$set": {
                    "status": "completed",
                    "title": "Barrister Brief",
                    "content": {
                        "analysis": clean_analysis,
                        "case_title": (analysis_result.get("case_data") or {}).get("title", ""),
                        "defendant": (analysis_result.get("case_data") or {}).get("defendant_name", ""),
                        "document_count": analysis_result.get("document_count", 0),
                        "event_count": analysis_result.get("event_count", 0),
                        "source_signature": analysis_result.get("source_signature", ""),
                        "source_reports": analysis_result.get("source_reports", []),
                        "aggressive_mode": False,
                        "partial_sections": [],
                        "partial_stage": None,
                        "partial_analysis": "",
                    },
                    "grounds_of_merit": analysis_result["grounds_of_merit"],
                    "metadata": analysis_result.get("metadata"),
                    "source_mode": "ai_generated",
                    "verification_status": "draft",
                    "error": None,
                    "technical_error": None,
                }
            },
        )
        logger.info(f"Barrister brief {report_id} generated successfully")
    except Exception as exc:
        logger.error(f"Barrister brief {report_id} generation failed: {exc}")
        friendly_error = "Barrister brief generation was interrupted by a temporary AI service error. Please generate again."
        #  — Restore backup on failure
        backup_doc = await db.reports.find_one(
            {"report_id": report_id},
            {"_id": 0, "content.backup_analysis": 1}
        )
        backup = (backup_doc or {}).get("content", {}).get("backup_analysis", "")
        if backup and len(backup) > 5000:
            await db.reports.update_one(
                {"report_id": report_id},
                {"$set": {
                    "status": "completed",
                    "error": None,
                    "content.analysis": backup,
                },
                "$unset": {"content.backup_analysis": 1}}
            )
            logger.info(f"Barrister {report_id} generation failed but restored from backup ({len(backup)} chars)")
        else:
            await db.reports.update_one(
                {"report_id": report_id},
                {"$set": {"status": "failed", "error": friendly_error, "technical_error": str(exc)}},
            )

