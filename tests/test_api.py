import pytest
from fastapi import HTTPException

from app import main as main_module


def test_delete_terminal_order_removes_cache(monkeypatch):
    deleted = []

    def one(sql, params=None):
        assert "DELETE FROM orders" in sql
        assert params == (12,)
        return {"id": 12}

    monkeypatch.setattr(main_module.db, "one", one)
    monkeypatch.setattr(main_module.cache, "drop", lambda key: deleted.append(key))

    response = main_module.delete_order(12)

    assert response.status_code == 204
    assert deleted == ["order:12"]


def test_delete_active_order_returns_conflict(monkeypatch):
    def one(sql, params=None):
        if "DELETE FROM orders" in sql:
            return None
        assert "SELECT status FROM orders" in sql
        return {"status": "cooking"}

    monkeypatch.setattr(main_module.db, "one", one)

    with pytest.raises(HTTPException) as error:
        main_module.delete_order(12)
    assert error.value.status_code == 409
    assert error.value.detail == "only delivered or cancelled orders can be deleted"


def test_delete_unknown_order_returns_not_found(monkeypatch):
    monkeypatch.setattr(main_module.db, "one", lambda sql, params=None: None)

    with pytest.raises(HTTPException) as error:
        main_module.delete_order(12)
    assert error.value.status_code == 404


def test_index_page_returns_html():
    response = main_module.index()
    assert response.status_code == 200
    assert b"Food Delivery Order Tracker" in response.body

