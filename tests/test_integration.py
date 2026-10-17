import os
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from app import cache, db
from app import main as main_module
from app.main import app


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION") != "1",
    reason="Set RUN_INTEGRATION=1 to run database/Redis integration tests",
)


@pytest.fixture(autouse=True)
def clean_services():
    """Give each integration test a clean database and Redis cache."""
    db.query(
        "TRUNCATE TABLE order_events, orders RESTART IDENTITY CASCADE",
        fetch=False,
    )
    cache.client().flushdb()
    yield
    cache.client().flushdb()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def create_order(client, restaurant="Integration Kitchen"):
    response = client.post(
        "/orders",
        json={
            "customer": "test_customer",
            "restaurant": restaurant,
            "items": [
                {"name": "Masala Dosa", "paise": 12000},
                {"name": "Coffee", "paise": 4000},
            ],
        },
    )
    assert response.status_code == 201
    return response.json()


def test_health_checks_postgres_and_redis(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["postgres"] is True
    assert response.json()["redis"] is True


def test_create_order_persists_in_database_and_cache(client):
    created = create_order(client)
    order_id = created["id"]

    assert created["status"] == "placed"
    assert created["total_paise"] == 16000
    assert created["customer"] == "test_customer"

    row = db.one(
        "SELECT id, customer, restaurant, total_paise, status "
        "FROM orders WHERE id=%s",
        (order_id,),
    )
    assert row is not None
    assert row["customer"] == "test_customer"
    assert row["total_paise"] == 16000
    assert row["status"] == "placed"

    cached = cache.get_json(f"order:{order_id}")
    assert cached is not None
    assert cached["id"] == order_id
    assert cached["status"] == "placed"

    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    assert response.json()["cached"] is True


def test_status_update_persists_version_and_event(client):
    created = create_order(client)
    order_id = created["id"]

    response = client.post(
        f"/orders/{order_id}/status",
        json={
            "to": "accepted",
            "expected": "placed",
            "actor": "integration_test",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
    assert response.json()["version"] == 1

    row = db.one(
        "SELECT status, version FROM orders WHERE id=%s",
        (order_id,),
    )
    assert row["status"] == "accepted"
    assert row["version"] == 1

    event = db.one(
        "SELECT from_status, to_status, actor "
        "FROM order_events "
        "WHERE order_id=%s AND to_status='accepted'",
        (order_id,),
    )
    assert event is not None
    assert event["from_status"] == "placed"
    assert event["actor"] == "integration_test"

    cached = cache.get_json(f"order:{order_id}")
    assert cached["status"] == "accepted"


def test_invalid_transition_is_rejected(client):
    created = create_order(client)

    response = client.post(
        f"/orders/{created['id']}/status",
        json={"to": "cooking", "expected": "placed"},
    )

    assert response.status_code == 400

    row = db.one(
        "SELECT status FROM orders WHERE id=%s",
        (created["id"],),
    )
    assert row["status"] == "placed"


def test_stale_expected_status_returns_conflict(client):
    created = create_order(client)
    order_id = created["id"]

    accepted = client.post(
        f"/orders/{order_id}/status",
        json={"to": "accepted", "expected": "placed"},
    )
    assert accepted.status_code == 200

    stale = client.post(
        f"/orders/{order_id}/status",
        json={"to": "cooking", "expected": "placed"},
    )

    assert stale.status_code == 409

    row = db.one(
        "SELECT status FROM orders WHERE id=%s",
        (order_id,),
    )
    assert row["status"] == "accepted"


def test_restaurant_queue_contains_outstanding_order(client):
    restaurant = "Queue Integration Kitchen"
    created = create_order(client, restaurant=restaurant)

    response = client.get(f"/restaurants/{restaurant}/queue")

    assert response.status_code == 200
    assert response.json()["restaurant"] == restaurant
    assert response.json()["outstanding"] == 1
    assert response.json()["orders"][0]["id"] == created["id"]


def test_cancellation_after_cooking_is_rejected(client):
    created = create_order(client)
    order_id = created["id"]

    accepted = client.post(
        f"/orders/{order_id}/status",
        json={"to": "accepted", "expected": "placed"},
    )
    assert accepted.status_code == 200

    cooking = client.post(
        f"/orders/{order_id}/status",
        json={"to": "cooking", "expected": "accepted"},
    )
    assert cooking.status_code == 200

    cancelled = client.post(
        f"/orders/{order_id}/cancel",
        json={"actor": "integration_test"},
    )

    assert cancelled.status_code == 409

    row = db.one(
        "SELECT status FROM orders WHERE id=%s",
        (order_id,),
    )
    assert row["status"] == "cooking"


def test_concurrent_updates_cannot_both_win(client, monkeypatch):
    created = create_order(client)
    order_id = created["id"]

    accepted = client.post(
        f"/orders/{order_id}/status",
        json={"to": "accepted", "expected": "placed"},
    )
    assert accepted.status_code == 200

    # Ensure both requests read the same status before either attempts its
    # conditional database update.
    barrier = threading.Barrier(2)
    thread_state = threading.local()
    original_load = main_module.load

    def synchronized_load(oid):
        row = original_load(oid)
        calls = getattr(thread_state, "calls", 0)
        thread_state.calls = calls + 1

        if calls == 0:
            barrier.wait(timeout=10)

        return row

    monkeypatch.setattr(main_module, "load", synchronized_load)

    def update_status(target):
        with TestClient(app) as parallel_client:
            return parallel_client.post(
                f"/orders/{order_id}/status",
                json={"to": target, "expected": "accepted"},
            )

    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(update_status, "cooking")
        second = executor.submit(update_status, "cancelled")
        responses = [first.result(timeout=20), second.result(timeout=20)]

    assert sorted(response.status_code for response in responses) == [200, 409]

    final_order = db.one(
        "SELECT status, version FROM orders WHERE id=%s",
        (order_id,),
    )
    assert final_order["status"] in ("cooking", "cancelled")
    assert final_order["version"] == 2
