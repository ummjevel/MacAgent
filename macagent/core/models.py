"""Data models for MacAgent."""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class ActionType(str, Enum):
    """Action types."""

    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    WAIT = "wait"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"


class ActionStatus(str, Enum):
    """Action execution status."""

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class SessionStatus(str, Enum):
    """Session status."""

    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Coordinates(BaseModel):
    """Screen coordinates."""

    x: int
    y: int


class ActionTarget(BaseModel):
    """Action target information."""

    element: str
    coordinates: Optional[Coordinates] = None
    confidence: float = Field(ge=0.0, le=1.0)


class Action(BaseModel):
    """Action model."""

    id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    step_number: int
    action_type: ActionType
    target_element: Optional[Dict[str, Any]] = None
    target: Optional[ActionTarget] = None
    text: Optional[str] = None  # For TYPE actions
    screenshot_url: Optional[str] = None
    status: ActionStatus = ActionStatus.PENDING
    execution_time: Optional[int] = None  # milliseconds
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None


class Session(BaseModel):
    """Session model."""

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    app_name: str
    task_description: str
    status: SessionStatus = SessionStatus.RUNNING
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    current_step: int = 0


class VLMAnalysisResult(BaseModel):
    """VLM analysis result."""

    current_screen: str
    available_actions: List[ActionTarget]
    recommended_action: Optional[Action] = None
    reasoning: Optional[str] = None


class ScreenAnalysisRequest(BaseModel):
    """Screen analysis request."""

    session_id: UUID
    screenshot: str  # base64 encoded
    context: Optional[str] = None


class NextActionPreview(BaseModel):
    """Next action preview."""

    type: ActionType
    target: str
    description: str


class SessionCreateRequest(BaseModel):
    """Session creation request."""

    user_id: UUID
    app_name: str
    task: str
    consent_confirmed: bool = False


class SessionCreateResponse(BaseModel):
    """Session creation response."""

    session_id: UUID
    status: SessionStatus
    current_step: int
    next_action_preview: Optional[NextActionPreview] = None


class User(BaseModel):
    """User model."""

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    consent_given: bool = False
    consent_timestamp: Optional[datetime] = None


class Route(BaseModel):
    """Route tracking model."""

    id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    planned_route: List[Dict[str, Any]]
    actual_route: List[Dict[str, Any]]
    created_at: datetime = Field(default_factory=datetime.utcnow)
