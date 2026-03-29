"""
Criminal Appeal AI - LLM Service
Reusable LLM call with model fallback.
"""
import os
import asyncio
import logging

logger = logging.getLogger(__name__)


async def call_llm_with_fallback(
    system_prompt: str,
    user_prompt: str,
    session_id: str = "default",
    max_tokens: int = 16384,
    timeout_seconds: int = 120,
) -> str:
    """Call LLM with model fallback: gpt-4o (x2) -> Claude -> gpt-4o-mini."""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise Exception("AI service not configured — EMERGENT_LLM_KEY missing")

    models = [
        ("openai", "gpt-4o"),
        ("openai", "gpt-4o"),
        ("anthropic", "claude-sonnet-4-20250514"),
        ("openai", "gpt-4o-mini"),
    ]
    last_err = None
    for idx, (provider, model_name) in enumerate(models):
        try:
            chat = LlmChat(api_key=api_key, session_id=session_id, system_message=system_prompt).with_model(provider, model_name).with_params(max_tokens=max_tokens)
            result = await asyncio.wait_for(chat.send_message(UserMessage(text=user_prompt)), timeout=timeout_seconds)
            if result and len(result.strip()) > 50 and "I'm sorry" not in result[:80]:
                logger.info(f"LLM success ({session_id}) with {provider}/{model_name} on attempt {idx+1}")
                return result
            last_err = f"Short/refused response from {provider}/{model_name}"
        except asyncio.TimeoutError:
            last_err = f"Timeout with {provider}/{model_name}"
        except Exception as e:
            last_err = str(e)[:200]
        logger.warning(f"LLM attempt {idx+1} ({provider}/{model_name}) for {session_id}: {last_err}")
        await asyncio.sleep(2 + idx)
    raise Exception(f"All LLM attempts failed: {last_err}")
