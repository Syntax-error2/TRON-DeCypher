import json
import typing
import urllib.error
import urllib.request
from unittest.mock import MagicMock, patch

import pytest

from app.ai.models.models import AIProviderConfig
from app.ai.providers.anthropic_provider import AnthropicProvider
from app.ai.providers.mock_provider import MockAIProvider
from app.ai.services.copilot_service import CopilotService
from app.core.config import settings


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> typing.Generator[None, None, None]:
    monkeypatch.setattr(settings, "anthropic_api_key", None)
    monkeypatch.setattr(settings, "anthropic_base_url", None)
    monkeypatch.setattr(settings, "anthropic_api_mode", "Mock")
    monkeypatch.setattr(settings, "anthropic_model", "claude-3-opus-20240229")
    yield

def test_config_loading_defaults(clean_env: None) -> None:
    service = CopilotService()
    assert service.config.provider == "Mock"
    assert service.config.model == "claude-3-opus-20240229"
    assert isinstance(service.provider, MockAIProvider)

def test_config_loading_external(monkeypatch: pytest.MonkeyPatch, clean_env: None) -> None:
    monkeypatch.setattr(settings, "anthropic_api_key", "sk-ant-test1234")
    monkeypatch.setattr(settings, "anthropic_api_mode", "External")
    monkeypatch.setattr(settings, "anthropic_base_url", "https://custom.router.com/v1")
    monkeypatch.setattr(settings, "anthropic_model", "claude-3-5-sonnet")
    
    service = CopilotService()
    assert service.config.provider == "Anthropic"
    assert service.config.model == "claude-3-5-sonnet"
    assert service.config.base_url == "https://custom.router.com/v1"
    assert isinstance(service.provider, AnthropicProvider)
    assert service.provider.is_configured()

def test_anthropic_url_validation(monkeypatch: pytest.MonkeyPatch, clean_env: None) -> None:
    monkeypatch.setattr(settings, "anthropic_api_key", "sk-ant-test")
    monkeypatch.setattr(settings, "anthropic_api_mode", "External")
    
    # Test valid
    monkeypatch.setattr(settings, "anthropic_base_url", "https://api.test.com/v1")
    service = CopilotService()
    assert type(service.provider) is AnthropicProvider; assert service.provider._validate_url(settings.anthropic_base_url or "")
    
    # Test invalid (HTTP non-local)
    monkeypatch.setattr(settings, "anthropic_base_url", "http://malicious.com")
    service = CopilotService()
    assert type(service.provider) is AnthropicProvider; assert not service.provider._validate_url(settings.anthropic_base_url or "")
    
    # Test valid local HTTP
    monkeypatch.setattr(settings, "anthropic_base_url", "http://127.0.0.1:8000")
    service = CopilotService()
    assert type(service.provider) is AnthropicProvider; assert service.provider._validate_url(settings.anthropic_base_url or "")

@patch("urllib.request.urlopen")
def test_anthropic_success(mock_urlopen: MagicMock, monkeypatch: pytest.MonkeyPatch, clean_env: None) -> None:
    monkeypatch.setattr(settings, "anthropic_api_key", "sk-ant-test")
    
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "content": [{"text": json.dumps({"summary": "Success!", "confidence": "High"})}]
    }).encode("utf-8")
    mock_response.status = 200
    mock_urlopen.return_value.__enter__.return_value = mock_response

    config = AIProviderConfig(provider="Anthropic")
    provider = AnthropicProvider(config)
    
    resp = provider.analyze("sys", "user")
    assert resp.summary == "Success!"
    assert resp.confidence == "High"

@patch("urllib.request.urlopen")
def test_anthropic_retry_429(mock_urlopen: MagicMock, monkeypatch: pytest.MonkeyPatch, clean_env: None) -> None:
    monkeypatch.setattr(settings, "anthropic_api_key", "sk-ant-test")
    
    # Fail twice with 429, then succeed
    mock_error = urllib.error.HTTPError("url", 429, "Too Many Requests", MagicMock(), None)
    
    mock_success = MagicMock()
    mock_success.read.return_value = json.dumps({
        "content": [{"text": json.dumps({"summary": "Recovered!", "confidence": "Medium"})}]
    }).encode("utf-8")
    mock_success.status = 200
    
    mock_urlopen.side_effect = [mock_error, mock_error, MagicMock(__enter__=lambda self: mock_success, __exit__=lambda *args: None)]
    
    config = AIProviderConfig(provider="Anthropic")
    provider = AnthropicProvider(config)
    
    # Speed up sleep
    with patch("time.sleep", return_value=None):
        resp = provider.analyze("sys", "user")
        
    assert resp.summary == "Recovered!"
    assert mock_urlopen.call_count == 3

@patch("urllib.request.urlopen")
def test_anthropic_401_no_retry(mock_urlopen: MagicMock, monkeypatch: pytest.MonkeyPatch, clean_env: None) -> None:
    monkeypatch.setattr(settings, "anthropic_api_key", "sk-ant-test")
    
    mock_error = urllib.error.HTTPError("url", 401, "Unauthorized", MagicMock(), None)
    mock_urlopen.side_effect = mock_error
    
    config = AIProviderConfig(provider="Anthropic")
    provider = AnthropicProvider(config)
    
    with patch("time.sleep") as mock_sleep:
        resp = provider.analyze("sys", "user")
        assert "API HTTP Error: 401" in resp.summary
        assert mock_urlopen.call_count == 1
        mock_sleep.assert_not_called()

@patch("urllib.request.urlopen")
def test_anthropic_malformed_json(mock_urlopen: MagicMock, monkeypatch: pytest.MonkeyPatch, clean_env: None) -> None:
    monkeypatch.setattr(settings, "anthropic_api_key", "sk-ant-test")
    
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "content": [{"text": "This is not JSON"}]
    }).encode("utf-8")
    mock_response.status = 200
    mock_urlopen.return_value.__enter__.return_value = mock_response

    config = AIProviderConfig(provider="Anthropic")
    provider = AnthropicProvider(config)
    
    resp = provider.analyze("sys", "user")
    assert "Failed to parse structured JSON" in resp.summary
    assert "This is not JSON" in resp.summary

def test_missing_key_behavior(clean_env: None) -> None:
    config = AIProviderConfig(provider="Anthropic")
    provider = AnthropicProvider(config)
    
    resp = provider.analyze("sys", "user")
    assert "Anthropic API Key not configured" in resp.summary




