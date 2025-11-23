"""VLM analysis API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from macagent.core.models import ScreenAnalysisRequest, VLMAnalysisResult
from macagent.vlm.vlm_client import VLMClient
from macagent.api.dependencies import get_vlm_client
from macagent.core.logger import logger


router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("/screen", response_model=VLMAnalysisResult)
async def analyze_screen(
    request: ScreenAnalysisRequest,
    vlm_client: VLMClient = Depends(get_vlm_client),
):
    """
    Analyze a screenshot using VLM.

    This endpoint:
    1. Receives base64 encoded screenshot
    2. Sends to VLM for analysis
    3. Returns available actions and recommendations
    """
    try:
        result = vlm_client.analyze_screen(
            screenshot_base64=request.screenshot,
            task_context=request.context,
            session_id=str(request.session_id),
        )

        # Check for payment screen
        is_payment = vlm_client.detect_payment_screen(request.screenshot)

        if is_payment:
            logger.warning(
                f"Payment screen detected for session {request.session_id}"
            )
            # You might want to add a warning field to the response
            # or automatically stop the session

        return result

    except Exception as e:
        logger.error(f"Failed to analyze screen: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/element")
async def analyze_element(
    request: ScreenAnalysisRequest,
    vlm_client: VLMClient = Depends(get_vlm_client),
):
    """
    Analyze a specific UI element.

    This is a simplified version that focuses on a specific element
    rather than the entire screen.
    """
    try:
        # For now, use the same analysis method
        # In a real implementation, you might want to:
        # 1. Crop the image to focus on the element
        # 2. Use a different prompt
        # 3. Return element-specific information

        result = vlm_client.analyze_screen(
            screenshot_base64=request.screenshot,
            task_context=request.context,
            session_id=str(request.session_id),
        )

        return result

    except Exception as e:
        logger.error(f"Failed to analyze element: {e}")
        raise HTTPException(status_code=500, detail=str(e))
