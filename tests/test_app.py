import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a known state before each test"""
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu"]
        },
    })
    yield
    activities.clear()


class TestGetActivities:
    def test_get_activities_returns_all_activities(self):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert data["Chess Club"]["max_participants"] == 12

    def test_get_activities_includes_participants(self):
        """Test that activities include participant lists"""
        response = client.get("/activities")
        data = response.json()
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]


class TestSignup:
    def test_signup_valid_email(self):
        """Test signing up with a valid email"""
        response = client.post(
            "/activities/Programming%20Class/signup?email=alice@mergington.edu"
        )
        assert response.status_code == 201
        data = response.json()
        assert "Signed up alice@mergington.edu" in data["message"]
        assert "alice@mergington.edu" in activities["Programming Class"]["participants"]

    def test_signup_invalid_email(self):
        """Test that invalid emails are rejected"""
        response = client.post(
            "/activities/Programming%20Class/signup?email=invalid-email"
        )
        assert response.status_code == 400
        data = response.json()
        assert "Invalid email address" in data["detail"]

    def test_signup_nonexistent_activity(self):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=alice@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_email(self):
        """Test that duplicate signups are rejected"""
        # First signup
        response1 = client.post(
            "/activities/Chess%20Club/signup?email=alice@mergington.edu"
        )
        assert response1.status_code == 201

        # Second signup with same email
        response2 = client.post(
            "/activities/Chess%20Club/signup?email=alice@mergington.edu"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]

    def test_signup_duplicate_case_insensitive(self):
        """Test that duplicate detection is case-insensitive"""
        # First signup
        response1 = client.post(
            "/activities/Chess%20Club/signup?email=alice@mergington.edu"
        )
        assert response1.status_code == 201

        # Second signup with different case
        response2 = client.post(
            "/activities/Chess%20Club/signup?email=ALICE@MERGINGTON.EDU"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]

    def test_signup_activity_full(self):
        """Test that signups are rejected when activity is at capacity"""
        # Create an activity with only 1 spot
        activities["Mini Activity"] = {
            "description": "Small activity",
            "schedule": "Today",
            "max_participants": 1,
            "participants": ["full@mergington.edu"]
        }

        response = client.post(
            "/activities/Mini%20Activity/signup?email=alice@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "full" in data["detail"]

    def test_signup_whitespace_handling(self):
        """Test that email whitespace is trimmed"""
        response = client.post(
            "/activities/Programming%20Class/signup?email=%20alice%40mergington.edu%20"
        )
        assert response.status_code == 201
        # Email should be stored normalized (lowercase, trimmed)
        assert "alice@mergington.edu" in activities["Programming Class"]["participants"]


class TestUnregister:
    def test_unregister_existing_participant(self):
        """Test unregistering an existing participant"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered michael@mergington.edu" in data["message"]
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]

    def test_unregister_nonexistent_participant(self):
        """Test unregistering a participant not in the activity"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_unregister_nonexistent_activity(self):
        """Test unregistering from a non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent%20Club/unregister?email=alice@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_invalid_email(self):
        """Test unregistering with invalid email format"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=invalid-email"
        )
        assert response.status_code == 400
        data = response.json()
        assert "Invalid email address" in data["detail"]

    def test_unregister_case_insensitive(self):
        """Test that unregister is case-insensitive"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=MICHAEL@MERGINGTON.EDU"
        )
        assert response.status_code == 200
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


class TestRoot:
    def test_root_redirects_to_static(self):
        """Test that root path redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
