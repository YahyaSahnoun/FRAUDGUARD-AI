"""Tests for application configuration."""

import pytest
from pydantic import ValidationError

from fraudguard.core.config import Settings


def test_default_settings(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    settings = Settings(
        _env_file=None,
        app_env="development",
        llm_provider="mock",
    )

    assert settings.app_env == "development"
    assert settings.llm_provider == "mock"


def test_invalid_postgres_port(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            postgres_port=70000,
        )


def test_production_requires_passwords(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="POSTGRES_PASSWORD"):
        Settings(
            _env_file=None,
            app_env="production",
            postgres_password="",
        )


def test_groq_requires_api_key(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="GROQ_API_KEY"):
        Settings(
            _env_file=None,
            llm_provider="groq",
            groq_api_key="",
        )


def test_password_is_masked(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    dummy_password = "example-only-password"  # pragma: allowlist secret

    settings = Settings(
        _env_file=None,
        postgres_password=dummy_password,
    )

    assert dummy_password not in repr(settings)
