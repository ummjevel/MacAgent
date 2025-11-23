"""Mock database implementation for testing and development."""

from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime
from macagent.core.models import User, Session, Action, Route
from macagent.database.interface import DatabaseInterface
from macagent.core.logger import logger


class MockDatabase(DatabaseInterface):
    """
    Mock in-memory database implementation.

    This is useful for development and testing without requiring
    an actual Supabase connection.
    """

    def __init__(self):
        """Initialize mock database with empty storage."""
        self.users: Dict[UUID, User] = {}
        self.sessions: Dict[UUID, Session] = {}
        self.actions: Dict[UUID, Action] = {}
        self.routes: Dict[UUID, Route] = {}
        logger.info("Mock database initialized")

    # User operations
    async def create_user(self, user: User) -> User:
        """Create a new user."""
        self.users[user.id] = user
        logger.info(f"User created: {user.id}")
        return user

    async def get_user(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)

    async def update_user_consent(
        self, user_id: UUID, consent_given: bool
    ) -> User:
        """Update user consent."""
        user = self.users.get(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")

        user.consent_given = consent_given
        user.consent_timestamp = datetime.utcnow()
        self.users[user_id] = user
        logger.info(f"User consent updated: {user_id} -> {consent_given}")
        return user

    # Session operations
    async def create_session(self, session: Session) -> Session:
        """Create a new session."""
        self.sessions[session.id] = session
        logger.info(f"Session created: {session.id}")
        return session

    async def get_session(self, session_id: UUID) -> Optional[Session]:
        """Get session by ID."""
        return self.sessions.get(session_id)

    async def update_session(self, session: Session) -> Session:
        """Update session."""
        if session.id not in self.sessions:
            raise ValueError(f"Session not found: {session.id}")

        self.sessions[session.id] = session
        logger.info(f"Session updated: {session.id}")
        return session

    async def list_sessions(
        self, user_id: Optional[UUID] = None, limit: int = 100
    ) -> List[Session]:
        """List sessions, optionally filtered by user."""
        sessions = list(self.sessions.values())

        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]

        # Sort by started_at descending
        sessions.sort(key=lambda s: s.started_at, reverse=True)

        return sessions[:limit]

    async def delete_session(self, session_id: UUID) -> bool:
        """Delete session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            # Also delete associated actions
            actions_to_delete = [
                aid for aid, action in self.actions.items()
                if action.session_id == session_id
            ]
            for aid in actions_to_delete:
                del self.actions[aid]
            logger.info(f"Session deleted: {session_id}")
            return True
        return False

    # Action operations
    async def create_action(self, action: Action) -> Action:
        """Create a new action."""
        self.actions[action.id] = action
        logger.debug(f"Action created: {action.id}")
        return action

    async def get_action(self, action_id: UUID) -> Optional[Action]:
        """Get action by ID."""
        return self.actions.get(action_id)

    async def update_action(self, action: Action) -> Action:
        """Update action."""
        if action.id not in self.actions:
            raise ValueError(f"Action not found: {action.id}")

        self.actions[action.id] = action
        logger.debug(f"Action updated: {action.id}")
        return action

    async def list_actions(
        self, session_id: UUID, limit: int = 1000
    ) -> List[Action]:
        """List actions for a session."""
        actions = [
            action for action in self.actions.values()
            if action.session_id == session_id
        ]

        # Sort by step_number
        actions.sort(key=lambda a: a.step_number)

        return actions[:limit]

    # Route operations
    async def create_route(self, route: Route) -> Route:
        """Create a new route."""
        self.routes[route.id] = route
        logger.info(f"Route created: {route.id}")
        return route

    async def get_route(self, route_id: UUID) -> Optional[Route]:
        """Get route by ID."""
        return self.routes.get(route_id)

    async def get_route_by_session(self, session_id: UUID) -> Optional[Route]:
        """Get route for a session."""
        for route in self.routes.values():
            if route.session_id == session_id:
                return route
        return None

    async def update_route(self, route: Route) -> Route:
        """Update route."""
        if route.id not in self.routes:
            raise ValueError(f"Route not found: {route.id}")

        self.routes[route.id] = route
        logger.info(f"Route updated: {route.id}")
        return route

    # Utility methods
    def clear_all(self):
        """Clear all data (useful for testing)."""
        self.users.clear()
        self.sessions.clear()
        self.actions.clear()
        self.routes.clear()
        logger.warning("All mock database data cleared")

    def get_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        return {
            "users": len(self.users),
            "sessions": len(self.sessions),
            "actions": len(self.actions),
            "routes": len(self.routes),
        }
