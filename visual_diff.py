"""Image-processing functions for comparing an earlier and an updated screenshot."""

import cv2
import numpy as np

# Pixels whose largest channel difference is above this value count as changed.
# Kept low because unchanged pixels in screenshots taken under the same conditions are identical.
DIFF_THRESHOLD = 10

# Changed pixels separated by a gap smaller than this (in pixels) are merged into one region,
# so e.g. the digits of a changed number get a single box.
MERGE_KERNEL_SIZE = 25

BOX_COLOR = (0, 0, 255)  # red, in BGR
BOX_THICKNESS = 2


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


def merge_regions(mask: np.ndarray, kernel_size: int = MERGE_KERNEL_SIZE) -> np.ndarray:
    """Close small gaps between changed pixels so nearby changes form one solid region.

    Closing (dilate, then erode) bridges gaps smaller than the kernel but keeps the region's outer
    edge where it was, so the boxes stay tight around the actual change.
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)


def find_boxes(mask: np.ndarray) -> list[tuple[int, int, int, int]]:
    """Return one (x, y, width, height) bounding box per changed region, top to bottom."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = [cv2.boundingRect(contour) for contour in contours]
    return sorted(boxes, key=lambda box: (box[1], box[0]))


def detect_differences(before: np.ndarray, after: np.ndarray) -> list[tuple[int, int, int, int]]:
    """Run the full pipeline: pixel differencing → thresholding → morphology → contours → boxes."""
    check_same_size(before, after)
    mask = threshold_mask(difference_map(before, after))
    return find_boxes(merge_regions(mask))


def draw_boxes(image: np.ndarray, boxes: list[tuple[int, int, int, int]]) -> np.ndarray:
    """Return a copy of the image with a rectangle drawn around every box."""
    annotated = image.copy()
    for x, y, w, h in boxes:
        cv2.rectangle(annotated, (x, y), (x + w - 1, y + h - 1), BOX_COLOR, BOX_THICKNESS)
    return annotated
