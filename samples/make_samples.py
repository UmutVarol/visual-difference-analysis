"""Generate a synthetic before/after screenshot pair like the example in the project PDF.

Changes in after.png compared to before.png:
  1. "NEW" badge removed from the Revenue card
  2. "NEW" badge added to the Orders card
  3. Revenue value 48,920 -> 52,340
  4. Export button blue -> green
  5. "Cancelled" status text dark red -> dark green (both have the same grayscale value)
"""

from pathlib import Path

import cv2
import numpy as np

WIDTH, HEIGHT = 1280, 800
FONT = cv2.FONT_HERSHEY_SIMPLEX

# OpenCV colors are (Blue, Green, Red)
BACKGROUND = (250, 247, 245)
WHITE = (255, 255, 255)
BORDER = (230, 225, 222)
TEXT = (40, 30, 20)
MUTED = (140, 125, 115)
BLUE = (235, 99, 37)  # #2563EB
GREEN = (74, 163, 22)  # #16A34A
ORANGE = (22, 115, 249)  # #F97316
DARK_RED = (0, 0, 196)
DARK_GREEN = (0, 100, 0)


def put_text(image, text, x, y, scale, color, thickness=1):
    cv2.putText(image, text, (x, y), FONT, scale, color, thickness, cv2.LINE_AA)


def put_centered_text(image, text, box, scale, color, thickness=1):
    x1, y1, x2, y2 = box
    (text_w, text_h), _ = cv2.getTextSize(text, FONT, scale, thickness)
    put_text(image, text, x1 + (x2 - x1 - text_w) // 2, y1 + (y2 - y1 + text_h) // 2, scale, color, thickness)


def draw_dashboard(revenue, badge_card, export_color, cancelled_color):
    image = np.full((HEIGHT, WIDTH, 3), BACKGROUND, dtype=np.uint8)

    # Top navigation bar
    cv2.rectangle(image, (0, 0), (WIDTH, 64), WHITE, -1)
    cv2.line(image, (0, 64), (WIDTH, 64), BORDER, 1)
    cv2.circle(image, (40, 32), 10, BLUE, -1, cv2.LINE_AA)
    put_text(image, "ShopBoard", 60, 40, 0.7, TEXT, 2)
    for i, item in enumerate(["Home", "Orders", "Reports", "Settings"]):
        put_text(image, item, 760 + i * 110, 40, 0.55, BLUE if item == "Orders" else MUTED)
    cv2.circle(image, (1230, 32), 16, BORDER, -1, cv2.LINE_AA)

    put_text(image, "Dashboard", 40, 115, 1.0, TEXT, 2)

    # Summary cards
    cards = [
        ("Orders", "1,284", "+3.2% vs last week"),
        ("Revenue", revenue, "+5.1% vs last week"),
        ("Users", "3,507", "+1.4% vs last week"),
    ]
    card_w = 380
    for i, (label, value, trend) in enumerate(cards):
        x = 40 + i * (card_w + 30)
        cv2.rectangle(image, (x, 145), (x + card_w, 295), WHITE, -1)
        cv2.rectangle(image, (x, 145), (x + card_w, 295), BORDER, 1)
        put_text(image, label, x + 24, 185, 0.6, MUTED)
        put_text(image, value, x + 24, 245, 1.3, TEXT, 2)
        put_text(image, trend, x + 24, 278, 0.5, GREEN)
        if label == badge_card:
            badge = (x + card_w - 84, 163, x + card_w - 24, 191)
            cv2.rectangle(image, badge[:2], badge[2:], ORANGE, -1)
            put_centered_text(image, "NEW", badge, 0.5, WHITE, 1)

    # Recent orders panel
    cv2.rectangle(image, (40, 325), (1240, 760), WHITE, -1)
    cv2.rectangle(image, (40, 325), (1240, 760), BORDER, 1)
    put_text(image, "Recent orders", 64, 370, 0.75, TEXT, 2)
    export = (1110, 345, 1216, 383)
    cv2.rectangle(image, export[:2], export[2:], export_color, -1)
    put_centered_text(image, "Export", export, 0.6, WHITE, 1)

    columns = [64, 300, 620, 1000]
    for x, header in zip(columns, ["Order", "Customer", "Status", "Amount"]):
        put_text(image, header, x, 425, 0.5, MUTED)
    cv2.line(image, (64, 440), (1216, 440), BORDER, 1)

    rows = [
        ("#10234", "Ayse Y.", "Shipped", "TRY 1,240"),
        ("#10235", "Mehmet K.", "Pending", "TRY 860"),
        ("#10236", "Zeynep O.", "Shipped", "TRY 2,115"),
        ("#10237", "Can B.", "Cancelled", "TRY 430"),
        ("#10238", "Elif S.", "Shipped", "TRY 975"),
    ]
    for r, row in enumerate(rows):
        y = 485 + r * 55
        for x, value in zip(columns, row):
            if value == "Cancelled":
                put_text(image, value, x, y, 0.6, cancelled_color, 2)
            else:
                put_text(image, value, x, y, 0.6, TEXT)
        cv2.line(image, (64, y + 22), (1216, y + 22), BORDER, 1)

    return image


def save_png(path, image):
    # imencode + write_bytes also works for paths with non-ASCII characters (cv2.imwrite may not on Windows).
    _, encoded = cv2.imencode(".png", image)
    path.write_bytes(encoded.tobytes())


if __name__ == "__main__":
    out_dir = Path(__file__).parent
    before = draw_dashboard("48,920", badge_card="Revenue", export_color=BLUE, cancelled_color=DARK_RED)
    after = draw_dashboard("52,340", badge_card="Orders", export_color=GREEN, cancelled_color=DARK_GREEN)
    save_png(out_dir / "before.png", before)
    save_png(out_dir / "after.png", after)
    print(f"Saved before.png and after.png ({WIDTH}x{HEIGHT}) to {out_dir}")
