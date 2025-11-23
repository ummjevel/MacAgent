"""Tests for action executor module."""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from macagent.vlm.action_executor import ActionExecutor
from macagent.core.models import (
    Action,
    ActionType,
    ActionStatus,
    ActionTarget,
    Coordinates,
)


class TestActionExecutor:
    """Test ActionExecutor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.executor = ActionExecutor(failsafe=False, pause=0.1)
        self.session_id = uuid4()

    @patch("macagent.vlm.action_executor.pyautogui.click")
    def test_execute_click_action(self, mock_click):
        """Test executing click action."""
        action = Action(
            session_id=self.session_id,
            step_number=1,
            action_type=ActionType.CLICK,
            target=ActionTarget(
                element="Test Button",
                coordinates=Coordinates(x=100, y=200),
                confidence=0.9,
            ),
        )

        result = self.executor.execute(action)

        # Verify click was called with correct coordinates
        mock_click.assert_called_once_with(100, 200)

        # Verify action status was updated
        assert result.status == ActionStatus.SUCCESS
        assert result.execution_time is not None
        assert result.execution_time >= 0

    @patch("macagent.vlm.action_executor.pyautogui.doubleClick")
    def test_execute_double_click_action(self, mock_double_click):
        """Test executing double click action."""
        action = Action(
            session_id=self.session_id,
            step_number=1,
            action_type=ActionType.DOUBLE_CLICK,
            target=ActionTarget(
                element="File Icon",
                coordinates=Coordinates(x=150, y=250),
                confidence=0.85,
            ),
        )

        result = self.executor.execute(action)

        mock_double_click.assert_called_once_with(150, 250)
        assert result.status == ActionStatus.SUCCESS

    @patch("macagent.vlm.action_executor.pyautogui.rightClick")
    def test_execute_right_click_action(self, mock_right_click):
        """Test executing right click action."""
        action = Action(
            session_id=self.session_id,
            step_number=1,
            action_type=ActionType.RIGHT_CLICK,
            target=ActionTarget(
                element="Context Menu",
                coordinates=Coordinates(x=300, y=400),
                confidence=0.9,
            ),
        )

        result = self.executor.execute(action)

        mock_right_click.assert_called_once_with(300, 400)
        assert result.status == ActionStatus.SUCCESS

    @patch("macagent.vlm.action_executor.pyautogui.write")
    @patch("macagent.vlm.action_executor.pyautogui.click")
    @patch("macagent.vlm.action_executor.time.sleep")
    def test_execute_type_action(self, mock_sleep, mock_click, mock_write):
        """Test executing type action."""
        action = Action(
            session_id=self.session_id,
            step_number=1,
            action_type=ActionType.TYPE,
            target=ActionTarget(
                element="Text Input",
                coordinates=Coordinates(x=200, y=300),
                confidence=0.95,
            ),
            text="Hello, World!",
        )

        result = self.executor.execute(action)

        # Verify click and write were called
        mock_click.assert_called_once_with(200, 300)
        mock_write.assert_called_once_with("Hello, World!", interval=0.05)
        assert result.status == ActionStatus.SUCCESS

    @patch("macagent.vlm.action_executor.pyautogui.scroll")
    @patch("macagent.vlm.action_executor.pyautogui.click")
    @patch("macagent.vlm.action_executor.time.sleep")
    def test_execute_scroll_action(self, mock_sleep, mock_click, mock_scroll):
        """Test executing scroll action."""
        action = Action(
            session_id=self.session_id,
            step_number=1,
            action_type=ActionType.SCROLL,
            target=ActionTarget(
                element="Scroll Area",
                coordinates=Coordinates(x=500, y=500),
                confidence=0.8,
            ),
            target_element={"amount": 5},
        )

        result = self.executor.execute(action)

        mock_click.assert_called_once_with(500, 500)
        mock_scroll.assert_called_once_with(5)
        assert result.status == ActionStatus.SUCCESS

    @patch("macagent.vlm.action_executor.time.sleep")
    def test_execute_wait_action(self, mock_sleep):
        """Test executing wait action."""
        action = Action(
            session_id=self.session_id,
            step_number=1,
            action_type=ActionType.WAIT,
            target_element={"duration": 2.0},
        )

        result = self.executor.execute(action)

        mock_sleep.assert_called()
        assert result.status == ActionStatus.SUCCESS

    def test_execute_click_without_coordinates(self):
        """Test executing click without coordinates fails."""
        action = Action(
            session_id=self.session_id,
            step_number=1,
            action_type=ActionType.CLICK,
            target=ActionTarget(
                element="Test Button",
                coordinates=None,
                confidence=0.9,
            ),
        )

        result = self.executor.execute(action)

        assert result.status == ActionStatus.FAILED
        assert result.error_message is not None
        assert "coordinates" in result.error_message.lower()

    def test_execute_type_without_text(self):
        """Test executing type without text fails."""
        action = Action(
            session_id=self.session_id,
            step_number=1,
            action_type=ActionType.TYPE,
            target=ActionTarget(
                element="Text Input",
                coordinates=Coordinates(x=100, y=100),
                confidence=0.9,
            ),
            text=None,
        )

        result = self.executor.execute(action)

        assert result.status == ActionStatus.FAILED
        assert result.error_message is not None

    @patch("macagent.vlm.action_executor.pyautogui.moveTo")
    def test_move_to(self, mock_move_to):
        """Test moving mouse to coordinates."""
        self.executor.move_to(100, 200, duration=0.3)

        mock_move_to.assert_called_once_with(100, 200, duration=0.3)

    @patch("macagent.vlm.action_executor.pyautogui.position")
    def test_get_mouse_position(self, mock_position):
        """Test getting mouse position."""
        # Mock the position return value
        mock_pos = Mock()
        mock_pos.x = 150
        mock_pos.y = 250
        mock_position.return_value = mock_pos

        position = self.executor.get_mouse_position()

        assert position == (150, 250)

    @patch("macagent.vlm.action_executor.pyautogui.click")
    def test_execution_time_recorded(self, mock_click):
        """Test that execution time is recorded."""
        action = Action(
            session_id=self.session_id,
            step_number=1,
            action_type=ActionType.CLICK,
            target=ActionTarget(
                element="Button",
                coordinates=Coordinates(x=100, y=100),
                confidence=0.9,
            ),
        )

        result = self.executor.execute(action)

        # Execution time should be set and be a reasonable value
        assert result.execution_time is not None
        assert result.execution_time >= 0
        assert result.execution_time < 10000  # Less than 10 seconds in ms
