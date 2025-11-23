"""End-to-end integration tests."""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from macagent.api.main import create_app
from macagent.core.models import SessionStatus


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def user_id():
    """Generate a test user ID."""
    return uuid4()


class TestE2E:
    """End-to-end integration tests."""

    def test_full_session_lifecycle(self, client, user_id):
        """
        Test complete session lifecycle:
        1. Create user consent
        2. Create session
        3. Pause session
        4. Resume session
        5. Cancel session
        6. Delete session
        """
        # Step 1: Create user consent
        consent_response = client.post(
            "/api/v1/users/consent",
            json={
                "user_id": str(user_id),
                "consent_given": True,
            },
        )
        assert consent_response.status_code == 200
        assert consent_response.json()["consent_given"] is True

        # Step 2: Create session
        session_response = client.post(
            "/api/v1/sessions",
            json={
                "user_id": str(user_id),
                "app_name": "McDonald's",
                "task": "Order a Big Mac",
                "consent_confirmed": True,
            },
        )
        assert session_response.status_code == 200
        session_id = session_response.json()["session_id"]
        assert session_response.json()["status"] == SessionStatus.RUNNING.value

        # Step 3: Get session details
        get_response = client.get(f"/api/v1/sessions/{session_id}")
        assert get_response.status_code == 200
        assert get_response.json()["id"] == session_id

        # Step 4: Pause session
        pause_response = client.patch(f"/api/v1/sessions/{session_id}/pause")
        assert pause_response.status_code == 200
        assert pause_response.json()["status"] == SessionStatus.PAUSED.value

        # Step 5: Resume session
        resume_response = client.patch(f"/api/v1/sessions/{session_id}/resume")
        assert resume_response.status_code == 200
        assert resume_response.json()["status"] == SessionStatus.RUNNING.value

        # Step 6: Cancel session
        cancel_response = client.patch(f"/api/v1/sessions/{session_id}/cancel")
        assert cancel_response.status_code == 200
        assert cancel_response.json()["status"] == SessionStatus.CANCELLED.value

        # Step 7: Delete session
        delete_response = client.delete(f"/api/v1/sessions/{session_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["deleted"] is True

        # Step 8: Verify session is deleted
        verify_response = client.get(f"/api/v1/sessions/{session_id}")
        assert verify_response.status_code == 404

    def test_multiple_sessions_per_user(self, client, user_id):
        """Test creating multiple sessions for the same user."""
        # Create user consent
        client.post(
            "/api/v1/users/consent",
            json={
                "user_id": str(user_id),
                "consent_given": True,
            },
        )

        # Create multiple sessions
        session_ids = []
        for i in range(3):
            response = client.post(
                "/api/v1/sessions",
                json={
                    "user_id": str(user_id),
                    "app_name": f"App {i}",
                    "task": f"Task {i}",
                    "consent_confirmed": True,
                },
            )
            assert response.status_code == 200
            session_ids.append(response.json()["session_id"])

        # Verify all sessions can be retrieved
        for session_id in session_ids:
            response = client.get(f"/api/v1/sessions/{session_id}")
            assert response.status_code == 200

    def test_consent_update_workflow(self, client, user_id):
        """Test updating user consent."""
        # Initial consent
        response1 = client.post(
            "/api/v1/users/consent",
            json={
                "user_id": str(user_id),
                "consent_given": True,
            },
        )
        assert response1.status_code == 200
        assert response1.json()["consent_given"] is True

        # Update consent to false
        response2 = client.post(
            "/api/v1/users/consent",
            json={
                "user_id": str(user_id),
                "consent_given": False,
            },
        )
        assert response2.status_code == 200
        assert response2.json()["consent_given"] is False

        # Verify consent status
        response3 = client.get(f"/api/v1/users/consent/{user_id}")
        assert response3.status_code == 200
        assert response3.json()["consent_given"] is False

    def test_session_state_transitions(self, client, user_id):
        """Test valid and invalid session state transitions."""
        # Create session
        session_response = client.post(
            "/api/v1/sessions",
            json={
                "user_id": str(user_id),
                "app_name": "Test App",
                "task": "Test task",
                "consent_confirmed": True,
            },
        )
        session_id = session_response.json()["session_id"]

        # Valid: RUNNING -> PAUSED
        pause_response = client.patch(f"/api/v1/sessions/{session_id}/pause")
        assert pause_response.status_code == 200

        # Invalid: Try to pause again (already paused)
        pause_again = client.patch(f"/api/v1/sessions/{session_id}/pause")
        assert pause_again.status_code == 400

        # Valid: PAUSED -> RUNNING
        resume_response = client.patch(f"/api/v1/sessions/{session_id}/resume")
        assert resume_response.status_code == 200

        # Invalid: Try to resume again (already running)
        resume_again = client.patch(f"/api/v1/sessions/{session_id}/resume")
        assert resume_again.status_code == 400

        # Valid: RUNNING -> CANCELLED
        cancel_response = client.patch(f"/api/v1/sessions/{session_id}/cancel")
        assert cancel_response.status_code == 200

    def test_health_check(self, client):
        """Test that the API is healthy."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_api_root(self, client):
        """Test API root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "MacAgent API"
        assert data["version"] == "0.1.0"
        assert data["status"] == "running"
