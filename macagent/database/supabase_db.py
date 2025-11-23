"""Supabase database implementation."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from supabase import create_client, Client
from macagent.core.models import User, Session, Action, Route, SessionStatus, ActionStatus
from macagent.database.interface import DatabaseInterface
from macagent.core.config import settings
from macagent.core.logger import logger


class SupabaseDatabase(DatabaseInterface):
    """
    Supabase database implementation.

    Requires SUPABASE_URL and SUPABASE_KEY environment variables.
    """

    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        """
        Initialize Supabase client.

        Args:
            url: Supabase project URL (defaults to settings)
            key: Supabase anon key (defaults to settings)
        """
        self.url = url or settings.supabase_url
        self.key = key or settings.supabase_key

        if not self.url or not self.key:
            raise ValueError(
                "Supabase URL and KEY are required. "
                "Set SUPABASE_URL and SUPABASE_KEY environment variables."
            )

        self.client: Client = create_client(self.url, self.key)
        logger.info("Supabase database initialized")

    # User operations
    async def create_user(self, user: User) -> User:
        """Create a new user."""
        data = {
            "id": str(user.id),
            "created_at": user.created_at.isoformat(),
            "consent_given": user.consent_given,
            "consent_timestamp": user.consent_timestamp.isoformat() if user.consent_timestamp else None,
        }

        result = self.client.table("users").insert(data).execute()
        logger.info(f"User created in Supabase: {user.id}")
        return user

    async def get_user(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = self.client.table("users").select("*").eq("id", str(user_id)).execute()

        if not result.data:
            return None

        data = result.data[0]
        return User(
            id=UUID(data["id"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            consent_given=data["consent_given"],
            consent_timestamp=datetime.fromisoformat(data["consent_timestamp"]) if data["consent_timestamp"] else None,
        )

    async def update_user_consent(self, user_id: UUID, consent_given: bool) -> User:
        """Update user consent."""
        now = datetime.utcnow()
        data = {
            "consent_given": consent_given,
            "consent_timestamp": now.isoformat(),
        }

        self.client.table("users").update(data).eq("id", str(user_id)).execute()
        logger.info(f"User consent updated in Supabase: {user_id}")

        user = await self.get_user(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")
        return user

    # Session operations
    async def create_session(self, session: Session) -> Session:
        """Create a new session."""
        data = {
            "id": str(session.id),
            "user_id": str(session.user_id),
            "app_name": session.app_name,
            "task_description": session.task_description,
            "status": session.status.value,
            "started_at": session.started_at.isoformat(),
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
        }

        self.client.table("sessions").insert(data).execute()
        logger.info(f"Session created in Supabase: {session.id}")
        return session

    async def get_session(self, session_id: UUID) -> Optional[Session]:
        """Get session by ID."""
        result = self.client.table("sessions").select("*").eq("id", str(session_id)).execute()

        if not result.data:
            return None

        data = result.data[0]
        return Session(
            id=UUID(data["id"]),
            user_id=UUID(data["user_id"]),
            app_name=data["app_name"],
            task_description=data["task_description"],
            status=SessionStatus(data["status"]),
            started_at=datetime.fromisoformat(data["started_at"]),
            ended_at=datetime.fromisoformat(data["ended_at"]) if data["ended_at"] else None,
            current_step=data.get("current_step", 0),
        )

    async def update_session(self, session: Session) -> Session:
        """Update session."""
        data = {
            "status": session.status.value,
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            "current_step": session.current_step,
        }

        self.client.table("sessions").update(data).eq("id", str(session.id)).execute()
        logger.info(f"Session updated in Supabase: {session.id}")
        return session

    async def list_sessions(
        self, user_id: Optional[UUID] = None, limit: int = 100
    ) -> List[Session]:
        """List sessions, optionally filtered by user."""
        query = self.client.table("sessions").select("*")

        if user_id:
            query = query.eq("user_id", str(user_id))

        result = query.order("started_at", desc=True).limit(limit).execute()

        sessions = []
        for data in result.data:
            sessions.append(
                Session(
                    id=UUID(data["id"]),
                    user_id=UUID(data["user_id"]),
                    app_name=data["app_name"],
                    task_description=data["task_description"],
                    status=SessionStatus(data["status"]),
                    started_at=datetime.fromisoformat(data["started_at"]),
                    ended_at=datetime.fromisoformat(data["ended_at"]) if data["ended_at"] else None,
                    current_step=data.get("current_step", 0),
                )
            )

        return sessions

    async def delete_session(self, session_id: UUID) -> bool:
        """Delete session."""
        # Delete associated actions first
        self.client.table("actions").delete().eq("session_id", str(session_id)).execute()

        # Delete session
        result = self.client.table("sessions").delete().eq("id", str(session_id)).execute()

        logger.info(f"Session deleted from Supabase: {session_id}")
        return len(result.data) > 0

    # Action operations
    async def create_action(self, action: Action) -> Action:
        """Create a new action."""
        data = {
            "id": str(action.id),
            "session_id": str(action.session_id),
            "step_number": action.step_number,
            "action_type": action.action_type.value,
            "target_element": action.target_element,
            "screenshot_url": action.screenshot_url,
            "status": action.status.value,
            "execution_time": action.execution_time,
            "timestamp": action.timestamp.isoformat(),
            "error_message": action.error_message,
        }

        self.client.table("actions").insert(data).execute()
        logger.debug(f"Action created in Supabase: {action.id}")
        return action

    async def get_action(self, action_id: UUID) -> Optional[Action]:
        """Get action by ID."""
        result = self.client.table("actions").select("*").eq("id", str(action_id)).execute()

        if not result.data:
            return None

        data = result.data[0]
        return self._action_from_dict(data)

    async def update_action(self, action: Action) -> Action:
        """Update action."""
        data = {
            "status": action.status.value,
            "execution_time": action.execution_time,
            "error_message": action.error_message,
        }

        self.client.table("actions").update(data).eq("id", str(action.id)).execute()
        logger.debug(f"Action updated in Supabase: {action.id}")
        return action

    async def list_actions(self, session_id: UUID, limit: int = 1000) -> List[Action]:
        """List actions for a session."""
        result = (
            self.client.table("actions")
            .select("*")
            .eq("session_id", str(session_id))
            .order("step_number")
            .limit(limit)
            .execute()
        )

        return [self._action_from_dict(data) for data in result.data]

    # Route operations
    async def create_route(self, route: Route) -> Route:
        """Create a new route."""
        data = {
            "id": str(route.id),
            "session_id": str(route.session_id),
            "planned_route": route.planned_route,
            "actual_route": route.actual_route,
            "created_at": route.created_at.isoformat(),
        }

        self.client.table("routes").insert(data).execute()
        logger.info(f"Route created in Supabase: {route.id}")
        return route

    async def get_route(self, route_id: UUID) -> Optional[Route]:
        """Get route by ID."""
        result = self.client.table("routes").select("*").eq("id", str(route_id)).execute()

        if not result.data:
            return None

        data = result.data[0]
        return Route(
            id=UUID(data["id"]),
            session_id=UUID(data["session_id"]),
            planned_route=data["planned_route"],
            actual_route=data["actual_route"],
            created_at=datetime.fromisoformat(data["created_at"]),
        )

    async def get_route_by_session(self, session_id: UUID) -> Optional[Route]:
        """Get route for a session."""
        result = (
            self.client.table("routes")
            .select("*")
            .eq("session_id", str(session_id))
            .execute()
        )

        if not result.data:
            return None

        data = result.data[0]
        return Route(
            id=UUID(data["id"]),
            session_id=UUID(data["session_id"]),
            planned_route=data["planned_route"],
            actual_route=data["actual_route"],
            created_at=datetime.fromisoformat(data["created_at"]),
        )

    async def update_route(self, route: Route) -> Route:
        """Update route."""
        data = {
            "planned_route": route.planned_route,
            "actual_route": route.actual_route,
        }

        self.client.table("routes").update(data).eq("id", str(route.id)).execute()
        logger.info(f"Route updated in Supabase: {route.id}")
        return route

    def _action_from_dict(self, data: dict) -> Action:
        """Convert dict to Action model."""
        from macagent.core.models import ActionType, ActionStatus

        return Action(
            id=UUID(data["id"]),
            session_id=UUID(data["session_id"]),
            step_number=data["step_number"],
            action_type=ActionType(data["action_type"]),
            target_element=data["target_element"],
            screenshot_url=data["screenshot_url"],
            status=ActionStatus(data["status"]),
            execution_time=data["execution_time"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            error_message=data["error_message"],
        )
