import copy
import pytest

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def preserve_activities():
    # Deep copy activities and restore after each test to avoid cross-test state
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "teststudent@mergington.edu"

    # Ensure not already registered
    assert email not in activities[activity]["participants"]

    # Sign up
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")
    assert email in activities[activity]["participants"]

    # Unregister
    resp = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")
    assert email not in activities[activity]["participants"]


def test_signup_duplicate_fails():
    activity = "Chess Club"
    # Use an existing participant from initial data
    existing = activities[activity]["participants"][0]

    resp = client.post(f"/activities/{activity}/signup", params={"email": existing})
    assert resp.status_code == 400


def test_unregister_nonexistent_fails():
    activity = "Chess Club"
    email = "not-registered@mergington.edu"

    resp = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 400


def test_activity_not_found():
    resp = client.post("/activities/NoSuchActivity/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404

    resp = client.post("/activities/NoSuchActivity/unregister", params={"email": "a@b.com"})
    assert resp.status_code == 404
