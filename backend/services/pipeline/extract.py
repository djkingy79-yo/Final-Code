# DO NOT UNDO — staged extraction pipeline. Additive module.
from services.llm_service import call_llm_for_json
from services.pipeline_models import (
    DocumentExtract,
    ExtractedFact,
    ExtractedEvent,
    ExtractedFinding,
)


def _validate_document_extract(payload: dict) -> bool:
    return (
        isinstance(payload, dict)
        and isinstance(payload.get("facts"), list)
        and isinstance(payload.get("events"), list)
        and isinstance(payload.get("findings"), list)
    )


def _normalise_fact(item: dict) -> ExtractedFact:
    return ExtractedFact(
        type=str(item.get("type", "fact")),
        text=str(item.get("text", "")),
        quote=item.get("quote"),
        page_reference=item.get("page_reference"),
        confidence=item.get("confidence", "moderate"),
    )


def _normalise_event(item: dict) -> ExtractedEvent:
    return ExtractedEvent(
        title=str(item.get("title", "Untitled event")),
        event_date=item.get("event_date"),
        event_type=str(item.get("event_type", "event")),
        event_category=str(item.get("event_category", "general")),
        description=str(item.get("description", "")),
        quote=item.get("quote"),
        page_reference=item.get("page_reference"),
        significance=str(item.get("significance", "normal")),
    )


def _normalise_finding(item: dict) -> ExtractedFinding:
    return ExtractedFinding(
        type=str(item.get("type", "judicial_finding")),
        text=str(item.get("text", "")),
        quote=item.get("quote"),
        page_reference=item.get("page_reference"),
        confidence=item.get("confidence", "moderate"),
    )


async def extract_document_artifacts(case: dict, document: dict) -> DocumentExtract:
    content_text = (document.get("content_text") or "").strip()

    system_prompt = """Extract only what is explicitly supported by the document.
Return JSON only.
Do not classify appeal grounds.
Do not argue the case.
Do not infer beyond the text.

ANTI-HALLUCINATION — ABSOLUTE:
- Do NOT invent facts, dates, names, or events not in the document.
- Do NOT assume the jurisdiction is NSW or any other state unless the document explicitly states it.
- If a fact is ambiguous, mark confidence as "weak".
- Use Australian English spelling throughout (analyse, defence, offence, behaviour).
- Do NOT fabricate case citations, section numbers, or Act names."""

    user_prompt = f"""Extract structured material from this criminal case document.

CASE:
- Title: {case.get('title', 'Unknown')}
- Defendant: {case.get('defendant_name', 'Unknown')}
- State: {case.get('state', '') or 'UNSPECIFIED'}
- Offence Category: {case.get('offence_category', 'unknown')}

DOCUMENT:
- Filename: {document.get('filename', 'Unknown')}
- Category: {document.get('category', 'other')}

TEXT:
{content_text[:30000]}

Return ONLY valid JSON:
{{
  "facts": [
    {{
      "type": "sentence_detail|medical_fact|procedural_fact|evidence_fact|general_fact",
      "text": "short factual statement",
      "quote": "short supporting quote",
      "page_reference": "optional",
      "confidence": "strong|moderate|weak"
    }}
  ],
  "events": [
    {{
      "title": "short event title",
      "event_date": "ISO date if known, else null",
      "event_type": "incident|arrest|charge|hearing|application|ruling|trial|verdict|sentence|appeal|other",
      "event_category": "factual|procedural|medical|evidentiary|general",
      "description": "short description",
      "quote": "short supporting quote",
      "page_reference": "optional",
      "significance": "low|normal|important|critical"
    }}
  ],
  "findings": [
    {{
      "type": "judicial_finding|expert_finding|credibility_finding|general_finding",
      "text": "short finding",
      "quote": "short supporting quote",
      "page_reference": "optional",
      "confidence": "strong|moderate|weak"
    }}
  ]
}}"""

    parsed = await call_llm_for_json(
        system_prompt,
        user_prompt,
        session_id=f"extract_{document.get('document_id', 'doc')}",
        task_type="document_extraction",
        validation_fn=_validate_document_extract,
    )

    facts = [_normalise_fact(x) for x in parsed.get("facts", [])]
    events = [_normalise_event(x) for x in parsed.get("events", [])]
    findings = [_normalise_finding(x) for x in parsed.get("findings", [])]

    return DocumentExtract(
        case_id=case["case_id"],
        user_id=case["user_id"],
        document_id=document["document_id"],
        filename=document.get("filename", "Unknown"),
        document_category=document.get("category"),
        model_metadata={
            "task_type": "document_extraction",
            "verification_status": "draft",
        },
        facts=facts,
        events=events,
        findings=findings,
    )
