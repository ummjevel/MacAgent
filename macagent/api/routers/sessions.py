"""Session management API endpoints."""

from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from macagent.core.models import (
    Session,
    SessionCreateRequest,
    SessionCreateResponse,
    SessionStatus,
    NextActionPreview,
    ActionType,
)
from macagent.database.interface import DatabaseInterface
from macagent.api.dependencies import get_database
from macagent.core.logger import logger


router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionCreateResponse)
async def create_session(
    request: SessionCreateRequest,
    db: DatabaseInterface = Depends(get_database),
):
    """Create a new automation session."""
    try:
        # Create session
        session = Session(
            user_id=request.user_id,
            app_name=request.app_name,
            task_description=request.task,
            status=SessionStatus.RUNNING,
        )

        created_session = await db.create_session(session)

        # TODO: In real implementation, analyze initial screen and provide preview
        next_action_preview = NextActionPreview(
            type=ActionType.CLICK,
            target="Starting point",
            description=f"Begin task: {request.task}",
        )

        return SessionCreateResponse(
            session_id=created_session.id,
            status=created_session.status,
            current_step=created_session.current_step,
            next_action_preview=next_action_preview,
        )

    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}", response_model=Session)
async def get_session(
    session_id: UUID,
    db: DatabaseInterface = Depends(get_database),
):
    """Get session by ID."""
    session = await db.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session


@router.patch("/{session_id}/pause")
async def pause_session(
    session_id: UUID,
    db: DatabaseInterface = Depends(get_database),
):
    """Pause a running session."""
    session = await db.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != SessionStatus.RUNNING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot pause session in {session.status} state"
        )

    session.status = SessionStatus.PAUSED
    updated = await db.update_session(session)

    return {"session_id": session_id, "status": updated.status}


@router.patch("/{session_id}/resume")
async def resume_session(
    session_id: UUID,
    db: DatabaseInterface = Depends(get_database),
):
    """Resume a paused session."""
    session = await db.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != SessionStatus.PAUSED:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot resume session in {session.status} state"
        )

    session.status = SessionStatus.RUNNING
    updated = await db.update_session(session)

    return {"session_id": session_id, "status": updated.status}


@router.patch("/{session_id}/cancel")
async def cancel_session(
    session_id: UUID,
    db: DatabaseInterface = Depends(get_database),
):
    """Cancel a session."""
    session = await db.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = SessionStatus.CANCELLED
    session.ended_at = datetime.utcnow()
    updated = await db.update_session(session)

    return {"session_id": session_id, "status": updated.status}


@router.delete("/{session_id}")
async def delete_session(
    session_id: UUID,
    db: DatabaseInterface = Depends(get_database),
):
    """Delete a session and all associated data."""
    deleted = await db.delete_session(session_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"session_id": session_id, "deleted": True}
