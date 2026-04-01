# DO NOT UNDO — llm_service module. All existing logic must be preserved.
"""
Criminal Appeal AI - LLM Service
Reusable LLM call with model fallback.

ADDITIVE HARDENING PATCH
"""
import os
import asyncio
import logging
import json
from typing import Optional, Callable, Any, Dict, Literal

logger = logging.getLogger(__name__)


# ============================================================================
# TASK TYPES
# ============================================================================

LLMTaskType = Literal[
    "general",
    "metadata_detection",
    "grounds_identification",
    "grounds_investigation",
    "timeline_extraction",
    "report_generation",
    "report_cleanup",
    "document_extraction",
    "issue_classification",
    "issue_verification",
]


# ============================================================================
# TASK CONFIGURATION
# ============================================================================

TASK_CONFIGS: dict[str, dict] = {
    "general": {
        "max_tokens": 16384,
        "timeout_seconds": 120,
        "require_json": False,
        "temperature": 0.2,
    },
    "metadata_detection": {
        "max_tokens": 4000,
        "timeout_seconds": 60,
        "require_json": True,
        "temperature": 0.1,
    },
    "grounds_identification": {
        "max_tokens": 12000,
        "timeout_seconds": 120,
        "require_json": True,
        "temperature": 0.15,
    },
    "grounds_investigation": {
        "max_tokens": 16384,
        "timeout_seconds": 120,
        "require_json": False,
        "temperature": 0.15,
    },
    "timeline_extraction": {
        "max_tokens": 8000,
        "timeout_seconds": 90,
        "require_json": True,
        "temperature": 0.1,
    },
    "report_generation": {
        "max_tokens": 16384,
        "timeout_seconds": 150,
        "require_json": False,
        "temperature": 0.2,
    },
    "report_cleanup": {
        "max_tokens": 8000,
        "timeout_seconds": 90,
        "require_json": False,
        "temperature": 0.1,
    },
    "document_extraction": {
        "max_tokens": 8000,
        "timeout_seconds": 90,
        "require_json": True,
        "temperature": 0.1,
    },
    "issue_classification": {
        "max_tokens": 12000,
        "timeout_seconds": 120,
        "require_json": True,
        "temperature": 0.15,
    },
    "issue_verification": {
        "max_tokens": 10000,
        "timeout_seconds": 120,
        "require_json": True,
        "temperature": 0.1,
    },
    "issue_argument": {
        "max_tokens": 9000,
        "timeout_seconds": 120,
        "require_json": True,
        "temperature": 0.15,
    },
    "submissions_draft": {
        "max_tokens": 12000,
        "timeout_seconds": 150,
        "require_json": True,
        "temperature": 0.15,
    },
}


# ============================================================================
# INTERNAL HELPERS
# ============================================================================

def _default_models_for_task(task_type: str):
    return [
        ("openai", "gpt-4o"),
        ("openai", "gpt-4o"),
        ("anthropic", "claude-sonnet-4-20250514"),
        ("openai", "gpt-4o-mini"),
    ]


def _looks_like_refusal(text: str) -> bool:
    if not text:
        return True
    head = text[:200].lower()
    refusal_markers = [
        "i'm sorry",
        "i cannot",
        "i can't",
        "i cannot assist",
        "i'm unable",
        "i am unable",
        "sorry, but",
    ]
    return any(marker in head for marker in refusal_markers)


def _extract_json_object(text: str) -> Optional[dict]:
    if not text:
        return None

    # First try direct parse
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    # Strip markdown code fences
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

    # Then try largest brace block
    try:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start:end + 1]
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
    except Exception:
        pass

    return None


def _json_instruction_suffix() -> str:
    return (
        "\n\nIMPORTANT:\n"
        "- Return ONLY valid JSON.\n"
        "- Do not include markdown code fences.\n"
        "- Do not include explanatory text before or after the JSON.\n"
    )


def _basic_text_validation(result: str) -> bool:
    if not result:
        return False
    if len(result.strip()) < 50:
        return False
    if _looks_like_refusal(result):
        return False
    return True


def _apply_task_guardrails(system_prompt: str, task_type: str, require_json: bool) -> str:
    """DO_NOT_UNDO — Report generation MUST NOT include 'cautious language' guardrail.
    That rule was stripping assertive legal analysis and making reports weak/generic."""
    # For report generation, the system prompt already contains comprehensive guardrails.
    # Adding conflicting "cautious language" rules undermines the report quality.
    if task_type == "report_generation":
        guardrails = (
            "\n\nSAFETY RULES:\n"
            "- Do not invent authorities, statutory provisions, or case citations.\n"
            "- If uncertain about a specific citation, say that verification is required.\n"
            "- Distinguish factual extraction from legal inference.\n"
        )
    else:
        guardrails = (
            "\n\nSAFETY / RELIABILITY RULES:\n"
            "- Do not invent authorities, statutory provisions, or case citations.\n"
            "- If uncertain, say that verification is required.\n"
            "- Distinguish factual extraction from legal inference.\n"
            "- Use cautious, conditional language for legal analysis.\n"
            "- Do not state that an appeal will succeed.\n"
        )

    if require_json:
        guardrails += (
            "- The output must be machine-parseable JSON only.\n"
        )

    return f"{system_prompt}{guardrails}"


# ============================================================================
# STRUCTURED RESPONSE LAYER
# ============================================================================

async def call_llm_structured(
    system_prompt: str,
    user_prompt: str,
    session_id: str = "default",
    *,
    task_type: LLMTaskType = "general",
    max_tokens: Optional[int] = None,
    timeout_seconds: Optional[int] = None,
    require_json: Optional[bool] = None,
    validation_fn: Optional[Callable[[Any], bool]] = None,
) -> Dict[str, Any]:
    from emergentintegrations.llm.chat import LlmChat, UserMessage

    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise Exception("AI service not configured — EMERGENT_LLM_KEY missing")

    config = TASK_CONFIGS.get(task_type, TASK_CONFIGS["general"])
    resolved_max_tokens = max_tokens if max_tokens is not None else config["max_tokens"]
    resolved_timeout = timeout_seconds if timeout_seconds is not None else config["timeout_seconds"]
    resolved_require_json = require_json if require_json is not None else config["require_json"]

    models = _default_models_for_task(task_type)
    last_err = None

    effective_system_prompt = _apply_task_guardrails(system_prompt, task_type, resolved_require_json)
    effective_user_prompt = user_prompt + (_json_instruction_suffix() if resolved_require_json else "")

    for idx, (provider, model_name) in enumerate(models):
        try:
            chat = (
                LlmChat(
                    api_key=api_key,
                    session_id=session_id,
                    system_message=effective_system_prompt
                )
                .with_model(provider, model_name)
                .with_params(max_tokens=resolved_max_tokens)
            )

            result = await asyncio.wait_for(
                chat.send_message(UserMessage(text=effective_user_prompt)),
                timeout=resolved_timeout
            )

            if not _basic_text_validation(result):
                last_err = f"Short/refused response from {provider}/{model_name}"
                logger.warning(f"LLM attempt {idx+1} ({provider}/{model_name}) for {session_id}: {last_err}")
                await asyncio.sleep(2 + idx)
                continue

            parsed_json = _extract_json_object(result) if resolved_require_json else None
            if resolved_require_json and parsed_json is None:
                last_err = f"JSON parse failed for {provider}/{model_name}"
                logger.warning(f"LLM attempt {idx+1} ({provider}/{model_name}) for {session_id}: {last_err}")
                await asyncio.sleep(2 + idx)
                continue

            validation_passed = True
            if validation_fn is not None:
                try:
                    validation_target = parsed_json if parsed_json is not None else result
                    validation_passed = bool(validation_fn(validation_target))
                except Exception as ve:
                    validation_passed = False
                    last_err = f"Validation function raised error: {str(ve)[:200]}"

            if not validation_passed:
                last_err = f"Validation failed for {provider}/{model_name}"
                logger.warning(f"LLM attempt {idx+1} ({provider}/{model_name}) for {session_id}: {last_err}")
                await asyncio.sleep(2 + idx)
                continue

            logger.info(f"LLM success ({session_id}) with {provider}/{model_name} on attempt {idx+1}")
            return {
                "ok": True,
                "content": result,
                "parsed_json": parsed_json,
                "provider": provider,
                "model": model_name,
                "attempt": idx + 1,
                "fallback_used": idx > 0,
                "task_type": task_type,
                "require_json": resolved_require_json,
                "validation_passed": validation_passed,
                "error": None,
            }

        except asyncio.TimeoutError:
            last_err = f"Timeout with {provider}/{model_name}"
        except Exception as e:
            last_err = str(e)[:200]

        logger.warning(f"LLM attempt {idx+1} ({provider}/{model_name}) for {session_id}: {last_err}")
        await asyncio.sleep(2 + idx)

    return {
        "ok": False,
        "content": "",
        "parsed_json": None,
        "provider": None,
        "model": None,
        "attempt": None,
        "fallback_used": True,
        "task_type": task_type,
        "require_json": resolved_require_json,
        "validation_passed": False,
        "error": last_err or "Unknown LLM failure",
    }


# ============================================================================
# BACKWARD-COMPATIBLE LEGACY FUNCTION
# ============================================================================

async def call_llm_with_fallback(
    system_prompt: str,
    user_prompt: str,
    session_id: str = "default",
    max_tokens: int = 16384,
    timeout_seconds: int = 120,
    task_type: str = None,
) -> str:
    """
    Backward-compatible legacy interface.
    Preserved so existing routers do not break.
    """
    response = await call_llm_structured(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        session_id=session_id,
        task_type=task_type or "general",
        max_tokens=max_tokens,
        timeout_seconds=timeout_seconds,
        require_json=False,
        validation_fn=None,
    )

    if response["ok"]:
        return response["content"]

    raise Exception(f"All LLM attempts failed: {response['error']}")


# ============================================================================
# CONVENIENCE WRAPPERS
# ============================================================================

async def call_llm_for_json(
    system_prompt: str,
    user_prompt: str,
    session_id: str = "default",
    *,
    task_type: LLMTaskType = "general",
    validation_fn: Optional[Callable[[dict], bool]] = None,
    max_tokens: Optional[int] = None,
    timeout_seconds: Optional[int] = None,
) -> dict:
    """
    Convenience wrapper for routes that need guaranteed JSON.
    Raises on failure to preserve existing route expectations.
    """
    response = await call_llm_structured(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        session_id=session_id,
        task_type=task_type,
        max_tokens=max_tokens,
        timeout_seconds=timeout_seconds,
        require_json=True,
        validation_fn=validation_fn,
    )

    if response["ok"] and response["parsed_json"] is not None:
        return response["parsed_json"]

    raise Exception(f"JSON LLM call failed: {response['error']}")


async def call_llm_for_report(
    system_prompt: str,
    user_prompt: str,
    session_id: str = "default",
    *,
    task_type: LLMTaskType = "report_generation",
    max_tokens: Optional[int] = None,
    timeout_seconds: Optional[int] = None,
) -> dict:
    """
    Report-focused wrapper returning metadata and content.
    """
    response = await call_llm_structured(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        session_id=session_id,
        task_type=task_type,
        max_tokens=max_tokens,
        timeout_seconds=timeout_seconds,
        require_json=False,
        validation_fn=None,
    )

    if not response["ok"]:
        raise Exception(f"Report LLM call failed: {response['error']}")

    return {
        "content": response["content"],
        "metadata": {
            "generated_by_model": response["model"],
            "fallback_used": response["fallback_used"],
            "verification_status": "draft",
            "confidence_note": "AI-generated output requiring legal review",
        }
    }
