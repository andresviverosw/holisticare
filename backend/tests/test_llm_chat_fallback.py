"""Anthropic → OpenAI fallback for RAG chat completions."""

from __future__ import annotations

from unittest.mock import MagicMock

import anthropic
import httpx
import pytest

from app.rag import llm_chat


def _bad_request() -> anthropic.BadRequestError:
    req = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    resp = httpx.Response(400, request=req)
    return anthropic.BadRequestError(
        "credit balance too low",
        response=resp,
        body={"error": {"type": "invalid_request_error"}},
    )


def test_complete_claude_or_openai_falls_back_to_openai(monkeypatch):
    fake_settings = MagicMock()
    fake_settings.anthropic_api_key = "sk-ant-test"
    fake_settings.claude_model = "claude-sonnet-4-20250514"
    fake_settings.rag_llm_fallback_openai = True
    fake_settings.openai_api_key = "sk-openai-test"
    fake_settings.openai_chat_model = "gpt-4o-mini"
    monkeypatch.setattr(llm_chat, "get_settings", lambda: fake_settings)

    anthro = MagicMock()
    anthro.messages.create.side_effect = _bad_request()
    monkeypatch.setattr(llm_chat.anthropic, "Anthropic", lambda **k: anthro)

    oai = MagicMock()
    oai.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="  openai summary  "))]
    )
    monkeypatch.setattr(llm_chat, "OpenAI", lambda **k: oai)

    out = llm_chat.complete_claude_or_openai(system=None, user="hello", max_tokens=50)
    assert out == "openai summary"
    oai.chat.completions.create.assert_called_once()
    kwargs = oai.chat.completions.create.call_args.kwargs
    assert kwargs["model"] == "gpt-4o-mini"
    assert kwargs["messages"] == [{"role": "user", "content": "hello"}]


def test_complete_claude_or_openai_no_fallback_when_disabled(monkeypatch):
    fake_settings = MagicMock()
    fake_settings.anthropic_api_key = "sk-ant-test"
    fake_settings.claude_model = "claude-sonnet-4-20250514"
    fake_settings.rag_llm_fallback_openai = False
    fake_settings.openai_api_key = "sk-openai-test"
    fake_settings.openai_chat_model = "gpt-4o-mini"
    monkeypatch.setattr(llm_chat, "get_settings", lambda: fake_settings)

    anthro = MagicMock()
    anthro.messages.create.side_effect = _bad_request()
    monkeypatch.setattr(llm_chat.anthropic, "Anthropic", lambda **k: anthro)
    monkeypatch.setattr(llm_chat, "OpenAI", MagicMock())

    with pytest.raises(anthropic.BadRequestError):
        llm_chat.complete_claude_or_openai(system=None, user="hello", max_tokens=50)


def test_complete_claude_or_openai_passes_system_to_openai(monkeypatch):
    fake_settings = MagicMock()
    fake_settings.anthropic_api_key = "sk-ant-test"
    fake_settings.claude_model = "claude-sonnet-4-20250514"
    fake_settings.rag_llm_fallback_openai = True
    fake_settings.openai_api_key = "sk-openai-test"
    fake_settings.openai_chat_model = "gpt-4o-mini"
    monkeypatch.setattr(llm_chat, "get_settings", lambda: fake_settings)

    anthro = MagicMock()
    anthro.messages.create.side_effect = _bad_request()
    monkeypatch.setattr(llm_chat.anthropic, "Anthropic", lambda **k: anthro)

    oai = MagicMock()
    oai.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="{}"))]
    )
    monkeypatch.setattr(llm_chat, "OpenAI", lambda **k: oai)

    llm_chat.complete_claude_or_openai(system="You are helpful.", user="Do task", max_tokens=100)
    msgs = oai.chat.completions.create.call_args.kwargs["messages"]
    assert msgs[0] == {"role": "system", "content": "You are helpful."}
    assert msgs[1] == {"role": "user", "content": "Do task"}
