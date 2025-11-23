"""Action execution API endpoints."""

from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from macagent.core.models import Action, ActionStatus
from macagent.database.interface import DatabaseInterface
from macagent.vlm.action_executor import ActionExecutor
from macagent.api.dependencies import get_database, get_action_executor
from macagent.core.logger import logger


router = APIRouter(prefix="/actions", tags=["actions"])


class ActionRequest(BaseModel):
    """Request to execute next action."""
    session_id: UUID


class ActionConfirmRequest(BaseModel):
    """Confirm action execution."""
    confirmed: bool = True


@router.post("")
async def request_next_action(
    request: ActionRequest,
    db: DatabaseInterface = Depends(get_database),
):
    """
    Request next action for a session.

    This would typically:
    1. Capture current screen
    2. Analyze with VLM
    3. Return recommended action for confirmation
    """
    try:
        session = await db.get_session(request.session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # TODO: Implement actual VLM analysis
        # For now, return a placeholder response
        return {
            "message": "Next action requested",
            "session_id": request.session_id,
            "note": "Implement VLM analysis to get actual next action"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to request next action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{action_id}", response_model=Action)
async def get_action(
    action_id: UUID,
    db: DatabaseInterface = Depends(get_database),
):
    """Get action by ID."""
    action = await db.get_action(action_id)

    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    return action


@router.post("/{action_id}/confirm")
async def confirm_action(
    action_id: UUID,
    request: ActionConfirmRequest,
    db: DatabaseInterface = Depends(get_database),
    executor: ActionExecutor = Depends(get_action_executor),
):
    """
    Confirm and execute an action.

    This endpoint:
    1. Retrieves the pending action
    2. Executes it if confirmed
    3. Updates the action status
    """
    try:
        action = await db.get_action(action_id)

        if not action:
            raise HTTPException(status_code=404, detail="Action not found")

        if action.status != ActionStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot confirm action in {action.status} state"
            )

        if not request.confirmed:
            action.status = ActionStatus.FAILED
            action.error_message = "Action not confirmed by user"
            updated = await db.update_action(action)
            return updated

        # Execute the action
        executed = executor.execute(action)

        # Update in database
        updated = await db.update_action(executed)

        return updated

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to confirm action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{action_id}/retry")
async def retry_action(
    action_id: UUID,
    db: DatabaseInterface = Depends(get_database),
    executor: ActionExecutor = Depends(get_action_executor),
):
    """Retry a failed action."""
    try:
        action = await db.get_action(action_id)

        if not action:
            raise HTTPException(status_code=404, detail="Action not found")

        if action.status != ActionStatus.FAILED:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot retry action in {action.status} state"
            )

        # Reset action status
        action.status = ActionStatus.PENDING
        action.error_message = None

        # Execute the action
        executed = executor.execute(action)

        # Update in database
        updated = await db.update_action(executed)

        return updated

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retry action: {e}")
        raise HTTPException(status_code=500, detail=str(e))
