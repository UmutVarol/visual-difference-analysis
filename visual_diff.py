"""Image-processing functions for comparing an earlier and an updated screenshot."""

import cv2
import numpy as np

# Pixels whose largest channel difference is above this value count as changed.
# Kept low because unchanged pixels in screenshots taken under the same conditions are identical.
DIFF_THRESHOLD = 10


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


def difference_map(before: np.ndarray, after: np.ndarray) -> np.ndarray:
    """Return a (height, width) uint8 map of how much each pixel changed (0 = identical).

    The difference is taken per channel and the largest of B, G, R is kept, because converting
    to grayscale first can hide color changes (e.g. dark red and dark green share gray value 59).
    """
    diff = cv2.absdiff(before, after)
    return diff.max(axis=2)


def threshold_mask(diff: np.ndarray, threshold: int = DIFF_THRESHOLD) -> np.ndarray:
    """Turn a difference map into a binary mask: 255 where the pixel changed, 0 elsewhere."""
    _, mask = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
    return mask
