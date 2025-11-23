"""Tests for mock database implementation."""

import pytest
from uuid import uuid4
from datetime import datetime
from macagent.database.mock_db import MockDatabase
from macagent.core.models import (
    User,
    Session,
    Action,
    Route,
    SessionStatus,
    ActionType,
    ActionStatus,
    ActionTarget,
    Coordinates,
)


class TestMockDatabase:
    """Test MockDatabase class."""

    @pytest.fixture
    def db(self):
        """Create a fresh mock database for each test."""
        return MockDatabase()

    @pytest.fixture
    def sample_user(self):
        """Create a sample user."""
        return User(
            id=uuid4(),
            consent_given=True,
        )

    @pytest.fixture
    def sample_session(self, sample_user):
        """Create a sample session."""
        return Session(
            id=uuid4(),
            user_id=sample_user.id,
            app_name="Test App",
            task_description="Test task",
        )

    # User tests
    @pytest.mark.asyncio
    async def test_create_and_get_user(self, db, sample_user):
        """Test creating and retrieving a user."""
        created = await db.create_user(sample_user)

        assert created.id == sample_user.id
        assert created.consent_given == sample_user.consent_given

        retrieved = await db.get_user(sample_user.id)
        assert retrieved is not None
        assert retrieved.id == sample_user.id

    @pytest.mark.asyncio
    async def test_get_nonexistent_user(self, db):
        """Test getting a user that doesn't exist."""
        result = await db.get_user(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_update_user_consent(self, db, sample_user):
        """Test updating user consent."""
        await db.create_user(sample_user)

        updated = await db.update_user_consent(sample_user.id, False)

        assert updated.consent_given is False
        assert updated.consent_timestamp is not None

    @pytest.mark.asyncio
    async def test_update_consent_nonexistent_user(self, db):
        """Test updating consent for nonexistent user."""
        with pytest.raises(ValueError):
            await db.update_user_consent(uuid4(), True)

    # Session tests
    @pytest.mark.asyncio
    async def test_create_and_get_session(self, db, sample_session):
        """Test creating and retrieving a session."""
        created = await db.create_session(sample_session)

        assert created.id == sample_session.id
        assert created.status == SessionStatus.RUNNING

        retrieved = await db.get_session(sample_session.id)
        assert retrieved is not None
        assert retrieved.id == sample_session.id

    @pytest.mark.asyncio
    async def test_update_session(self, db, sample_session):
        """Test updating a session."""
        await db.create_session(sample_session)

        sample_session.status = SessionStatus.COMPLETED
        sample_session.ended_at = datetime.utcnow()

        updated = await db.update_session(sample_session)

        assert updated.status == SessionStatus.COMPLETED
        assert updated.ended_at is not None

    @pytest.mark.asyncio
    async def test_list_sessions(self, db, sample_user):
        """Test listing sessions."""
        # Create multiple sessions
        session1 = Session(
            id=uuid4(),
            user_id=sample_user.id,
            app_name="App 1",
            task_description="Task 1",
        )
        session2 = Session(
            id=uuid4(),
            user_id=sample_user.id,
            app_name="App 2",
            task_description="Task 2",
        )

        await db.create_session(session1)
        await db.create_session(session2)

        # List all sessions
        sessions = await db.list_sessions()
        assert len(sessions) == 2

        # List sessions for user
        user_sessions = await db.list_sessions(user_id=sample_user.id)
        assert len(user_sessions) == 2

    @pytest.mark.asyncio
    async def test_delete_session(self, db, sample_session):
        """Test deleting a session."""
        await db.create_session(sample_session)

        # Create an action for this session
        action = Action(
            id=uuid4(),
            session_id=sample_session.id,
            step_number=1,
            action_type=ActionType.CLICK,
        )
        await db.create_action(action)

        # Delete session
        deleted = await db.delete_session(sample_session.id)
        assert deleted is True

        # Verify session is gone
        retrieved_session = await db.get_session(sample_session.id)
        assert retrieved_session is None

        # Verify associated actions are gone
        retrieved_action = await db.get_action(action.id)
        assert retrieved_action is None

    # Action tests
    @pytest.mark.asyncio
    async def test_create_and_get_action(self, db, sample_session):
        """Test creating and retrieving an action."""
        action = Action(
            id=uuid4(),
            session_id=sample_session.id,
            step_number=1,
            action_type=ActionType.CLICK,
            target=ActionTarget(
                element="Button",
                coordinates=Coordinates(x=100, y=200),
                confidence=0.9,
            ),
        )

        created = await db.create_action(action)
        assert created.id == action.id

        retrieved = await db.get_action(action.id)
        assert retrieved is not None
        assert retrieved.id == action.id
        assert retrieved.action_type == ActionType.CLICK

    @pytest.mark.asyncio
    async def test_update_action(self, db, sample_session):
        """Test updating an action."""
        action = Action(
            id=uuid4(),
            session_id=sample_session.id,
            step_number=1,
            action_type=ActionType.CLICK,
        )

        await db.create_action(action)

        action.status = ActionStatus.SUCCESS
        action.execution_time = 500

        updated = await db.update_action(action)
        assert updated.status == ActionStatus.SUCCESS
        assert updated.execution_time == 500

    @pytest.mark.asyncio
    async def test_list_actions(self, db, sample_session):
        """Test listing actions for a session."""
        # Create multiple actions
        action1 = Action(
            id=uuid4(),
            session_id=sample_session.id,
            step_number=1,
            action_type=ActionType.CLICK,
        )
        action2 = Action(
            id=uuid4(),
            session_id=sample_session.id,
            step_number=2,
            action_type=ActionType.TYPE,
        )

        await db.create_action(action1)
        await db.create_action(action2)

        actions = await db.list_actions(sample_session.id)
        assert len(actions) == 2
        # Should be sorted by step_number
        assert actions[0].step_number == 1
        assert actions[1].step_number == 2

    # Route tests
    @pytest.mark.asyncio
    async def test_create_and_get_route(self, db, sample_session):
        """Test creating and retrieving a route."""
        route = Route(
            id=uuid4(),
            session_id=sample_session.id,
            planned_route=[{"step": 1, "action": "click"}],
            actual_route=[{"step": 1, "action": "click", "success": True}],
        )

        created = await db.create_route(route)
        assert created.id == route.id

        retrieved = await db.get_route(route.id)
        assert retrieved is not None
        assert retrieved.id == route.id

    @pytest.mark.asyncio
    async def test_get_route_by_session(self, db, sample_session):
        """Test getting route by session ID."""
        route = Route(
            id=uuid4(),
            session_id=sample_session.id,
            planned_route=[],
            actual_route=[],
        )

        await db.create_route(route)

        retrieved = await db.get_route_by_session(sample_session.id)
        assert retrieved is not None
        assert retrieved.session_id == sample_session.id

    @pytest.mark.asyncio
    async def test_update_route(self, db, sample_session):
        """Test updating a route."""
        route = Route(
            id=uuid4(),
            session_id=sample_session.id,
            planned_route=[{"step": 1}],
            actual_route=[],
        )

        await db.create_route(route)

        route.actual_route = [{"step": 1, "completed": True}]
        updated = await db.update_route(route)

        assert len(updated.actual_route) == 1
        assert updated.actual_route[0]["completed"] is True

    # Utility tests
    def test_clear_all(self, db, sample_user, sample_session):
        """Test clearing all data."""
        # Create some data
        import asyncio
        asyncio.run(db.create_user(sample_user))
        asyncio.run(db.create_session(sample_session))

        # Clear all
        db.clear_all()

        # Verify empty
        stats = db.get_stats()
        assert stats["users"] == 0
        assert stats["sessions"] == 0
        assert stats["actions"] == 0
        assert stats["routes"] == 0

    def test_get_stats(self, db, sample_user, sample_session):
        """Test getting database statistics."""
        import asyncio

        # Initially empty
        stats = db.get_stats()
        assert stats["users"] == 0

        # Add data
        asyncio.run(db.create_user(sample_user))
        asyncio.run(db.create_session(sample_session))

        stats = db.get_stats()
        assert stats["users"] == 1
        assert stats["sessions"] == 1
