"""Small-screen rendering shared by the Pi and controller preview."""

import math
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

COLORS = {
    "idle": "#9aa9bd",
    "listening": "#69e3bc",
    "thinking": "#f6c879",
    "speaking": "#95baff",
    "confirm": "#c4a6ff",
    "ready": "#69e3bc",
    "error": "#ff9797",
}
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


@lru_cache(maxsize=16)
def font(size):
    return (
        ImageFont.truetype(FONT, size)
        if Path(FONT).exists()
        else ImageFont.load_default()
    )


def fit(draw, text, width, size=14):
    text = str(text)
    while text and draw.textlength(text, font=font(size)) > width:
        text = text[:-1]
    return text


def render(state, now):
    im = Image.new("RGB", (240, 135), "#101923")
    d = ImageDraw.Draw(im)
    mode = state["state"]
    accent = COLORS.get(mode, COLORS["idle"])
    d.text((10, 7), "ONE THING", font=font(10), fill="#a5b4c5")
    d.ellipse((222, 10, 228, 16), fill=accent)
    if mode in ("confirm", "ready"):
        d.text(
            (10, 28),
            "YOUR FIRST STEP" if mode == "confirm" else "YOU HAVE A START",
            font=font(11),
            fill=accent,
        )
        words = state.get("step", "").split()
        lines = [""]
        for word in words:
            trial = (lines[-1] + " " + word).strip()
            if d.textlength(trial, font=font(16)) > 218 and lines[-1]:
                lines.append(word)
            else:
                lines[-1] = trial
        for i, line in enumerate(lines[:2]):
            d.text(
                (10, 47 + i * 21), fit(d, line, 218, 16), font=font(16), fill="white"
            )
        d.text(
            (10, 93),
            fit(
                d, f"{state.get('minutes', 0)} MIN  /  {state.get('task', '')}", 220, 10
            ),
            font=font(10),
            fill="#a5b4c5",
        )
    else:
        # A pair of eyes and a changing mouth indicate whose turn it is.
        blink = int(now * 2) % 13 == 0
        for x in (91, 133):
            if blink:
                d.rounded_rectangle((x, 35, x + 15, 39), radius=2, fill=accent)
            else:
                d.rounded_rectangle((x, 29, x + 15, 45), radius=5, fill=accent)
        if mode == "thinking":
            for i in range(3):
                y = 57 - int(3 * math.sin(now * 5 + i))
                d.ellipse((103 + i * 12, y, 107 + i * 12, y + 4), fill=accent)
        else:
            level = (
                state.get("level", 0)
                if mode == "listening"
                else (0.4 + 0.3 * math.sin(now * 12) if mode == "speaking" else 0.08)
            )
            for i in range(13):
                h = 2 + int(
                    min(1, level)
                    * 17
                    * (0.45 + 0.55 * math.sin(i * 1.7 + now * 8) ** 2)
                )
                d.rounded_rectangle(
                    (77 + i * 7, 63 - h // 2, 80 + i * 7, 63 + h // 2),
                    radius=1,
                    fill=accent,
                )
        labels = {
            "idle": "A little room to start.",
            "listening": "Your turn. I am listening.",
            "thinking": "One moment...",
            "speaking": "My turn.",
            "error": "Check the controller.",
        }
        d.text((10, 84), mode.upper(), font=font(12), fill=accent)
        d.text((10, 102), labels.get(mode, ""), font=font(11), fill="#dce4ec")
    d.line((10, 118, 230, 118), fill="#2c3949")
    footer = (
        "A: confirm   B: change"
        if mode == "confirm"
        else "A: start again   B: stop"
        if mode == "ready"
        else "A: your turn   B: stop"
    )
    d.text((10, 122), footer, font=font(9), fill="#a5b4c5")
    return im
