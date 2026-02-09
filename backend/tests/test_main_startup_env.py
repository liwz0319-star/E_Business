"""Tests for startup .env promotion to os.environ."""

import os
from pathlib import Path

from app.main import _ensure_provider_registration, _promote_env_to_os_environ
from app.core.factory import ProviderFactory
from app.infrastructure.generators import DeepSeekGenerator


def test_promote_env_to_os_environ_sets_missing_key(monkeypatch, tmp_path: Path):
    """Loads DEEPSEEK_API_KEY from .env when missing from process env."""
    env_file = tmp_path / ".env"
    env_file.write_text("DEEPSEEK_API_KEY=from-file-key\n", encoding="utf-8")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setattr("app.main._candidate_env_files", lambda: [env_file])

    loaded = _promote_env_to_os_environ()

    assert loaded == env_file
    assert os.getenv("DEEPSEEK_API_KEY") == "from-file-key"


def test_promote_env_to_os_environ_keeps_existing_env(monkeypatch, tmp_path: Path):
    """Does not override explicit runtime env values."""
    env_file = tmp_path / ".env"
    env_file.write_text("DEEPSEEK_API_KEY=from-file-key\n", encoding="utf-8")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "runtime-key")
    monkeypatch.setattr("app.main._candidate_env_files", lambda: [env_file])

    loaded = _promote_env_to_os_environ()

    assert loaded == env_file
    assert os.getenv("DEEPSEEK_API_KEY") == "runtime-key"


def test_promote_env_to_os_environ_returns_none_when_missing(monkeypatch, tmp_path: Path):
    """Returns None when no candidate file exists."""
    missing_env_file = tmp_path / ".env"
    monkeypatch.setattr("app.main._candidate_env_files", lambda: [missing_env_file])

    loaded = _promote_env_to_os_environ()

    assert loaded is None


def test_ensure_provider_registration_is_idempotent():
    """Registers DeepSeek provider once and allows repeated calls."""
    ProviderFactory._registry.pop("deepseek", None)

    _ensure_provider_registration()
    _ensure_provider_registration()

    assert ProviderFactory._registry.get("deepseek") is DeepSeekGenerator
