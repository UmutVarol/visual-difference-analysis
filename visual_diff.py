"""Image-processing functions for comparing an earlier and an updated screenshot."""

import cv2
import numpy as np


def load_image(data: bytes) -> np.ndarray:
    """Decode an image file's bytes into a BGR array of shape (height, width, 3), dtype uint8."""
    if not data:
        raise ValueError("The file is empty.")
    buffer = np.frombuffer(data, dtype=np.uint8)
    # IMREAD_COLOR always returns 3 channels: grayscale is expanded, a PNG alpha channel is dropped.
    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("The file could not be read as an image.")
    return image


def check_same_size(before: np.ndarray, after: np.ndarray) -> None:
    """Raise ValueError if the two images do not have identical dimensions."""
    if before.shape[:2] != after.shape[:2]:
        before_h, before_w = before.shape[:2]
        after_h, after_w = after.shape[:2]
        raise ValueError(
            f"Images must have the same size: earlier version is {before_w}x{before_h}, "
            f"updated version is {after_w}x{after_h}."
        )
