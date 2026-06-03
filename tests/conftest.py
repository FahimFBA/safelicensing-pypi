"""
Shared pytest fixtures for the SafeLicensing test suite.
"""

import numpy as np
import pytest
from PIL import Image


@pytest.fixture
def tiny_rgb_array() -> np.ndarray:
    """
    Return a small 4x4x3 uint8 NumPy array for encryption tests.

    :return: NumPy array of shape (4, 4, 3) with dtype uint8.
    """
    rng = np.random.default_rng(seed=42)
    return rng.integers(0, 256, (4, 4, 3), dtype=np.uint8)


@pytest.fixture
def tiny_pil_image(tiny_rgb_array) -> Image.Image:
    """
    Return a small 4x4 RGB PIL Image built from tiny_rgb_array.

    :return: PIL.Image.Image of size (4, 4) in RGB mode.
    """
    return Image.fromarray(tiny_rgb_array)


@pytest.fixture
def valid_seed() -> float:
    """
    Return a seed value that is valid for all chaotic encryption functions.

    :return: Float 0.42, strictly inside (0.0, 1.0).
    """
    return 0.42
