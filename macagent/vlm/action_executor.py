"""Action executor using pyautogui."""

import time
from typing import Optional, Tuple
import pyautogui
from macagent.core.models import Action, ActionType, ActionStatus
from macagent.core.logger import logger


# Configure pyautogui safety settings
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.5  # Pause between actions


class ActionExecutor:
    """Execute UI actions using pyautogui."""

    def __init__(self, failsafe: bool = True, pause: float = 0.5):
        """
        Initialize action executor.

        Args:
            failsafe: Enable failsafe (move mouse to corner to abort)
            pause: Pause duration between actions (seconds)
        """
        pyautogui.FAILSAFE = failsafe
        pyautogui.PAUSE = pause

    def execute(self, action: Action) -> Action:
        """
        Execute an action.

        Args:
            action: Action to execute

        Returns:
            Updated action with execution results
        """
        start_time = time.time()

        try:
            if action.action_type == ActionType.CLICK:
                self._click(action)
            elif action.action_type == ActionType.DOUBLE_CLICK:
                self._double_click(action)
            elif action.action_type == ActionType.RIGHT_CLICK:
                self._right_click(action)
            elif action.action_type == ActionType.TYPE:
                self._type(action)
            elif action.action_type == ActionType.SCROLL:
                self._scroll(action)
            elif action.action_type == ActionType.WAIT:
                self._wait(action)
            else:
                raise ValueError(f"Unknown action type: {action.action_type}")

            action.status = ActionStatus.SUCCESS
            logger.info(f"Action executed successfully: {action.action_type}")

        except Exception as e:
            action.status = ActionStatus.FAILED
            action.error_message = str(e)
            logger.error(f"Action execution failed: {e}")

        finally:
            execution_time = int((time.time() - start_time) * 1000)
            action.execution_time = execution_time

        return action

    def _click(self, action: Action) -> None:
        """Execute click action."""
        if action.target and action.target.coordinates:
            x, y = action.target.coordinates.x, action.target.coordinates.y
            pyautogui.click(x, y)
            logger.debug(f"Clicked at ({x}, {y})")
        else:
            raise ValueError("Click action requires coordinates")

    def _double_click(self, action: Action) -> None:
        """Execute double click action."""
        if action.target and action.target.coordinates:
            x, y = action.target.coordinates.x, action.target.coordinates.y
            pyautogui.doubleClick(x, y)
            logger.debug(f"Double clicked at ({x}, {y})")
        else:
            raise ValueError("Double click action requires coordinates")

    def _right_click(self, action: Action) -> None:
        """Execute right click action."""
        if action.target and action.target.coordinates:
            x, y = action.target.coordinates.x, action.target.coordinates.y
            pyautogui.rightClick(x, y)
            logger.debug(f"Right clicked at ({x}, {y})")
        else:
            raise ValueError("Right click action requires coordinates")

    def _type(self, action: Action) -> None:
        """Execute type action."""
        if not action.text:
            raise ValueError("Type action requires text")

        # Click at coordinates if provided
        if action.target and action.target.coordinates:
            x, y = action.target.coordinates.x, action.target.coordinates.y
            pyautogui.click(x, y)
            time.sleep(0.2)  # Wait for focus

        pyautogui.write(action.text, interval=0.05)
        logger.debug(f"Typed text: {action.text}")

    def _scroll(self, action: Action) -> None:
        """Execute scroll action."""
        if not action.target_element or "amount" not in action.target_element:
            raise ValueError("Scroll action requires amount")

        amount = action.target_element["amount"]

        # Click at coordinates if provided
        if action.target and action.target.coordinates:
            x, y = action.target.coordinates.x, action.target.coordinates.y
            pyautogui.click(x, y)
            time.sleep(0.1)

        pyautogui.scroll(amount)
        logger.debug(f"Scrolled by {amount}")

    def _wait(self, action: Action) -> None:
        """Execute wait action."""
        if not action.target_element or "duration" not in action.target_element:
            raise ValueError("Wait action requires duration")

        duration = action.target_element["duration"]
        time.sleep(duration)
        logger.debug(f"Waited for {duration} seconds")

    def move_to(self, x: int, y: int, duration: float = 0.5) -> None:
        """
        Move mouse to coordinates.

        Args:
            x: X coordinate
            y: Y coordinate
            duration: Movement duration (seconds)
        """
        pyautogui.moveTo(x, y, duration=duration)
        logger.debug(f"Moved mouse to ({x}, {y})")

    def get_mouse_position(self) -> Tuple[int, int]:
        """
        Get current mouse position.

        Returns:
            Tuple of (x, y) coordinates
        """
        position = pyautogui.position()
        return (position.x, position.y)
