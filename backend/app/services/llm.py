"""Unified, cost-optimized LLM client.

All providers except Anthropic share one OpenAI-compatible code path, so switching
to the cheapest model (DeepSeek V3.2 or Gemini Flash-Lite) is a one-line env change.
When no key is configured the client returns deterministic, schema-valid stubs so the
whole app stays runnable end to end (local dev, CI, demos).
"""

import json
import logging
from typing import Any

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_TIMEOUT_SECONDS = 60


def _has_key() -> bool:
    if settings.llm_provider == "anthropic":
        return bool(settings.anthropic_api_key)
    return bool(settings.llm_api_key)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=20),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def _call_anthropic(system: str, user: str, max_tokens: int) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key, timeout=_TIMEOUT_SECONDS)
    msg = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return msg.content[0].text


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=20),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def _call_openai_compatible(system: str, user: str, max_tokens: int) -> str:
    from openai import OpenAI

    resolved = settings.llm_resolved
    client = OpenAI(
        api_key=settings.llm_api_key,
        base_url=resolved["base_url"],
        timeout=_TIMEOUT_SECONDS,
    )
    resp = client.chat.completions.create(
        model=resolved["model"],
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content or ""


def complete(system: str, user: str, max_tokens: int = 700) -> str:
    if not _has_key():
        logger.warning("No LLM key configured; returning offline stub response.")
        return _offline_stub(system, user)
    if settings.llm_provider == "anthropic":
        return _call_anthropic(system, user, max_tokens)
    return _call_openai_compatible(system, user, max_tokens)


def complete_json(system: str, user: str, max_tokens: int = 900) -> dict[str, Any]:
    raw = complete(system, user, max_tokens)
    return _extract_json(raw)


def _extract_json(text: str) -> dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        s, e = text.find("["), text.rfind("]")
        if s != -1 and e != -1:
            return {"items": json.loads(text[s : e + 1])}
        raise ValueError(f"No JSON object found in model output: {text[:200]}")
    return json.loads(text[start : end + 1])


def _offline_stub(system: str, user: str) -> str:
    """Heuristic, schema-valid responses so flows work without an API key."""
    s, u = system.lower(), user.lower()

    if "behavioral interviewer probing" in u or ("behavioral" in s and "json" in s):
        return json.dumps(
            {
                "score": 3.2,
                "structure_score": 3.0,
                "specificity_score": 3.0,
                "feedback": (
                    "Good arc, but quantify the result and use 'I' not 'we' "
                    "for your actions."
                ),
                "followups": [
                    "What would you do differently next time?",
                    "What was your specific contribution versus the team's?",
                ],
            }
        )

    if "map" in s and "value" in s:
        return json.dumps(
            {"items": [{"value": "Ownership", "evidence": "Drove the fix end to end."}]}
        )

    if "quant" in s:
        return json.dumps(
            {"correct": True, "reasoning_quality": 3.5, "feedback": "Reasonable approach."}
        )

    if "grader" in s or "rubric criteria" in u:
        return json.dumps(
            {
                "overall": 3.4,
                "recommendation": "lean_yes",
                "breakdown": [
                    {
                        "criterion": "Problem Solving",
                        "score": 3.5,
                        "weight": 3.0,
                        "justification": (
                            "Reached a working approach but needed a nudge on complexity."
                        ),
                    },
                    {
                        "criterion": "Communication",
                        "score": 3.0,
                        "weight": 2.0,
                        "justification": "Thought aloud but skipped edge-case discussion.",
                    },
                ],
                "strengths": "Clear final solution; solid data-structure choice.",
                "improvements": "State complexity up front and enumerate edge cases before coding.",
            }
        )

    return (
        "Thanks for joining. Here is the problem: walk me through your approach first, "
        "and feel free to ask any clarifying questions before you start coding."
    )
