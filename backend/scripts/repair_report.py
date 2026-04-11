"""
Repair missing/thin sections in a completed report.
Runs targeted LLM calls for ONLY the gaps, then stitches content in-place.
Much faster than full regeneration (~2-3 min vs 20 min).
"""
import asyncio
import logging
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv  # noqa: E402
from motor.motor_asyncio import AsyncIOMotorClient  # noqa: E402
from services.llm_service import call_llm_with_fallback  # noqa: E402

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("repair_report")

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "test_database")


def split_sections(text):
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


def get_section_num(heading):
    match = re.match(r"##\s+(\d+)\.", heading)
    return int(match.group(1)) if match else 0


async def repair_report(report_id: str):
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    report = await db.reports.find_one({"report_id": report_id}, {"_id": 0})
    if not report:
        logger.error(f"Report {report_id} not found")
        return

    analysis = report.get("content", {}).get("analysis", "")
    case_id = report.get("case_id")
    report_type = report.get("report_type")

    logger.info(f"Repairing {report_id} ({report_type}): {len(analysis)} chars")

    # Get case context
    case = await db.cases.find_one({"case_id": case_id}, {"_id": 0})
    documents = await db.documents.find({"case_id": case_id}, {"_id": 0}).to_list(100)
    grounds = await db.grounds_of_merit.find({"case_id": case_id}, {"_id": 0}).to_list(50)

    grounds_enumerated = "\n".join([
        f"{i+1}. {g.get('title', 'Unknown')} ({g.get('ground_type', 'general')})"
        for i, g in enumerate(grounds)
    ])
    doc_list = "\n".join([
        f"- {d.get('original_filename', d.get('filename', 'Unknown'))}"
        for d in documents[:20]
    ])
    case_title = case.get("title", "Unknown")
    state = case.get("state", "NSW")
    sentence = case.get("sentence", "Not specified")

    sections = split_sections(analysis)

    # Define expected sections for extensive_log
    expected = {
        3: "DOCUMENT EVIDENCE DIGEST",
        9: "PRECEDENT OUTCOME MATRIX",
        11: "HOW TO ARGUE EACH TOP GROUND — DETAILED STRATEGY",
    }

    repairs_made = 0

    for num, name in sorted(expected.items()):
        # Check if section exists AND has content
        existing_content = ""
        for h, c in sections:
            if h and get_section_num(h) == num:
                existing_content = c
                break

        if len(existing_content.strip()) > 500:
            logger.info(f"Section {num} ({name}) OK: {len(existing_content)} chars")
            continue

        logger.warning(f"Section {num} ({name}) MISSING or THIN ({len(existing_content)} chars). Generating.")

        # Build a targeted prompt
        if num == 3:
            section_prompt = f"""Generate Section 3 of an Extensive Legal Analysis Report for the case: {case_title} ({state}).
Sentence: {sentence}

DOCUMENTS ({len(documents)}):
{doc_list}

## 3. DOCUMENT EVIDENCE DIGEST (1500+ words)
For EACH of the {len(documents)} uploaded documents, write 2-3 FULL PARAGRAPHS analysing:
- Document title and date
- Key extracts (QUOTE directly from the document content where possible)
- Reliability and credibility assessment
- Probative value — what it proves or disproves
- Which specific grounds this document supports
- Rating: Critical / Important / Supporting / Peripheral

If there are {len(documents)} documents, write {len(documents)*2}-{len(documents)*3} paragraphs.
Use Australian English. STRICT third-person — NEVER "you", "your", "we", "us", "our".
Start with exactly: ## 3. DOCUMENT EVIDENCE DIGEST
Do NOT include any other section headings."""

        elif num == 9:
            section_prompt = f"""Generate Section 9 of an Extensive Legal Analysis Report for the case: {case_title} ({state}).
Sentence: {sentence}

GROUNDS:
{grounds_enumerated}

## 9. PRECEDENT OUTCOME MATRIX (12+ CASES)
For each of 12+ real comparable cases, write a FULL PARAGRAPH (not just a table row):
- Full citation (real Australian case law)
- Factual similarity to THIS matter (be specific — offence type, relationship, circumstances)
- Hearing outcome (appeal result, sentence change)
- Extracted legal principle
- How this principle applies to the current case (3-4 sentences)

Focus on NSW murder/manslaughter appeals, particularly cases involving domestic violence, mental illness defences, and sentencing manifest excess.
Use Australian English. STRICT third-person only.
Start with exactly: ## 9. PRECEDENT OUTCOME MATRIX
Do NOT include any other section headings."""

        elif num == 11:
            section_prompt = f"""Generate Section 11 of an Extensive Legal Analysis Report for the case: {case_title} ({state}).
Sentence: {sentence}

## 11. HOW TO ARGUE EACH TOP GROUND — DETAILED STRATEGY
MUST cover ALL {len(grounds)} grounds below. For EACH ground write 500+ words.

GROUNDS TO COVER:
{grounds_enumerated}

For each ground write as flowing paragraphs:
- **Lead Proposition**: The core argument in 2 powerful sentences
- **Supporting Authority Cluster**: Specific statute + 3-4 precedent cases with full citations and 2-3 sentences explaining each
- **Expected Crown Response**: 4-5 sentences predicting what the prosecution will argue
- **Rebuttal Strategy**: 4-5 sentences with specific counter-authorities
- **Fallback Position**: If the primary argument is rejected, what's the alternative? (3-4 sentences)
- **If Established**: What specific court order should be sought?

Use Australian English. STRICT third-person only.
Start with exactly: ## 11. HOW TO ARGUE EACH TOP GROUND — DETAILED STRATEGY
Do NOT include any other section headings."""

        else:
            continue

        try:
            system_prompt = "You are a senior Australian criminal appeals analyst generating a section of a legal report. Write substantive, case-specific analysis with real legal authorities. Do NOT invent or fabricate case citations, Act names, section numbers, or facts. Do NOT default to NSW legislation for non-NSW cases. Use forensic appellate language — it is arguable that, not declarative assertions. Use Australian English and third-person language only."
            
            result = await call_llm_with_fallback(
                system_prompt=system_prompt,
                user_prompt=section_prompt,
                session_id=f"repair_{report_id}_{num}",
                max_tokens=16384,
                timeout_seconds=300,
                task_type="report_generation",
            )

            if not result or len(result.strip()) < 500:
                logger.error(f"Section {num} repair returned too little content ({len(result or '')} chars)")
                continue

            # Clean up result
            cleaned = result.strip()
            if not cleaned.startswith("##"):
                cleaned = f"## {num}. {name}\n\n{cleaned}"

            # Find insertion point in the original analysis
            # Insert before the next higher-numbered section
            insert_before = None
            for h, _ in sections:
                if h:
                    h_num = get_section_num(h)
                    if h_num > num:
                        insert_before = h
                        break

            if existing_content.strip():
                # REPLACE existing thin content
                for h, c in sections:
                    if h and get_section_num(h) == num:
                        old_section = h + "\n" + c
                        analysis = analysis.replace(old_section, cleaned, 1)
                        break
            elif insert_before:
                # INSERT before the next section
                insert_idx = analysis.find(insert_before)
                if insert_idx > 0:
                    analysis = analysis[:insert_idx] + cleaned + "\n\n" + analysis[insert_idx:]
            else:
                # Append at the end
                analysis = analysis + "\n\n" + cleaned

            logger.info(f"Repaired section {num} ({name}): {len(cleaned)} chars")
            repairs_made += 1

            # Re-parse sections after modification
            sections = split_sections(analysis)

        except Exception as e:
            logger.error(f"Failed to repair section {num}: {e}")
            continue

    if repairs_made > 0:
        # Update the report in DB
        await db.reports.update_one(
            {"report_id": report_id},
            {"$set": {"content.analysis": analysis}}
        )
        logger.info(f"Report {report_id} updated with {repairs_made} repaired sections. New total: {len(analysis)} chars, ~{len(analysis.split())} words")
    else:
        logger.info(f"No repairs needed for {report_id}")

    # Show final section summary
    final_sections = split_sections(analysis)
    for h, c in final_sections:
        if h:
            print(f"  {h[:70]}: {len(c)} chars")

    client.close()


if __name__ == "__main__":
    report_id = sys.argv[1] if len(sys.argv) > 1 else "rpt_731f70dd5767"
    asyncio.run(repair_report(report_id))
