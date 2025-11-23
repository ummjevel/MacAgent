"""Tests for VLM client module."""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
from macagent.vlm.vlm_client import VLMClient
from macagent.core.models import VLMAnalysisResult, ActionType


class TestVLMClient:
    """Test VLMClient class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Mock settings to avoid requiring actual API keys
        with patch("macagent.vlm.vlm_client.settings") as mock_settings:
            mock_settings.openrouter_api_key = "test_api_key"
            mock_settings.openrouter_base_url = "https://test.api.com/v1"
            mock_settings.vlm_model = "test-model"
            self.client = VLMClient()

    def test_init_with_custom_params(self):
        """Test initializing client with custom parameters."""
        client = VLMClient(
            api_key="custom_key",
            base_url="https://custom.api.com",
            model="custom-model",
        )

        assert client.api_key == "custom_key"
        assert client.base_url == "https://custom.api.com"
        assert client.model == "custom-model"

    def test_init_without_api_key_raises_error(self):
        """Test that missing API key raises error."""
        with patch("macagent.vlm.vlm_client.settings") as mock_settings:
            mock_settings.openrouter_api_key = ""
            mock_settings.openrouter_base_url = "https://test.api.com/v1"
            mock_settings.vlm_model = "test-model"

            with pytest.raises(ValueError, match="API key is required"):
                VLMClient()

    @patch("macagent.vlm.vlm_client.OpenAI")
    def test_analyze_screen_success(self, mock_openai):
        """Test successful screen analysis."""
        # Mock API response
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()

        response_json = {
            "current_screen": "Main Menu",
            "available_actions": [
                {
                    "element": "Start Button",
                    "coordinates": {"x": 100, "y": 200},
                    "confidence": 0.95,
                }
            ],
            "recommended_action": {
                "action_type": "click",
                "target": "Start Button",
                "coordinates": {"x": 100, "y": 200},
                "reasoning": "Click start to begin",
            },
        }

        mock_message.content = json.dumps(response_json)
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client_instance

        # Recreate client with mocked OpenAI
        with patch("macagent.vlm.vlm_client.settings") as mock_settings:
            mock_settings.openrouter_api_key = "test_key"
            mock_settings.openrouter_base_url = "https://test.api.com/v1"
            mock_settings.vlm_model = "test-model"
            client = VLMClient()

        # Analyze screen
        result = client.analyze_screen(
            screenshot_base64="fake_base64_string",
            task_context="Test task",
            session_id="test_session",
        )

        # Verify result
        assert isinstance(result, VLMAnalysisResult)
        assert result.current_screen == "Main Menu"
        assert len(result.available_actions) == 1
        assert result.available_actions[0].element == "Start Button"
        assert result.available_actions[0].coordinates.x == 100
        assert result.available_actions[0].coordinates.y == 200
        assert result.recommended_action is not None
        assert result.recommended_action.action_type == ActionType.CLICK

    def test_parse_response_with_markdown_wrapper(self):
        """Test parsing response wrapped in markdown code blocks."""
        response_text = """```json
{
    "current_screen": "Test Screen",
    "available_actions": [],
    "recommended_action": null
}
```"""

        result = self.client._parse_response(response_text)

        assert isinstance(result, VLMAnalysisResult)
        assert result.current_screen == "Test Screen"
        assert len(result.available_actions) == 0

    def test_parse_response_without_recommended_action(self):
        """Test parsing response without recommended action."""
        response_text = json.dumps({
            "current_screen": "End Screen",
            "available_actions": [],
        })

        result = self.client._parse_response(response_text)

        assert result.current_screen == "End Screen"
        assert result.recommended_action is None

    def test_parse_response_invalid_json(self):
        """Test parsing invalid JSON response."""
        response_text = "This is not valid JSON"

        with pytest.raises(ValueError):
            self.client._parse_response(response_text)

    def test_build_prompt_with_context(self):
        """Test building prompt with task context."""
        prompt = self.client._build_prompt(task_context="Order a burger")

        assert "Order a burger" in prompt
        assert "JSON format" in prompt
        assert "current_screen" in prompt

    def test_build_prompt_without_context(self):
        """Test building prompt without task context."""
        prompt = self.client._build_prompt()

        assert "JSON format" in prompt
        assert "current_screen" in prompt

    @patch("macagent.vlm.vlm_client.OpenAI")
    def test_detect_payment_screen_true(self, mock_openai):
        """Test detecting payment screen returns True."""
        # Mock API response
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "true"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client_instance

        # Recreate client
        with patch("macagent.vlm.vlm_client.settings") as mock_settings:
            mock_settings.openrouter_api_key = "test_key"
            mock_settings.openrouter_base_url = "https://test.api.com/v1"
            mock_settings.vlm_model = "test-model"
            client = VLMClient()

        result = client.detect_payment_screen("fake_screenshot")

        assert result is True

    @patch("macagent.vlm.vlm_client.OpenAI")
    def test_detect_payment_screen_false(self, mock_openai):
        """Test detecting non-payment screen returns False."""
        # Mock API response
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "false"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client_instance

        # Recreate client
        with patch("macagent.vlm.vlm_client.settings") as mock_settings:
            mock_settings.openrouter_api_key = "test_key"
            mock_settings.openrouter_base_url = "https://test.api.com/v1"
            mock_settings.vlm_model = "test-model"
            client = VLMClient()

        result = client.detect_payment_screen("fake_screenshot")

        assert result is False

    @patch("macagent.vlm.vlm_client.OpenAI")
    def test_detect_payment_screen_error_failsafe(self, mock_openai):
        """Test payment detection fails safe to True on error."""
        # Mock API to raise exception
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client_instance

        # Recreate client
        with patch("macagent.vlm.vlm_client.settings") as mock_settings:
            mock_settings.openrouter_api_key = "test_key"
            mock_settings.openrouter_base_url = "https://test.api.com/v1"
            mock_settings.vlm_model = "test-model"
            client = VLMClient()

        result = client.detect_payment_screen("fake_screenshot")

        # Should fail safe to True (assume payment screen)
        assert result is True
