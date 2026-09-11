import pytest

from app.core.config import AppSettings


def test_config_loads_defaults() -> None:
    settings = AppSettings()
    assert settings.app_name == "TRON-DeCypher"
    assert settings.log_level == "INFO"
    assert settings.env == "development"

def test_new_settings_defaults() -> None:
    from app.core.config import settings
    assert settings.offline_mode is True
    assert settings.max_artifact_size == 100 * 1024 * 1024
    assert settings.max_pcap_packets == 100000

def test_settings_persistence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRON_DECYPHER_MAX_ARTIFACT_SIZE", "5000")
    new_settings = AppSettings()
    assert new_settings.max_artifact_size == 5000
