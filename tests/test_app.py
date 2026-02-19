"""
Test suite for FastAPI activities API using AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_returns_200(self, client, reset_activities):
        """
        Arrange: Setup TestClient
        Act: Make GET request to /activities
        Assert: Verify 200 status and response contains all activities
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) == 5

    def test_get_activities_contains_chess_club(self, client, reset_activities):
        """
        Arrange: Setup TestClient
        Act: Make GET request to /activities
        Assert: Verify Chess Club activity exists with correct details
        """
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert "Chess Club" in activities
        assert activities["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
        assert activities["Chess Club"]["max_participants"] == 12

    def test_get_activities_includes_participants(self, client, reset_activities):
        """
        Arrange: Setup TestClient
        Act: Make GET request to /activities
        Assert: Verify each activity contains participants list
        """
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            assert len(activity_data["participants"]) > 0


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_student_returns_200(self, client, reset_activities):
        """
        Arrange: Prepare new student email for an activity with available spots
        Act: Make POST request to signup endpoint
        Assert: Verify 200 status and success message returned
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """
        Arrange: Prepare new student email
        Act: Make POST request to signup endpoint
        Assert: Verify student appears in activity participants list
        """
        # Arrange
        activity_name = "Programming Class"
        email = "alice@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities").json()
        assert email in activities_response[activity_name]["participants"]

    def test_signup_duplicate_student_returns_400(self, client, reset_activities):
        """
        Arrange: Select an activity with existing participant
        Act: Try to signup the same student twice
        Assert: Verify 400 status and error detail returned
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up for Chess Club

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        Arrange: Use activity name that doesn't exist
        Act: Make POST request with invalid activity name
        Assert: Verify 404 status and activity not found message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_multiple_different_students_to_same_activity(self, client, reset_activities):
        """
        Arrange: Prepare two new student emails
        Act: Sign up both students to the same activity
        Assert: Verify both are added to participants list
        """
        # Arrange
        activity_name = "Tennis Club"
        email1 = "bob@mergington.edu"
        email2 = "carol@mergington.edu"

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
        
        activities_response = client.get("/activities").json()
        participants = activities_response[activity_name]["participants"]
        assert email1 in participants
        assert email2 in participants


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant_returns_200(self, client, reset_activities):
        """
        Arrange: Select an activity with existing participant
        Act: Make DELETE request to unregister that participant
        Assert: Verify 200 status and success message returned
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

    def test_unregister_removes_participant(self, client, reset_activities):
        """
        Arrange: Select an activity with existing participant
        Act: Make DELETE request to unregister
        Assert: Verify participant is removed from activity
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "james@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities").json()
        assert email not in activities_response[activity_name]["participants"]

    def test_unregister_nonexistent_participant_returns_400(self, client, reset_activities):
        """
        Arrange: Select an activity, use email not signed up for it
        Act: Try to unregister student not in activity
        Assert: Verify 400 status and appropriate error message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notasignup@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"

    def test_unregister_from_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        Arrange: Use activity name that doesn't exist
        Act: Make DELETE request with invalid activity name
        Assert: Verify 404 status and activity not found message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_then_unregister_roundtrip(self, client, reset_activities):
        """
        Arrange: Use a new student and activity
        Act: Sign up student, then unregister them
        Assert: Verify both operations succeed and final state is correct
        """
        # Arrange
        activity_name = "Programming Class"
        email = "david@mergington.edu"

        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert signup_response.status_code == 200
        assert unregister_response.status_code == 200
        
        # Verify final state: participant not in activity
        activities_response = client.get("/activities").json()
        assert email not in activities_response[activity_name]["participants"]
