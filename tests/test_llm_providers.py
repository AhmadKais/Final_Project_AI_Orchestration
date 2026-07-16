"""The three non-default LLM providers for the verbal bluff layer (Sec.
6.5.1, Appendix F Table 21): Ollama, Claude API, Claude CLI. All mocked --
none of these should ever be exercised against a real network/subprocess in
an automated test suite (slow, non-deterministic, and for the API/CLI
providers, real token cost). The one exception is a genuinely unreachable
localhost Ollama, which is safe, fast, and confirms the real error path.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from police_thief.infra.llm.base import truncate_to_word_limit
from police_thief.infra.llm.claude_api_provider import ClaudeAPIProvider
from police_thief.infra.llm.claude_cli_provider import ClaudeCLIProvider
from police_thief.infra.llm.ollama_provider import OllamaProvider


# -- shared truncation helper -----------------------------------------------

def test_truncate_to_word_limit_leaves_short_text_alone():
    assert truncate_to_word_limit("holding position now", 5) == "holding position now"


def test_truncate_to_word_limit_cuts_long_text():
    assert truncate_to_word_limit("one two three four five six", 3) == "one two three"


# -- OllamaProvider -----------------------------------------------------------

def test_ollama_provider_raises_on_unreachable_server():
    # Genuinely unreachable (no mocking) -- fast, safe, and confirms the
    # real error path a team would hit if they forgot to run `ollama serve`.
    provider = OllamaProvider(base_url="http://localhost:1", timeout_sec=1)
    with pytest.raises(RuntimeError, match="unreachable"):
        provider.generate_hint(prompt="test", word_limit=15)


def test_ollama_provider_parses_response_and_truncates():
    provider = OllamaProvider()
    fake_response = MagicMock()
    fake_response.read.return_value = json.dumps(
        {"response": "one two three four five six seven eight"}
    ).encode("utf-8")
    fake_response.__enter__.return_value = fake_response
    fake_response.__exit__.return_value = False

    with patch("urllib.request.urlopen", return_value=fake_response) as mock_urlopen:
        hint = provider.generate_hint(prompt="where are you", word_limit=4)

    assert hint == "one two three four"
    mock_urlopen.assert_called_once()


def test_ollama_provider_sends_the_model_and_prompt():
    provider = OllamaProvider(model="mistral", base_url="http://localhost:11434")
    fake_response = MagicMock()
    fake_response.read.return_value = json.dumps({"response": "ok"}).encode("utf-8")
    fake_response.__enter__.return_value = fake_response
    fake_response.__exit__.return_value = False

    with patch("urllib.request.urlopen", return_value=fake_response) as mock_urlopen:
        provider.generate_hint(prompt="hello", word_limit=15)

    sent_request = mock_urlopen.call_args[0][0]
    payload = json.loads(sent_request.data.decode("utf-8"))
    assert payload["model"] == "mistral"
    assert "hello" in payload["prompt"]


# -- ClaudeAPIProvider --------------------------------------------------------

def test_claude_api_provider_calls_messages_create_and_truncates():
    provider = ClaudeAPIProvider(model="claude-haiku-4-5", api_key="fake-key")

    text_block = MagicMock(type="text", text="one two three four five")
    fake_response = MagicMock(content=[text_block])
    fake_client = MagicMock()
    fake_client.messages.create.return_value = fake_response

    with patch("anthropic.Anthropic", return_value=fake_client):
        hint = provider.generate_hint(prompt="closing in", word_limit=3)

    assert hint == "one two three"
    _, kwargs = fake_client.messages.create.call_args
    assert kwargs["model"] == "claude-haiku-4-5"
    assert kwargs["messages"] == [{"role": "user", "content": "closing in"}]


def test_claude_api_provider_wraps_api_errors():
    import anthropic

    provider = ClaudeAPIProvider(api_key="fake-key")
    fake_client = MagicMock()
    fake_client.messages.create.side_effect = anthropic.APIConnectionError(request=MagicMock())

    with patch("anthropic.Anthropic", return_value=fake_client):
        with pytest.raises(RuntimeError, match="Claude API call failed"):
            provider.generate_hint(prompt="test", word_limit=15)


# -- ClaudeCLIProvider --------------------------------------------------------

def test_claude_cli_provider_shells_out_and_truncates():
    provider = ClaudeCLIProvider()
    fake_result = MagicMock(stdout="one two three four five\n")

    with patch("subprocess.run", return_value=fake_result) as mock_run:
        hint = provider.generate_hint(prompt="status", word_limit=3)

    assert hint == "one two three"
    args, kwargs = mock_run.call_args
    assert args[0][0] == "claude"
    assert args[0][1] == "-p"
    assert kwargs["timeout"] == provider.timeout_sec


def test_claude_cli_provider_raises_when_cli_unavailable():
    provider = ClaudeCLIProvider()

    with patch("subprocess.run", side_effect=FileNotFoundError("no such file")):
        with pytest.raises(RuntimeError, match="unavailable"):
            provider.generate_hint(prompt="test", word_limit=15)
