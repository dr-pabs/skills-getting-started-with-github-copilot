import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test."""
    original = {
        name: {**data, "participants": list(data["participants"])}
        for name, data in activities.items()
    }
    yield
    activities.clear()
    activities.update(original)


client = TestClient(app)


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_signup_for_activity():
    response = client.post("/activities/Chess Club/signup?email=new@mergington.edu")
    assert response.status_code == 200
    assert "new@mergington.edu" in response.json()["message"]
    assert "new@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_activity_not_found():
    response = client.post("/activities/Unknown Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404


def test_signup_already_registered():
    response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_activity_full():
    activity = activities["Chess Club"]
    max_p = activity["max_participants"]
    # Fill the activity to capacity
    while len(activity["participants"]) < max_p:
        activity["participants"].append(f"fill{len(activity['participants'])}@mergington.edu")
    response = client.post("/activities/Chess Club/signup?email=extra@mergington.edu")
    assert response.status_code == 400
    assert "full" in response.json()["detail"]


def test_unregister_from_activity():
    response = client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")
    assert response.status_code == 200
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_activity_not_found():
    response = client.delete("/activities/Unknown Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404


def test_unregister_not_signed_up():
    response = client.delete("/activities/Chess Club/signup?email=nobody@mergington.edu")
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]


def test_root_redirects():
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (301, 302, 307, 308)
