"""Tests for sessions API endpoints."""

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


class TestSessionsAPI:
    """Test sessions API endpoints."""

    def test_create_session(self, client, user_id):
        """Test creating a new session."""
        response = client.post(
            "/api/v1/sessions",
            json={
                "user_id": str(user_id),
                "app_name": "Test App",
                "task": "Test task",
                "consent_confirmed": True,
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "session_id" in data
        assert data["status"] == SessionStatus.RUNNING.value
        assert data["current_step"] == 0

    def test_get_session(self, client, user_id):
        """Test retrieving a session."""
        # First create a session
        create_response = client.post(
            "/api/v1/sessions",
            json={
                "user_id": str(user_id),
                "app_name": "Test App",
                "task": "Test task",
                "consent_confirmed": True,
            },
        )

        session_id = create_response.json()["session_id"]

        # Get the session
        response = client.get(f"/api/v1/sessions/{session_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == session_id
        assert data["app_name"] == "Test App"

    def test_get_nonexistent_session(self, client):
        """Test getting a session that doesn't exist."""
        response = client.get(f"/api/v1/sessions/{uuid4()}")

        assert response.status_code == 404

    def test_pause_session(self, client, user_id):
        """Test pausing a session."""
        # Create a session
        create_response = client.post(
            "/api/v1/sessions",
            json={
                "user_id": str(user_id),
                "app_name": "Test App",
                "task": "Test task",
                "consent_confirmed": True,
            },
        )

        session_id = create_response.json()["session_id"]

        # Pause the session
        response = client.patch(f"/api/v1/sessions/{session_id}/pause")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == SessionStatus.PAUSED.value

    def test_resume_session(self, client, user_id):
        """Test resuming a paused session."""
        # Create and pause a session
        create_response = client.post(
            "/api/v1/sessions",
            json={
                "user_id": str(user_id),
                "app_name": "Test App",
                "task": "Test task",
                "consent_confirmed": True,
            },
        )

        session_id = create_response.json()["session_id"]
        client.patch(f"/api/v1/sessions/{session_id}/pause")

        # Resume the session
        response = client.patch(f"/api/v1/sessions/{session_id}/resume")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == SessionStatus.RUNNING.value

    def test_cancel_session(self, client, user_id):
        """Test canceling a session."""
        # Create a session
        create_response = client.post(
            "/api/v1/sessions",
            json={
                "user_id": str(user_id),
                "app_name": "Test App",
                "task": "Test task",
                "consent_confirmed": True,
            },
        )

        session_id = create_response.json()["session_id"]

        # Cancel the session
        response = client.patch(f"/api/v1/sessions/{session_id}/cancel")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == SessionStatus.CANCELLED.value

    def test_delete_session(self, client, user_id):
        """Test deleting a session."""
        # Create a session
        create_response = client.post(
            "/api/v1/sessions",
            json={
                "user_id": str(user_id),
                "app_name": "Test App",
                "task": "Test task",
                "consent_confirmed": True,
            },
        )

        session_id = create_response.json()["session_id"]

        # Delete the session
        response = client.delete(f"/api/v1/sessions/{session_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["deleted"] is True

        # Verify it's gone
        get_response = client.get(f"/api/v1/sessions/{session_id}")
        assert get_response.status_code == 404

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "MacAgent API"
        assert data["status"] == "running"

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
