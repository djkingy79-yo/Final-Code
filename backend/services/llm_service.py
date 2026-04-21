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

# DO_NOT_UNDO — Direct OpenAI SDK is fully async (AsyncOpenAI.chat.completions.create
# is a coroutine). No ThreadPoolExecutor is required — the event loop is NOT
# blocked, unlike the previous emergentintegrations → litellm (sync) wrapper.
# Swapped 2026-04-21 per owner requirement to drop google-generativeai /
# google-genai / litellm / emergentintegrations transitive deps.
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# Module-level lazy singleton. Instantiated on first call (not at import time)
# so pytest / uvicorn reload don't fail when OPENAI_API_KEY isn't yet loaded.
_openai_client: Optional[AsyncOpenAI] = None


def _get_openai_client() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise Exception("AI service not configured — OPENAI_API_KEY is missing")
        _openai_client = AsyncOpenAI(api_key=api_key)
    return _openai_client


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
        "max_tokens": 8192,
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
    # DO_NOT_UNDO — Model diversity for resilience. Previously used Anthropic as
    # one of the fallbacks, but since moving to the user's OWN OpenAI API key
    # (no Anthropic key available), all slots must be OpenAI models. GPT-4o is
    # the primary; gpt-4o-mini is the cheaper fallback if gpt-4o is rate-limited
    # or momentarily unavailable. Multiple gpt-4o slots provide natural retry.
    return [
        ("openai", "gpt-4o"),
        ("openai", "gpt-4o"),
        ("openai", "gpt-4o-mini"),
        ("openai", "gpt-4o"),
        ("openai", "gpt-4o-mini"),
        ("openai", "gpt-4o"),
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
    """Extract JSON from LLM response — supports both objects and arrays."""
    if not text:
        return None

    # First try direct parse
    try:
        parsed = json.loads(text)
        if isinstance(parsed, (dict, list)):
            return parsed
    except Exception:
        pass

    # Strip markdown code fences
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, (dict, list)):
                return parsed
        except Exception:
            pass

    # Try largest bracket block (array)
    try:
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            candidate = text[start:end + 1]
            parsed = json.loads(candidate)
            if isinstance(parsed, list):
                return parsed
    except Exception:
        pass

    # Then try largest brace block (object)
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
    # Universal anti-hallucination and jurisdiction fidelity guardrails
    # applied to EVERY LLM call regardless of task type.
    universal_guardrails = (
        "\n\nUNIVERSAL ANTI-HALLUCINATION RULES (ABSOLUTE — APPLY TO ALL OUTPUT):\n"
        "- Do NOT invent or fabricate case names, citations, section numbers, Act names, judge names, dates, or penalty amounts.\n"
        "- If uncertain about a specific citation or section number, say that verification is required — do NOT guess.\n"
        "- Do NOT default to NSW legislation when the jurisdiction is unspecified or is a different state.\n"
        "- Distinguish factual extraction from legal inference.\n"
        "- Use Australian English spelling throughout (analyse, defence, offence, behaviour, honour, favour, centre, judgement).\n"
    )

    # For report generation, the system prompt already contains comprehensive guardrails.
    # Adding conflicting "cautious language" rules undermines the report quality.
    if task_type == "report_generation":
        guardrails = (
            universal_guardrails
            + "- If uncertain about a specific citation, say that verification is required.\n"
        )
    else:
        guardrails = (
            universal_guardrails
            + "- Use cautious, conditional forensic appellate language. ROTATE across at least 8 grammatically-varied phrases — never repeat the same stem within three consecutive sentences. Approved variations (use all, in rotation): \"it is arguable that\", \"it is contended that\", \"it is submitted that\", \"it is open to argument that\", \"there is a tenable argument that\", \"a question arises as to whether\", \"with respect, the [direction / finding / approach] is open to question\", \"the proper course, it is submitted, would have been\", \"it warrants consideration whether\", \"the material gives rise to an arguable basis that\", \"there is a reasonably arguable case that\", \"it may be contended that\".\n"
            + "- Do NOT state that an appeal will succeed or is likely to succeed.\n"
            + "- Do NOT use declarative framing: \"The judge erred\", \"This proves\", \"The sentence is excessive\". The Court makes findings; the brief identifies arguable errors.\n"
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
    # Self-hosted: the app runs entirely on the owner's personal OPENAI_API_KEY
    # (billing goes straight to the user's OpenAI account). Validated here so
    # a missing key surfaces as a clean 500 rather than a cryptic SDK stack.
    if not os.environ.get("OPENAI_API_KEY"):
        raise Exception("AI service not configured — OPENAI_API_KEY is missing")

    config = TASK_CONFIGS.get(task_type, TASK_CONFIGS["general"])
    resolved_max_tokens = max_tokens if max_tokens is not None else config["max_tokens"]
    resolved_timeout = timeout_seconds if timeout_seconds is not None else config["timeout_seconds"]
    resolved_require_json = require_json if require_json is not None else config["require_json"]

    models = _default_models_for_task(task_type)
    last_err = None

    effective_system_prompt = _apply_task_guardrails(system_prompt, task_type, resolved_require_json)
    effective_user_prompt = user_prompt + (_json_instruction_suffix() if resolved_require_json else "")

    client = _get_openai_client()

    for idx, (provider, model_name) in enumerate(models):
        try:
            # DO_NOT_UNDO — Direct AsyncOpenAI call. Swapped from emergentintegrations
            # LlmChat on 2026-04-21 per owner requirement. Natively async — no
            # thread-pool shim needed. `provider` is retained in the loop tuple
            # for schema compatibility with _default_models_for_task; all slots
            # are OpenAI (see that function for rationale).
            completion = await asyncio.wait_for(
                client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": effective_system_prompt},
                        {"role": "user", "content": effective_user_prompt},
                    ],
                    max_tokens=resolved_max_tokens,
                ),
                timeout=resolved_timeout,
            )

            result = (completion.choices[0].message.content or "") if completion.choices else ""

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
            # Extract real OpenAI usage counts for cent-accurate cost tracking.
            # If missing (rare — streaming/legacy paths), record_usage falls
            # back to tiktoken estimates internally.
            usage = getattr(completion, "usage", None)
            p_tok = getattr(usage, "prompt_tokens", None) if usage else None
            c_tok = getattr(usage, "completion_tokens", None) if usage else None
            t_tok = getattr(usage, "total_tokens", None) if usage else None

            # Record token usage for admin cost dashboard (fire-and-forget).
            try:
                from services.ai_usage_tracker import record_usage
                await record_usage(
                    session_id=session_id,
                    provider=provider,
                    model=model_name,
                    system_prompt=effective_system_prompt,
                    user_prompt=effective_user_prompt,
                    response_text=result,
                    task_type=task_type,
                    ok=True,
                    attempt=idx + 1,
                    prompt_tokens=p_tok,
                    completion_tokens=c_tok,
                    total_tokens=t_tok,
                )
            except Exception:
                pass
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
        # DO_NOT_UNDO — Exponential backoff for 502/service errors on large report prompts.
        # Increased backoff ceiling (was 14s, now 25s) to survive sustained proxy outages.
        is_server_error = "502" in str(last_err) or "503" in str(last_err) or "ServiceUnavailable" in str(last_err) or "BadGateway" in str(last_err)
        if is_server_error and task_type == "report_generation":
            backoff = min(8 + idx * 5, 25)
            logger.info(f"Report generation 502 backoff: waiting {backoff}s before retry")
            await asyncio.sleep(backoff)
        else:
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
