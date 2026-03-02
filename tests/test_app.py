"""
Tests for the Mergington High School Activities API
"""

import pytest
import copy
from fastapi.testclient import TestClient

from app import app, activities

client = TestClient(app)

_original_activities = copy.deepcopy(dict(activities))


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    for key in _original_activities:
        activities[key] = copy.deepcopy(_original_activities[key])
    yield


def test_get_activities():
    """Test that all activities are returned"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_signup_for_activity():
    """Test signing up for an activity"""
    response = client.post(
        "/activities/Chess Club/signup?email=newstudent@mergington.edu"
    )
    assert response.status_code == 200
    assert "newstudent@mergington.edu" in response.json()["message"]
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_for_nonexistent_activity():
    """Test signing up for an activity that doesn't exist"""
    response = client.post(
        "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
    )
    assert response.status_code == 404


def test_signup_duplicate_participant():
    """Test that duplicate sign-ups are rejected"""
    response = client.post(
        "/activities/Chess Club/signup?email=michael@mergington.edu"
    )
    assert response.status_code == 400


def test_unregister_from_activity():
    """Test unregistering a participant from an activity"""
    response = client.delete(
        "/activities/Chess Club/signup?email=michael@mergington.edu"
    )
    assert response.status_code == 200
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_nonexistent_participant():
    """Test unregistering a participant who is not signed up"""
    response = client.delete(
        "/activities/Chess Club/signup?email=notregistered@mergington.edu"
    )
    assert response.status_code == 404


def test_unregister_from_nonexistent_activity():
    """Test unregistering from an activity that doesn't exist"""
    response = client.delete(
        "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
    )
    assert response.status_code == 404


def test_activity_has_required_fields():
    """Test that activities have all required fields"""
    response = client.get("/activities")
    data = response.json()
    for activity in data.values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
