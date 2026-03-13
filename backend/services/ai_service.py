# DO NOT UNDO — ai_service service. All logic in this file is approved and must be preserved.
"""
Criminal Appeal AI - AI Services Module
Encapsulates all AI/LLM operations for report generation, grounds analysis, etc.
"""
import os
import uuid
import re
import asyncio
from datetime import datetime, timezone
from typing import Optional
import logging

logger = logging.getLogger(__name__)


async def call_llm_with_retry(
    api_key: str,
    system_prompt: str,
    user_prompt: str,
    session_prefix: str,
    max_retries: int = 4
) -> Optional[str]:
    """Call LLM with exponential backoff retry logic"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    response = None
    last_error = None
    
    for attempt in range(max_retries):
        try:
            chat = LlmChat(
                api_key=api_key,
                session_id=f"{session_prefix}_{uuid.uuid4().hex[:8]}",
                system_message=system_prompt
            ).with_model("openai", "gpt-4o")
            
            response = await chat.send_message(UserMessage(text=user_prompt))
            return response
        except Exception as e:
            last_error = e
            logger.warning(f"LLM call attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(3 * (2 ** attempt))
    
    logger.error(f"All LLM call attempts failed: {last_error}")
    raise Exception(f"AI service failed after {max_retries} retries: {str(last_error)}")


def extract_law_sections(text: str) -> list:
    """Extract law section references from AI response text"""
    law_sections = []
    section_patterns = re.findall(r'[sS]\.?\s*(\d+[A-Za-z]?)\s+([A-Za-z\s]+(?:Act|Code))\s*(?:\d{4})?', text)
    for section_num, act_name in section_patterns[:10]:
        law_sections.append({
            "section": section_num,
            "act": act_name.strip(),
            "jurisdiction": "NSW" if "NSW" in act_name or "1900" in text else "Federal"
        })
    return law_sections


def extract_case_citations(text: str) -> list:
    """Extract case citations from AI response text"""
    similar_cases = []
    case_patterns = re.findall(r'([A-Z][a-z]+(?:\s+v\s+)[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', text)
    for case_name in list(set(case_patterns))[:5]:
        similar_cases.append({
            "case_name": case_name,
            "year": "",
            "citation": ""
        })
    return similar_cases


def build_case_context(case: dict, documents: list, timeline: list = None, notes: list = None, grounds: list = None, report_type: str = "full") -> str:
    """Build comprehensive context string from case data for AI analysis"""
    max_chars = 2000 if report_type == "quick_summary" else 3000
    
    context = f"""
=== CASE INFORMATION ===
Title: {case.get('title', 'N/A')}
Defendant: {case.get('defendant_name', 'N/A')}
Case Number: {case.get('case_number', 'N/A')}
Court: {case.get('court', 'N/A')}
Judge: {case.get('judge', 'N/A')}
Summary: {case.get('summary', 'N/A')}

"""
    
    if documents:
        context += f"=== CASE DOCUMENTS ({len(documents)} files) ===\n"
        for doc in documents:
            context += f"\n--- DOCUMENT: {doc.get('filename')} [{doc.get('category', 'other')}] ---\n"
            if doc.get('description'):
                context += f"Description: {doc.get('description')}\n"
            content = doc.get('content_text', '')
            if content:
                context += f"CONTENT:\n{content[:max_chars]}\n"
                if len(content) > max_chars:
                    context += f"[... {len(content) - max_chars} more characters ...]\n"
            else:
                context += "CONTENT: [No text extracted]\n"
    else:
        context += "=== NO DOCUMENTS UPLOADED ===\n"
    
    if timeline:
        context += f"\n=== TIMELINE OF EVENTS ({len(timeline)} events) ===\n"
        for event in timeline:
            context += f"- {event.get('event_date', 'Unknown')}: [{event.get('event_type')}] {event.get('title')}\n"
            if event.get('description'):
                context += f"  Details: {event.get('description')}\n"
    
    if notes:
        context += f"\n=== LEGAL NOTES ({len(notes)} notes) ===\n"
        for note in notes:
            context += f"- [{note.get('category')}] {note.get('title')}: {note.get('content', '')[:500]}\n"
    
    if grounds:
        context += f"\n=== IDENTIFIED GROUNDS OF MERIT ({len(grounds)} grounds) ===\n"
        for g in grounds:
            context += f"- [{g.get('ground_type')}] {g.get('title')} (Strength: {g.get('strength')})\n"
            context += f"  {g.get('description', '')[:300]}\n"
    
    return context


# Ground types for NSW/Australian murder appeals
GROUND_TYPES = {
    "procedural_error": "Procedural Error",
    "fresh_evidence": "Fresh Evidence",
    "miscarriage_of_justice": "Miscarriage of Justice",
    "sentencing_error": "Sentencing Error",
    "judicial_error": "Judicial Error",
    "ineffective_counsel": "Ineffective Counsel",
    "other": "Other"
}

# Event categories for timeline
EVENT_CATEGORIES = {
    "incident": "Incident/Crime",
    "arrest": "Arrest",
    "investigation": "Investigation",
    "court_appearance": "Court Appearance",
    "trial": "Trial",
    "evidence": "Evidence",
    "witness": "Witness",
    "verdict": "Verdict/Sentence",
    "appeal": "Appeal",
    "other": "Other"
}
