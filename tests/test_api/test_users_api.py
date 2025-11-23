"""Tests for users API endpoints."""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from macagent.api.main import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


class TestUsersAPI:
    """Test users API endpoints."""

    def test_save_consent_new_user(self, client):
        """Test saving consent for a new user."""
        user_id = uuid4()

        response = client.post(
            "/api/v1/users/consent",
            json={
                "user_id": str(user_id),
                "consent_given": True,
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["user_id"] == str(user_id)
        assert data["consent_given"] is True
        assert "created" in data["message"].lower()

    def test_update_consent_existing_user(self, client):
        """Test updating consent for an existing user."""
        user_id = uuid4()

        # Create user with consent
        client.post(
            "/api/v1/users/consent",
            json={
                "user_id": str(user_id),
                "consent_given": True,
            },
        )

        # Update consent
        response = client.post(
            "/api/v1/users/consent",
            json={
                "user_id": str(user_id),
                "consent_given": False,
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["consent_given"] is False
        assert "updated" in data["message"].lower()

    def test_get_consent(self, client):
        """Test getting consent status."""
        user_id = uuid4()

        # Create user with consent
        client.post(
            "/api/v1/users/consent",
            json={
                "user_id": str(user_id),
                "consent_given": True,
            },
        )

        # Get consent
        response = client.get(f"/api/v1/users/consent/{user_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["user_id"] == str(user_id)
        assert data["consent_given"] is True
        assert "consent_timestamp" in data

    def test_get_consent_nonexistent_user(self, client):
        """Test getting consent for a user that doesn't exist."""
        response = client.get(f"/api/v1/users/consent/{uuid4()}")

        assert response.status_code == 404
