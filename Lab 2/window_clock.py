"""One More Window: a 25-minute building clock for the Mini PiTFT.

A starts/pauses/resumes. B advances to a fresh break/work session.
Both held for one second reset. --demo uses 25s work / 5s break.
--preview DIR renders an accelerated software demo without GPIO.
"""
from dataclasses import dataclass
from pathlib import Path
import argparse
import math
import time
from PIL import Image, ImageDraw, ImageFont


@dataclass
class Clock:
    work: float = 1500
    rest: float = 300
    phase: str = "work"
    elapsed: float = 0
    running: bool = False
    done: bool = False

    def __post_init__(self):
        if not all(math.isfinite(x) and x > 0 for x in (self.work, self.rest)):
            raise ValueError("Durations must be finite and positive")

    @property
    def duration(self):
        return self.work if self.phase == "work" else self.rest

    @property
    def fraction(self):
        return min(1.0, self.elapsed / self.duration)

    def tick(self, seconds):
        if self.running:
            self.elapsed = min(self.duration, self.elapsed + max(0, seconds))
            if self.elapsed >= self.duration:
                self.running, self.done = False, True

    def action(self, key):
        if key == "reset":
            self.phase, self.elapsed, self.running, self.done = "work", 0, False, False
        elif key == "b":
            self.phase = "break" if self.phase == "work" else "work"
            self.elapsed, self.running, self.done = 0, True, False
        elif key == "a" and not self.done:
            self.running = not self.running


class Buttons:
    """Debounced release events; simultaneous presses never trigger singles."""
    def __init__(self):
        self.raw = self.stable = (False, False)
        self.changed = 0
        self.chord = False
        self.chord_start = None
        self.reset_sent = False

    def update(self, a, b, now):
        pair = (a, b)
        if pair != self.raw:
            self.raw, self.changed = pair, now
        events = []
        if now - self.changed >= .04 and self.stable != self.raw:
            old, self.stable = self.stable, self.raw
            if all(self.stable):
                self.chord, self.chord_start = True, now
            if self.chord:
                if self.stable == (False, False):
                    self.chord, self.chord_start, self.reset_sent = False, None, False
            else:
                for i, key in enumerate(("a", "b")):
                    if old[i] and not self.stable[i]:
                        events.append(key)
        if (all(self.stable) and self.chord_start is not None
                and now - self.chord_start >= 1 and not self.reset_sent):
            self.reset_sent = True
            events.append("reset")
        return events


def font(size):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "/System/Library/Fonts/Supplemental/Arial.ttf"):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


SMALL, BIG = font(10), font(15)


def render(clock, demo=False):
    image = Image.new("RGB", (240, 135), "#111827")
    d = ImageDraw.Draw(image)
    amber, teal, muted = "#ffc66d", "#6ee7c7", "#8793a5"
    accent = amber if clock.phase == "work" else teal
    title = "ONE MORE WINDOW" if clock.phase == "work" else "ROOM TO BREATHE"
    d.text((8, 5), title, font=SMALL, fill=accent)
    if demo:
        d.text((202, 5), "DEMO", font=SMALL, fill=muted)
    d.rectangle((12, 26, 115, 113), fill="#263247", outline="#64748b")
    d.line((7, 114, 120, 114), fill=muted, width=2)
    count = (math.ceil(25 * (1 - clock.fraction)) if clock.phase == "work"
             else math.floor(25 * clock.fraction))
    for i in range(25):
        x, y = 21 + (i % 5) * 18, 34 + (i // 5) * 15
        d.rectangle((x, y, x + 10, y + 8), fill=accent if i < count else "#111827")
    if clock.done:
        lines = ("STEP AWAY", "you did enough", "B: take a break") if clock.phase == "work" else ("READY?", "no rush", "B: start fresh")
    elif clock.running:
        lines = ("SETTLE IN", "one window", "at a time") if clock.phase == "work" else ("BREATHE", "fill back up", "take your time")
    else:
        lines = ("PAUSED", "it can wait", "A: keep going") if clock.elapsed else ("A LITTLE", "room to focus", "A: start")
    for i, line in enumerate(lines):
        d.text((128, 35 + i * 23), line, font=BIG if i == 0 else SMALL,
               fill=accent if i == 0 else "#e5e7eb")
    d.text((8, 120), "A: pause/play   B: next   A+B: reset", font=SMALL, fill=muted)
    return image


class Display:
    def __init__(self):
        import board
        import digitalio
        from adafruit_rgb_display import st7789
        self.pins = []
        def pin(number):
            p = digitalio.DigitalInOut(number)
            self.pins.append(p)
            return p
        self.spi = board.SPI()
        self.display = st7789.ST7789(self.spi, cs=pin(board.D5), dc=pin(board.D25),
            rst=None, baudrate=64000000, width=135, height=240, x_offset=53, y_offset=40)
        self.light = pin(board.D22)
        self.light.switch_to_output(value=True)
        self.a, self.b = pin(board.D23), pin(board.D24)
        self.a.switch_to_input(pull=digitalio.Pull.UP)
        self.b.switch_to_input(pull=digitalio.Pull.UP)

    def show(self, image):
        self.display.image(image, 90)

    def close(self):
        self.light.value = False
        for p in reversed(self.pins):
            p.deinit()
        self.spi.deinit()


def preview(directory):
    """Deterministic accelerated demo; saved images are explicitly software output."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    c = Clock(work=25, rest=5)
    frames = []
    def frame(name=None):
        im = render(c, demo=True)
        if name:
            im.save(directory / (name + ".png"))
        big = im.resize((960, 540), Image.Resampling.NEAREST)
        canvas = Image.new("RGB", (960, 580), "#111827")
        canvas.paste(big)
        ImageDraw.Draw(canvas).text((15, 551), "SOFTWARE PREVIEW - accelerated time; not camera footage", font=font(18), fill="white")
        frames.append(canvas)
    frame("ready")
    c.action("a")
    for i in range(25):
        c.tick(1)
        frame("work" if i == 11 else None)
        if i == 11:
            c.action("a")
            for _ in range(3):
                c.tick(1)
                frame("paused")
            c.action("a")
    frame("complete")
    c.action("b")
    for _ in range(5):
        c.tick(1)
        frame("break")
    frame("break-complete")
    frames[0].save(directory / "software-demo.gif", save_all=True,
                   append_images=frames[1:], duration=400, loop=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--preview", metavar="DIRECTORY")
    parser.add_argument("--seconds", type=float, help="Exit after this many seconds (hardware smoke test)")
    parser.add_argument("--autostart", action="store_true")
    args = parser.parse_args()
    if args.preview:
        preview(args.preview)
        return
    c = Clock(work=25, rest=5) if args.demo else Clock()
    if args.autostart:
        c.action("a")
    display, buttons = Display(), Buttons()
    start = previous = time.monotonic()
    last_image = None
    print("Clock running; A: start/pause, B: next, hold A+B: reset", flush=True)
    try:
        while args.seconds is None or time.monotonic() - start < args.seconds:
            now = time.monotonic()
            c.tick(now - previous)
            previous = now
            for event in buttons.update(not display.a.value, not display.b.value, now):
                c.action(event)
                print(f"button={event} phase={c.phase} elapsed={c.elapsed:.2f} running={c.running}", flush=True)
            im = render(c, args.demo)
            pixels = im.tobytes()
            if pixels != last_image:
                display.show(im)
                last_image = pixels
            time.sleep(.02)
    except KeyboardInterrupt:
        pass
    finally:
        display.close()


if __name__ == "__main__":
    main()
