import pytest
from src.app import activities

class TestGetActivities:
    """Test GET /activities endpoint"""

    def test_get_all_activities_success(self, client, sample_activity_data):
        # Arrange - Set up test client and expected data
        expected_activities = list(activities.keys())

        # Act - Make the request
        response = client.get("/activities")

        # Assert - Verify response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == len(activities)

        # Verify all expected activities are present
        for activity_name in expected_activities:
            assert activity_name in data
            assert "description" in data[activity_name]
            assert "schedule" in data[activity_name]
            assert "max_participants" in data[activity_name]
            assert "participants" in data[activity_name]
            assert isinstance(data[activity_name]["participants"], list)

class TestSignupForActivity:
    """Test POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client, test_email):
        # Arrange - Set up test data
        activity_name = "Soccer Team"  # This activity has no participants initially
        initial_participants = activities[activity_name]["participants"].copy()

        # Act - Make the signup request
        response = client.post(f"/activities/{activity_name}/signup?email={test_email}")

        # Assert - Verify response and state change
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert test_email in data["message"]
        assert activity_name in data["message"]

        # Verify participant was added to the activity
        assert test_email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == len(initial_participants) + 1

    def test_signup_activity_not_found(self, client, test_email):
        # Arrange - Set up invalid activity name
        invalid_activity = "NonExistent Activity"

        # Act - Attempt to signup for non-existent activity
        response = client.post(f"/activities/{invalid_activity}/signup?email={test_email}")

        # Assert - Verify error response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_participant(self, client):
        # Arrange - Set up existing participant
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in Chess Club

        # Act - Attempt to signup again
        response = client.post(f"/activities/{activity_name}/signup?email={existing_email}")

        # Assert - Verify error response
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_signup_activity_full(self, client, test_email):
        # Arrange - Fill up an activity to max capacity
        activity_name = "Gym Class"
        max_participants = activities[activity_name]["max_participants"]

        # Fill the activity
        for i in range(max_participants - len(activities[activity_name]["participants"])):
            temp_email = f"temp{i}@mergington.edu"
            activities[activity_name]["participants"].append(temp_email)

        # Act - Attempt to signup when full
        response = client.post(f"/activities/{activity_name}/signup?email={test_email}")

        # Assert - Verify error response
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "full" in data["detail"]

class TestRemoveParticipant:
    """Test DELETE /activities/{activity_name}/participant/{email} endpoint"""

    def test_remove_participant_success(self, client):
        # Arrange - Set up participant to remove
        activity_name = "Programming Class"
        email_to_remove = "emma@mergington.edu"
        initial_participants = activities[activity_name]["participants"].copy()

        # Act - Remove the participant
        response = client.delete(f"/activities/{activity_name}/participant/{email_to_remove}")

        # Assert - Verify response and state change
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email_to_remove in data["message"]
        assert activity_name in data["message"]

        # Verify participant was removed
        assert email_to_remove not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == len(initial_participants) - 1

    def test_remove_participant_activity_not_found(self, client):
        # Arrange - Set up invalid activity name
        invalid_activity = "NonExistent Activity"
        test_email = "test@mergington.edu"

        # Act - Attempt to remove from non-existent activity
        response = client.delete(f"/activities/{invalid_activity}/participant/{test_email}")

        # Assert - Verify error response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_remove_participant_not_found(self, client):
        # Arrange - Set up valid activity but non-existent participant
        activity_name = "Yoga Club"  # Empty activity
        non_existent_email = "nonexistent@mergington.edu"

        # Act - Attempt to remove non-existent participant
        response = client.delete(f"/activities/{activity_name}/participant/{non_existent_email}")

        # Assert - Verify error response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]