"""VLM client for OpenRouter API integration."""

import json
from typing import Optional, List, Dict, Any
from openai import OpenAI
from macagent.core.config import settings
from macagent.core.models import (
    VLMAnalysisResult,
    ActionTarget,
    Action,
    ActionType,
    Coordinates,
)
from macagent.core.logger import logger


class VLMClient:
    """VLM client for analyzing screens and recommending actions."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        Initialize VLM client.

        Args:
            api_key: OpenRouter API key (defaults to settings)
            base_url: OpenRouter base URL (defaults to settings)
            model: Model name (defaults to settings)
        """
        self.api_key = api_key or settings.openrouter_api_key
        self.base_url = base_url or settings.openrouter_base_url
        self.model = model or settings.vlm_model

        if not self.api_key:
            raise ValueError("OpenRouter API key is required")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def analyze_screen(
        self,
        screenshot_base64: str,
        task_context: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> VLMAnalysisResult:
        """
        Analyze screenshot and recommend actions.

        Args:
            screenshot_base64: Base64 encoded screenshot
            task_context: Context about the current task
            session_id: Session ID for logging

        Returns:
            VLM analysis result with recommended actions
        """
        try:
            prompt = self._build_prompt(task_context)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{screenshot_base64}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=2000,
                temperature=0.3,
            )

            # Parse response
            result = self._parse_response(response.choices[0].message.content)

            logger.info(
                f"Screen analyzed successfully (session: {session_id}): "
                f"{result.current_screen}"
            )

            return result

        except Exception as e:
            logger.error(f"Failed to analyze screen: {e}")
            raise

    def _build_prompt(self, task_context: Optional[str] = None) -> str:
        """Build analysis prompt."""
        base_prompt = """You are a UI automation assistant. Analyze this screenshot and provide:

1. A description of the current screen
2. All available interactive elements (buttons, inputs, etc.) with their approximate coordinates
3. The recommended next action to accomplish the task

Return your response in the following JSON format:
{
    "current_screen": "Description of what's shown",
    "available_actions": [
        {
            "element": "Element description",
            "coordinates": {"x": 100, "y": 200},
            "confidence": 0.95
        }
    ],
    "recommended_action": {
        "action_type": "click|type|scroll|wait",
        "target": "Element to interact with",
        "text": "Text to type (if action_type is 'type')",
        "coordinates": {"x": 100, "y": 200},
        "reasoning": "Why this action is recommended"
    }
}

Important:
- Provide coordinates in screen pixels
- Confidence should be between 0.0 and 1.0
- Only recommend safe actions that won't trigger payments or irreversible changes
"""

        if task_context:
            base_prompt += f"\n\nTask context: {task_context}"

        return base_prompt

    def _parse_response(self, response_text: str) -> VLMAnalysisResult:
        """
        Parse VLM response into structured result.

        Args:
            response_text: Raw response text from VLM

        Returns:
            Structured analysis result
        """
        try:
            # Extract JSON from response (might be wrapped in markdown)
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            data = json.loads(response_text.strip())

            # Parse available actions
            available_actions = []
            for action_data in data.get("available_actions", []):
                coords_data = action_data.get("coordinates")
                coordinates = None
                if coords_data:
                    coordinates = Coordinates(
                        x=coords_data["x"],
                        y=coords_data["y"]
                    )

                available_actions.append(
                    ActionTarget(
                        element=action_data["element"],
                        coordinates=coordinates,
                        confidence=action_data.get("confidence", 0.5),
                    )
                )

            # Parse recommended action
            recommended_action = None
            if "recommended_action" in data and data["recommended_action"]:
                rec_data = data["recommended_action"]
                coords_data = rec_data.get("coordinates")
                coordinates = None
                if coords_data:
                    coordinates = Coordinates(
                        x=coords_data["x"],
                        y=coords_data["y"]
                    )

                # Create ActionTarget
                target = ActionTarget(
                    element=rec_data.get("target", ""),
                    coordinates=coordinates,
                    confidence=rec_data.get("confidence", 0.8),
                )

                # Placeholder session_id and step_number
                from uuid import uuid4
                recommended_action = Action(
                    session_id=uuid4(),
                    step_number=0,
                    action_type=ActionType(rec_data.get("action_type", "click")),
                    target=target,
                    text=rec_data.get("text"),
                )

            return VLMAnalysisResult(
                current_screen=data.get("current_screen", "Unknown"),
                available_actions=available_actions,
                recommended_action=recommended_action,
                reasoning=data.get("recommended_action", {}).get("reasoning"),
            )

        except Exception as e:
            logger.error(f"Failed to parse VLM response: {e}")
            logger.debug(f"Raw response: {response_text}")
            raise ValueError(f"Failed to parse VLM response: {e}")

    def detect_payment_screen(self, screenshot_base64: str) -> bool:
        """
        Detect if screenshot shows a payment screen.

        Args:
            screenshot_base64: Base64 encoded screenshot

        Returns:
            True if payment screen detected
        """
        try:
            prompt = """Analyze this screenshot and determine if it shows a payment screen.
Look for indicators like:
- Payment forms or credit card inputs
- "Pay", "Purchase", "Complete Order" buttons
- Price/amount confirmations
- Payment method selection

Return only "true" or "false"."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{screenshot_base64}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=10,
                temperature=0.0,
            )

            result = response.choices[0].message.content.strip().lower()
            is_payment = "true" in result

            if is_payment:
                logger.warning("Payment screen detected!")

            return is_payment

        except Exception as e:
            logger.error(f"Failed to detect payment screen: {e}")
            # Fail safe - assume it's a payment screen if detection fails
            return True
