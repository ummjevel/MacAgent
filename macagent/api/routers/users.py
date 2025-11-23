"""User management API endpoints."""

from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from macagent.core.models import User
from macagent.database.interface import DatabaseInterface
from macagent.api.dependencies import get_database
from macagent.core.logger import logger


router = APIRouter(prefix="/users", tags=["users"])


class ConsentRequest(BaseModel):
    """User consent request."""
    user_id: UUID
    consent_given: bool


class ConsentResponse(BaseModel):
    """User consent response."""
    user_id: UUID
    consent_given: bool
    message: str


@router.post("/consent", response_model=ConsentResponse)
async def save_consent(
    request: ConsentRequest,
    db: DatabaseInterface = Depends(get_database),
):
    """Save or update user consent."""
    try:
        # Check if user exists
        user = await db.get_user(request.user_id)

        if user:
            # Update existing user
            updated = await db.update_user_consent(
                request.user_id,
                request.consent_given
            )
            message = "Consent updated"
        else:
            # Create new user
            user = User(
                id=request.user_id,
                consent_given=request.consent_given,
            )
            updated = await db.create_user(user)
            message = "User created with consent"

        return ConsentResponse(
            user_id=updated.id,
            consent_given=updated.consent_given,
            message=message,
        )

    except Exception as e:
        logger.error(f"Failed to save consent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/consent/{user_id}")
async def get_consent(
    user_id: UUID,
    db: DatabaseInterface = Depends(get_database),
):
    """Get user consent status."""
    user = await db.get_user(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user.id,
        "consent_given": user.consent_given,
        "consent_timestamp": user.consent_timestamp,
    }
