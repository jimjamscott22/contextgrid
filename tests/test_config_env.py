"""Tests for DB_* / MYSQL_* env aliasing and script collection hygiene."""

import importlib.util
from pathlib import Path

import pytest

from src.config import first_env


def test_first_env_prefers_db_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DB_USER", "from_db")
    monkeypatch.setenv("MYSQL_USER", "from_mysql")
    assert first_env("DB_USER", "MYSQL_USER", default="") == "from_db"


def test_first_env_falls_back_to_mysql_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DB_USER", raising=False)
    monkeypatch.setenv("MYSQL_USER", "from_mysql")
    assert first_env("DB_USER", "MYSQL_USER", default="") == "from_mysql"


def test_first_env_uses_default_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DB_USER", raising=False)
    monkeypatch.delenv("MYSQL_USER", raising=False)
    assert first_env("DB_USER", "MYSQL_USER", default="missing") == "missing"


def test_scripts_mysql_module_has_no_pytest_collected_names() -> None:
    path = Path(__file__).resolve().parent.parent / "scripts" / "test_mysql_connection.py"
    spec = importlib.util.spec_from_file_location("mysql_check_script", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    collected = [name for name in dir(module) if name.startswith("test_")]
    assert collected == []
