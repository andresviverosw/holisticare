"""
Shared chat completion for RAG: Anthropic Messages API first, optional OpenAI fallback.

Used when Anthropic returns billing/auth/rate errors but OpenAI (embeddings key) still works.
"""

from __future__ import annotations

import logging

import anthropic
from openai import OpenAI

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def complete_claude_or_openai(
    *,
    system: str | None,
    user: str,
    max_tokens: int,
) -> str:
    """
    Run Claude; on Anthropic failure, optionally retry with OpenAI Chat Completions
    (same prompts; system message mapped to OpenAI's system role).
    """
    settings = get_settings()
    anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    try:
        kwargs: dict = {
            "model": settings.claude_model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": user}],
        }
        if system:
            kwargs["system"] = system
        response = anthropic_client.messages.create(**kwargs)
        return response.content[0].text.strip()
    except anthropic.AnthropicError as exc:
        if not settings.rag_llm_fallback_openai:
            raise
        logger.warning(
            "Anthropic request failed (%s: %s); falling back to OpenAI chat model %s",
            type(exc).__name__,
            exc,
            settings.openai_chat_model,
        )
        return _openai_chat_completion(system=system, user=user, max_tokens=max_tokens)


def _openai_chat_completion(*, system: str | None, user: str, max_tokens: int) -> str:
    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    resp = client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=messages,
        max_tokens=max_tokens,
    )
    content = resp.choices[0].message.content
    return (content or "").strip()
