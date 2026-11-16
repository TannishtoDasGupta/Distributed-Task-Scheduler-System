from types import SimpleNamespace
import pytest
from fastapi import HTTPException
from app.security import require_api_key

def test_api_key_is_required_when_configured(monkeypatch):
    monkeypatch.setattr("app.security.settings", SimpleNamespace(api_key="a" * 32))
    with pytest.raises(HTTPException) as error:
        require_api_key(None)
    assert error.value.status_code == 401

def test_api_key_accepts_matching_secret(monkeypatch):
    secret = "b" * 32
    monkeypatch.setattr("app.security.settings", SimpleNamespace(api_key=secret))
    assert require_api_key(secret) is None

def test_api_key_rejects_wrong_secret(monkeypatch):
    monkeypatch.setattr("app.security.settings", SimpleNamespace(api_key="c" * 32))
    with pytest.raises(HTTPException) as error:
        require_api_key("wrong")
    assert error.value.status_code == 401

def test_api_fails_closed_if_secret_is_not_configured(monkeypatch):
    monkeypatch.setattr("app.security.settings", SimpleNamespace(api_key=None))
    with pytest.raises(HTTPException) as error:
        require_api_key(None)
    assert error.value.status_code == 503
