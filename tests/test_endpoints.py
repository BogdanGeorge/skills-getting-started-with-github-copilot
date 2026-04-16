"""
Integration tests for FastAPI backend endpoints.

All tests follow the AAA (Arrange-Act-Assert) testing pattern:
- Arrange: Set up test data and client using fixtures
- Act: Call the endpoint with specific parameters
- Assert: Verify response status, data structure, and state changes
"""

import pytest


# ============================================================================
# GET /activities Tests
# ============================================================================

class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: TestClient is ready
        Act: GET /activities
        Assert: 200 status, returns dict with 9 activities
        """
        # Arrange is implicit via client fixture

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities_data = response.json()
        assert isinstance(activities_data, dict)
        assert len(activities_data) == 9

    def test_get_activities_response_structure(self, client):
        """
        Arrange: TestClient is ready
        Act: GET /activities
        Assert: Each activity has required fields (description, schedule, max_participants, participants)
        """
        # Arrange is implicit via client fixture

        # Act
        response = client.get("/activities")
        activities_data = response.json()

        # Assert - verify structure of first activity
        assert "Chess Club" in activities_data
        chess_club = activities_data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_includes_all_activity_names(self, client):
        """
        Arrange: TestClient is ready
        Act: GET /activities
        Assert: All 10 activity names are present in response
        """
        # Arrange - expected activity names
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Soccer Team",
            "Swimming Club",
            "Art Club",
            "Drama Club",
            "Debate Team",
            "Math Olympiad"
        ]

        # Act
        response = client.get("/activities")
        activities_data = response.json()

        # Assert
        for activity_name in expected_activities:
            assert activity_name in activities_data

    def test_get_activities_includes_initial_participants(self, client):
        """
        Arrange: TestClient is ready
        Act: GET /activities
        Assert: Initial participants are returned correctly
        """
        # Arrange is implicit via client fixture

        # Act
        response = client.get("/activities")
        activities_data = response.json()

        # Assert - verify initial participants are present
        assert "michael@mergington.edu" in activities_data["Chess Club"]["participants"]
        assert "emma@mergington.edu" in activities_data["Programming Class"]["participants"]
        assert "john@mergington.edu" in activities_data["Gym Class"]["participants"]

    def test_get_activities_empty_activities_are_empty_lists(self, client):
        """
        Arrange: TestClient is ready
        Act: GET /activities
        Assert: Activities with no participants have empty lists
        """
        # Arrange is implicit via client fixture

        # Act
        response = client.get("/activities")
        activities_data = response.json()

        # Assert
        assert activities_data["Soccer Team"]["participants"] == []
        assert activities_data["Swimming Club"]["participants"] == []


# ============================================================================
# POST /activities/{activity_name}/signup Tests
# ============================================================================

class TestSignupActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_student_success(self, client, test_emails, test_activities):
        """
        Arrange: New student email and valid activity
        Act: POST signup with new email
        Assert: 200 status, response confirms signup, participants updated
        """
        # Arrange
        activity_name = test_activities["valid_empty"]  # Soccer Team (no participants)
        email = test_emails["new_student"]

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert - response
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]

        # Assert - state changed (verify via another GET call)
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]

    def test_signup_multiple_students_same_activity(self, client, test_emails, test_activities):
        """
        Arrange: Two different student emails and valid activity
        Act: POST signup for first student, then second student
        Assert: Both signups succeed, both emails in participants
        """
        # Arrange
        activity_name = test_activities["valid_empty"]
        email1 = test_emails["new_student"]
        email2 = test_emails["another_student"]

        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200

        # Verify both are in participants
        activities = client.get("/activities").json()
        assert email1 in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]

    def test_signup_duplicate_email_returns_error(self, client, test_emails, test_activities):
        """
        Arrange: Email already signed up for activity
        Act: POST signup with same email again
        Assert: 400 status, error message indicates duplicate signup
        """
        # Arrange
        activity_name = test_activities["valid_empty"]
        email = test_emails["new_student"]
        
        # First signup succeeds
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Act - attempt duplicate signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_existing_student_still_in_activity(self, client, test_emails, test_activities):
        """
        Arrange: Using email already in initial participants
        Act: POST signup with existing email
        Assert: 400 status, error indicates already signed up
        """
        # Arrange
        activity_name = test_activities["valid"]  # Chess Club (has participants)
        email = test_emails["existing_chess"]

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client, test_emails, test_activities):
        """
        Arrange: Invalid activity name
        Act: POST signup to non-existent activity
        Assert: 404 status, error message indicates activity not found
        """
        # Arrange
        activity_name = test_activities["invalid"]
        email = test_emails["new_student"]

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_increments_participant_count(self, client, test_emails, test_activities):
        """
        Arrange: Valid activity and new email
        Act: POST signup
        Assert: Participant count increases by exactly 1
        """
        # Arrange
        activity_name = test_activities["valid_empty"]
        email = test_emails["new_student"]
        
        # Get initial count
        activities_before = client.get("/activities").json()
        initial_count = len(activities_before[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        activities_after = client.get("/activities").json()
        final_count = len(activities_after[activity_name]["participants"])
        assert final_count == initial_count + 1


# ============================================================================
# POST /activities/{activity_name}/unregister Tests
# ============================================================================

class TestUnregisterActivity:
    """Tests for the POST /activities/{activity_name}/unregister endpoint."""

    def test_unregister_existing_student_success(self, client, test_emails, test_activities):
        """
        Arrange: Sign up email first, then unregister
        Act: POST unregister with enrolled email
        Assert: 200 status, response confirms unregister, email removed from participants
        """
        # Arrange
        activity_name = test_activities["valid_empty"]
        email = test_emails["new_student"]
        
        # Sign up first
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert - response
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email in response.json()["message"]

        # Assert - state changed
        activities = client.get("/activities").json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_initial_participant_success(self, client, test_emails, test_activities):
        """
        Arrange: Unregister from initial participant list
        Act: POST unregister with email from initial state
        Assert: 200 status, email removed from participants
        """
        # Arrange
        activity_name = test_activities["valid"]  # Chess Club
        email = test_emails["existing_chess"]

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        activities = client.get("/activities").json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_nonexistent_email_returns_error(self, client, test_emails, test_activities):
        """
        Arrange: Email never signed up for activity
        Act: POST unregister with email not in participants
        Assert: 400 status, error indicates student not signed up
        """
        # Arrange
        activity_name = test_activities["valid_empty"]  # Soccer Team (empty)
        email = test_emails["new_student"]

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_nonexistent_activity_returns_404(self, client, test_emails, test_activities):
        """
        Arrange: Invalid activity name
        Act: POST unregister from non-existent activity
        Assert: 404 status, error message indicates activity not found
        """
        # Arrange
        activity_name = test_activities["invalid"]
        email = test_emails["new_student"]

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_decrements_participant_count(self, client, test_emails, test_activities):
        """
        Arrange: Sign up email first, record initial count
        Act: POST unregister
        Assert: Participant count decreases by exactly 1
        """
        # Arrange
        activity_name = test_activities["valid"]
        email = test_emails["existing_chess"]
        
        # Get initial count
        activities_before = client.get("/activities").json()
        initial_count = len(activities_before[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        activities_after = client.get("/activities").json()
        final_count = len(activities_after[activity_name]["participants"])
        assert final_count == initial_count - 1

    def test_unregister_different_emails_independent(self, client, test_emails, test_activities):
        """
        Arrange: Multiple students in activity
        Act: Unregister one student
        Assert: Only that student is removed, others remain
        """
        # Arrange
        activity_name = test_activities["valid"]  # Chess Club (michael and daniel)
        email_to_remove = test_emails["existing_chess"]
        email_to_keep = "daniel@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )

        # Assert
        assert response.status_code == 200
        activities = client.get("/activities").json()
        assert email_to_remove not in activities[activity_name]["participants"]
        assert email_to_keep in activities[activity_name]["participants"]

    def test_signup_after_unregister_success(self, client, test_emails, test_activities):
        """
        Arrange: Sign up email, unregister, then sign up again
        Act: Signup → Unregister → Signup
        Assert: All three operations succeed, final state has email in participants
        """
        # Arrange
        activity_name = test_activities["valid_empty"]
        email = test_emails["new_student"]

        # Act - Sign up
        signup1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Act - Unregister
        unregister = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Act - Sign up again
        signup2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert signup1.status_code == 200
        assert unregister.status_code == 200
        assert signup2.status_code == 200

        # Final state check
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]
