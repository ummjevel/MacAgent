"""Tests for screen capture module."""

import base64
import pytest
from PIL import Image
from macagent.vlm.screen_capture import ScreenCapture


class TestScreenCapture:
    """Test ScreenCapture class."""

    def test_image_to_base64(self):
        """Test converting image to base64."""
        # Create a simple test image
        img = Image.new("RGB", (100, 100), color="red")

        # Convert to base64
        base64_str = ScreenCapture.image_to_base64(img)

        # Verify it's a valid base64 string
        assert isinstance(base64_str, str)
        assert len(base64_str) > 0

        # Verify we can decode it
        decoded = base64.b64decode(base64_str)
        assert len(decoded) > 0

    def test_base64_to_image(self):
        """Test converting base64 to image."""
        # Create a test image and convert to base64
        original_img = Image.new("RGB", (100, 100), color="blue")
        base64_str = ScreenCapture.image_to_base64(original_img)

        # Convert back to image
        decoded_img = ScreenCapture.base64_to_image(base64_str)

        # Verify it's an image with correct size
        assert isinstance(decoded_img, Image.Image)
        assert decoded_img.size == (100, 100)

    def test_image_to_base64_different_formats(self):
        """Test converting image to base64 with different formats."""
        img = Image.new("RGB", (50, 50), color="green")

        # Test PNG format
        png_base64 = ScreenCapture.image_to_base64(img, format="PNG")
        assert isinstance(png_base64, str)

        # Test JPEG format
        jpeg_base64 = ScreenCapture.image_to_base64(img, format="JPEG")
        assert isinstance(jpeg_base64, str)

        # JPEG should typically be smaller for simple images
        # (this may not always be true, but it's a reasonable test)
        assert len(jpeg_base64) <= len(png_base64) * 1.5

    def test_roundtrip_conversion(self):
        """Test roundtrip conversion (image -> base64 -> image)."""
        # Create original image with specific properties
        original_img = Image.new("RGB", (200, 150), color=(128, 64, 32))

        # Convert to base64 and back
        base64_str = ScreenCapture.image_to_base64(original_img)
        decoded_img = ScreenCapture.base64_to_image(base64_str)

        # Verify properties are preserved
        assert decoded_img.size == original_img.size
        assert decoded_img.mode == original_img.mode

    def test_base64_to_image_invalid_input(self):
        """Test base64_to_image with invalid input."""
        with pytest.raises(Exception):
            ScreenCapture.base64_to_image("invalid_base64_string!!!")

    def test_get_screen_size(self):
        """Test getting screen size."""
        size = ScreenCapture.get_screen_size()

        # Verify it returns a tuple of two positive integers
        assert isinstance(size, tuple)
        assert len(size) == 2
        assert all(isinstance(s, int) and s > 0 for s in size)

    # Note: Actual screen capture tests are skipped in CI environments
    # as they require a display
    @pytest.mark.skip(reason="Requires display environment")
    def test_capture_screen(self):
        """Test capturing full screen."""
        screenshot = ScreenCapture.capture_screen()

        assert isinstance(screenshot, Image.Image)
        assert screenshot.size[0] > 0
        assert screenshot.size[1] > 0

    @pytest.mark.skip(reason="Requires display environment")
    def test_capture_screen_region(self):
        """Test capturing screen region."""
        region = (0, 0, 100, 100)
        screenshot = ScreenCapture.capture_screen(region=region)

        assert isinstance(screenshot, Image.Image)
        assert screenshot.size == (100, 100)

    @pytest.mark.skip(reason="Requires display environment")
    def test_capture_and_encode(self):
        """Test capture_and_encode method."""
        base64_str = ScreenCapture.capture_and_encode()

        assert isinstance(base64_str, str)
        assert len(base64_str) > 0

        # Verify it's valid base64
        decoded = base64.b64decode(base64_str)
        assert len(decoded) > 0
