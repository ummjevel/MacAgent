"""Screen capture module using PIL and pyautogui."""

import base64
import io
from typing import Optional, Tuple
from PIL import Image, ImageGrab
import pyautogui
from macagent.core.logger import logger


class ScreenCapture:
    """Screen capture utility."""

    @staticmethod
    def capture_screen(region: Optional[Tuple[int, int, int, int]] = None) -> Image.Image:
        """
        Capture screenshot.

        Args:
            region: Optional tuple (x, y, width, height) to capture specific region

        Returns:
            PIL Image object
        """
        try:
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()

            logger.info(f"Screenshot captured: {screenshot.size}")
            return screenshot
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            raise

    @staticmethod
    def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
        """
        Convert PIL Image to base64 string.

        Args:
            image: PIL Image object
            format: Image format (PNG, JPEG, etc.)

        Returns:
            Base64 encoded string
        """
        try:
            buffered = io.BytesIO()
            image.save(buffered, format=format)
            img_bytes = buffered.getvalue()
            img_base64 = base64.b64encode(img_bytes).decode("utf-8")
            return img_base64
        except Exception as e:
            logger.error(f"Failed to convert image to base64: {e}")
            raise

    @staticmethod
    def base64_to_image(base64_string: str) -> Image.Image:
        """
        Convert base64 string to PIL Image.

        Args:
            base64_string: Base64 encoded image string

        Returns:
            PIL Image object
        """
        try:
            img_bytes = base64.b64decode(base64_string)
            image = Image.open(io.BytesIO(img_bytes))
            return image
        except Exception as e:
            logger.error(f"Failed to convert base64 to image: {e}")
            raise

    @staticmethod
    def capture_and_encode(
        region: Optional[Tuple[int, int, int, int]] = None,
        format: str = "PNG"
    ) -> str:
        """
        Capture screenshot and return as base64 string.

        Args:
            region: Optional tuple (x, y, width, height) to capture specific region
            format: Image format (PNG, JPEG, etc.)

        Returns:
            Base64 encoded screenshot
        """
        screenshot = ScreenCapture.capture_screen(region)
        return ScreenCapture.image_to_base64(screenshot, format)

    @staticmethod
    def get_screen_size() -> Tuple[int, int]:
        """
        Get screen resolution.

        Returns:
            Tuple of (width, height)
        """
        try:
            size = pyautogui.size()
            logger.info(f"Screen size: {size}")
            return size
        except Exception as e:
            logger.error(f"Failed to get screen size: {e}")
            raise
