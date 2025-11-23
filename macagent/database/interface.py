"""Database interface for MacAgent."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from macagent.core.models import User, Session, Action, Route


class DatabaseInterface(ABC):
    """Abstract database interface."""

    # User operations
    @abstractmethod
    async def create_user(self, user: User) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    async def get_user(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        pass

    @abstractmethod
    async def update_user_consent(
        self, user_id: UUID, consent_given: bool
    ) -> User:
        """Update user consent."""
        pass

    # Session operations
    @abstractmethod
    async def create_session(self, session: Session) -> Session:
        """Create a new session."""
        pass

    @abstractmethod
    async def get_session(self, session_id: UUID) -> Optional[Session]:
        """Get session by ID."""
        pass

    @abstractmethod
    async def update_session(self, session: Session) -> Session:
        """Update session."""
        pass

    @abstractmethod
    async def list_sessions(
        self, user_id: Optional[UUID] = None, limit: int = 100
    ) -> List[Session]:
        """List sessions, optionally filtered by user."""
        pass

    @abstractmethod
    async def delete_session(self, session_id: UUID) -> bool:
        """Delete session."""
        pass

    # Action operations
    @abstractmethod
    async def create_action(self, action: Action) -> Action:
        """Create a new action."""
        pass

    @abstractmethod
    async def get_action(self, action_id: UUID) -> Optional[Action]:
        """Get action by ID."""
        pass

    @abstractmethod
    async def update_action(self, action: Action) -> Action:
        """Update action."""
        pass

    @abstractmethod
    async def list_actions(
        self, session_id: UUID, limit: int = 1000
    ) -> List[Action]:
        """List actions for a session."""
        pass

    # Route operations
    @abstractmethod
    async def create_route(self, route: Route) -> Route:
        """Create a new route."""
        pass

    @abstractmethod
    async def get_route(self, route_id: UUID) -> Optional[Route]:
        """Get route by ID."""
        pass

    @abstractmethod
    async def get_route_by_session(self, session_id: UUID) -> Optional[Route]:
        """Get route for a session."""
        pass

    @abstractmethod
    async def update_route(self, route: Route) -> Route:
        """Update route."""
        pass
