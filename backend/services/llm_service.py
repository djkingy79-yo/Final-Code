"""
Criminal Appeal AI - LLM Service
Reusable LLM call with model fallback, structured metadata, and legal safety controls.

Key improvements over raw wrapper:
  - Returns structured result dict (not just raw text)
  - Task-type aware model selection and token limits
  - Anti-hallucination safety instructions appended to legal tasks
  - Provider/model metadata for audit trail
"""
import os
import asyncio
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

# Task-type configurations: preferred model, max tokens, timeout
TASK_CONFIGS = {
    "grounds_identification": {"max_tokens": 12000, "timeout": 150},
    "ground_investigation": {"max_tokens": 8000, "timeout": 120},
    "report_generation": {"max_tokens": 16384, "timeout": 180},
    "timeline_extraction": {"max_tokens": 6000, "timeout": 90},
    "contradiction_scan": {"max_tokens": 6000, "timeout": 90},
    "deadline_summary": {"max_tokens": 4000, "timeout": 60},
    "case_comparison": {"max_tokens": 6000, "timeout": 90},
    "note_generation": {"max_tokens": 4000, "timeout": 60},
    "default": {"max_tokens": 16384, "timeout": 120},
}

# Anti-hallucination controls appended to all legal analysis tasks
LEGAL_SAFETY_SUFFIX = """

CRITICAL SAFETY INSTRUCTIONS (always follow):
- Do NOT invent case names, citations, or statutory references not supplied or well-established.
- Do NOT state that an appeal will succeed or is likely to succeed.
- Distinguish extracted fact from possible issue from legal inference from missing material.
- Where evidence is incomplete, say so expressly.
- Use conditional language for legal conclusions.
- Every assertion must be traceable to supplied documents or flagged as inference."""


LEGAL_TASK_TYPES = {
    "grounds_identification", "ground_investigation", "report_generation",
    "contradiction_scan", "case_comparison", "timeline_extraction",
}


async def call_llm_with_fallback(
    system_prompt: str,
    user_prompt: str,
    session_id: str = "default",
    max_tokens: int = 16384,
    timeout_seconds: int = 120,
    task_type: Optional[str] = None,
) -> str:
    """
    Call LLM with model fallback. Returns raw text for backwards compatibility.
    For structured metadata, use call_llm_structured() instead.
    """
    result = await call_llm_structured(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        session_id=session_id,
        max_tokens=max_tokens,
        timeout_seconds=timeout_seconds,
        task_type=task_type,
    )
    return result["content"]


async def call_llm_structured(
    system_prompt: str,
    user_prompt: str,
    session_id: str = "default",
    max_tokens: int = 16384,
    timeout_seconds: int = 120,
    task_type: Optional[str] = None,
) -> dict:
    """
    Call LLM with model fallback and return structured result.

    Returns:
        {
            "content": str,
            "provider": str,
            "model": str,
            "attempt": int,
            "fallback_used": bool,
            "latency_ms": int,
            "task_type": str | None,
            "warnings": list[str],
        }
    """
    from emergentintegrations.llm.chat import LlmChat, UserMessage

    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise Exception("AI service not configured — EMERGENT_LLM_KEY missing")

    # Apply task-specific config overrides
    config = TASK_CONFIGS.get(task_type, TASK_CONFIGS["default"])
    effective_max_tokens = min(max_tokens, config["max_tokens"])
    effective_timeout = min(timeout_seconds, config["timeout"])

    # Append legal safety controls for legal tasks
    effective_system_prompt = system_prompt
    if task_type and task_type in LEGAL_TASK_TYPES:
        effective_system_prompt = system_prompt + LEGAL_SAFETY_SUFFIX

    models = [
        ("openai", "gpt-4o"),
        ("openai", "gpt-4o"),
        ("anthropic", "claude-sonnet-4-20250514"),
        ("openai", "gpt-4o-mini"),
    ]

    last_err = None
    warnings = []
    start_time = time.time()

    for idx, (provider, model_name) in enumerate(models):
        attempt_start = time.time()
        try:
            chat = (
                LlmChat(api_key=api_key, session_id=session_id, system_message=effective_system_prompt)
                .with_model(provider, model_name)
                .with_params(max_tokens=effective_max_tokens)
            )
            result = await asyncio.wait_for(
                chat.send_message(UserMessage(text=user_prompt)),
                timeout=effective_timeout,
            )

            # Validate response quality
            if result and len(result.strip()) > 50 and "I'm sorry" not in result[:80]:
                latency = int((time.time() - start_time) * 1000)
                fallback_used = idx > 0

                if fallback_used:
                    warnings.append(f"Primary model unavailable; fell back to {provider}/{model_name} on attempt {idx + 1}")

                logger.info(f"LLM success ({session_id}) with {provider}/{model_name} on attempt {idx+1} ({latency}ms)")

                return {
                    "content": result,
                    "provider": provider,
                    "model": model_name,
                    "attempt": idx + 1,
                    "fallback_used": fallback_used,
                    "latency_ms": latency,
                    "task_type": task_type,
                    "warnings": warnings,
                }

            last_err = f"Short/refused response from {provider}/{model_name}"
            warnings.append(last_err)

        except asyncio.TimeoutError:
            last_err = f"Timeout with {provider}/{model_name} after {effective_timeout}s"
            warnings.append(last_err)
        except Exception as e:
            last_err = str(e)[:200]
            warnings.append(f"Error with {provider}/{model_name}: {last_err}")

        logger.warning(f"LLM attempt {idx+1} ({provider}/{model_name}) for {session_id}: {last_err}")
        await asyncio.sleep(2 + idx)

    raise Exception(f"All LLM attempts failed: {last_err}")
