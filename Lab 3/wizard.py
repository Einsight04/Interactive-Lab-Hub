#!/usr/bin/env python3
"""One Thing: Wizard-of-Oz controller for the Part 2 prototype.

The wizard types the device's replies in this terminal; the Pi speaks them
with Piper. Everything else is automatic:

  - Optional APDS-9960 proximity sensor: when a hand is held nearby, the device
    greets them with the first prompt. When removed, it goes back to idle.
  - Silero VAD on the microphone: when the person stops talking, the screen
    switches from LISTENING to THINKING, so they know their turn registered.
  - Mini PiTFT: shows IDLE / LISTENING / THINKING / SPEAKING.

Every event (arrival, end of each spoken turn, each reply, operator notes) is
timestamped in results/session-*.jsonl.

    sudo systemctl stop window-clock.service   # free the screen from Lab 2
    python wizard.py
    python wizard.py --no-screen   # microphone and speaker only
    python wizard.py --sensor      # optional attached proximity sensor

Controls: a number speaks that preset, any other text is spoken as typed,
"/note ..." logs a silent note, "/quit" ends the session.
"""

import argparse
import json
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import sherpa_onnx
import sounddevice as sd
from piper import PiperVoice

SAMPLE_RATE = 16000
LAB_DIR = Path(__file__).resolve().parent
VAD_MODEL = LAB_DIR / "models" / "silero_vad.onnx"
VOICE = LAB_DIR / "voices" / "en_US-lessac-medium.onnx"

# Revise these after the Part 1 acting-out session.
PROMPTS = {
    "1": "Hi. What is one thing you want to get started on?",
    "2": "How many minutes do you have?",
    "3": "What is the smallest first step you could take?",
    "4": "Sorry, could you say that once more?",
    "5": "Would you like a smaller step, or a different task?",
    "6": "Ready when you are.",
    "7": "Okay. We can stop here.",
    "8": "Take your time.",
}

SCREEN = {  # state: (title, subtitle, colour)
    "idle": ("ONE THING", "wave to start", "#aab2c0"),
    "listening": ("LISTENING", "your turn", "#6ee7c7"),
    "thinking": ("THINKING", "one moment", "#ffc66d"),
    "speaking": ("SPEAKING", "my turn", "#93c5fd"),
}


class Screen:
    """The Mini PiTFT, driven by the Display class from Lab 2."""

    def __init__(self) -> None:
        sys.path.insert(0, str(LAB_DIR.parent / "Lab 2"))
        import window_clock
        self.font = window_clock.font
        self.display = window_clock.Display()

    def show(self, state: str) -> None:
        from PIL import Image, ImageDraw
        title, subtitle, colour = SCREEN[state]
        image = Image.new("RGB", (240, 135), "#111827")
        draw = ImageDraw.Draw(image)
        draw.text((12, 12), "ONE THING", font=self.font(12), fill="#aab2c0")
        draw.text((12, 45), title, font=self.font(24), fill=colour)
        draw.text((12, 90), subtitle, font=self.font(16), fill="white")
        self.display.show(image)

    def close(self) -> None:
        self.display.close()


class Proximity:
    """APDS-9960 proximity (0-255, higher is closer), debounced into arrive/leave."""

    def __init__(self, near: int, leave_after: float) -> None:
        import board
        from adafruit_apds9960.apds9960 import APDS9960
        self.sensor = APDS9960(board.I2C())
        self.sensor.enable_proximity = True
        self.near, self.leave_after = near, leave_after
        self.present, self.last_near = False, 0.0

    def update(self) -> str | None:
        now = time.monotonic()
        if self.sensor.proximity >= self.near:
            self.last_near = now
            if not self.present:
                self.present = True
                return "arrived"
        elif self.present and now - self.last_near > self.leave_after:
            self.present = False
            return "left"
        return None


class Wizard:
    def __init__(self, args: argparse.Namespace) -> None:
        self.voice = PiperVoice.load(str(VOICE))
        self.screen = None if args.no_screen else Screen()
        self.proximity = Proximity(args.near, args.leave_after) if args.sensor else None
        self.min_silence = args.min_silence
        self.lock = threading.Lock()
        self.voice_lock = threading.Lock()
        self.speaking = threading.Event()
        self.stopped = threading.Event()
        self.sensor_error = None
        self.worker = None
        self.state = None
        self.start = time.monotonic()
        (LAB_DIR / "results").mkdir(exist_ok=True)
        self.log = LAB_DIR / "results" / f"session-{datetime.now():%Y%m%d-%H%M%S}.jsonl"

    def event(self, kind: str, **fields) -> None:
        row = {"t": round(time.monotonic() - self.start, 2), "event": kind, **fields}
        with self.lock, self.log.open("a") as f:
            f.write(json.dumps(row) + "\n")

    def set_state(self, state: str) -> None:
        with self.lock:
            if state == self.state:
                return
            self.state = state
            if self.screen:
                self.screen.show(state)
        self.event("state", state=state)
        print(f"\r[{state.upper()}]", flush=True)

    def say(self, text: str) -> None:
        with self.voice_lock:
            self.speaking.set()
            self.set_state("speaking")
            self.event("reply", text=text)
            try:
                for chunk in self.voice.synthesize(text):
                    sd.play(np.frombuffer(chunk.audio_int16_bytes, dtype=np.int16),
                            samplerate=chunk.sample_rate)
                    sd.wait()
            finally:
                self.speaking.clear()
            self.set_state("listening")

    def sense(self) -> None:
        try:
            self._sense()
        except Exception as exc:
            self.sensor_error = exc
            self.event("sensor_error", message=str(exc))
            self.stopped.set()
            print(f"\nMicrophone/sensor stopped: {exc}. Restart the session.", flush=True)

    def _sense(self) -> None:
        """Background thread: microphone VAD and the proximity sensor."""
        config = sherpa_onnx.VadModelConfig()
        config.silero_vad.model = str(VAD_MODEL)
        config.silero_vad.min_silence_duration = self.min_silence
        config.sample_rate = SAMPLE_RATE
        vad = sherpa_onnx.VoiceActivityDetector(config, buffer_size_in_seconds=30)
        window = config.silero_vad.window_size
        buffer = np.empty(0, dtype=np.float32)

        with sd.InputStream(channels=1, dtype="float32", samplerate=SAMPLE_RATE) as stream:
            while not self.stopped.is_set():
                chunk, _ = stream.read(int(0.1 * SAMPLE_RATE))
                if self.proximity:
                    change = self.proximity.update()
                    if change:
                        self.event(change)
                        print(f"\r** person {change} **", flush=True)
                        if change == "arrived" and not self.speaking.is_set():
                            threading.Thread(target=self.say, args=(PROMPTS["1"],)).start()
                        elif change == "left":
                            self.set_state("idle")
                if self.speaking.is_set():
                    # Don't let the device hear itself.
                    buffer = np.empty(0, dtype=np.float32)
                    vad.reset()
                    continue
                if self.proximity and not self.proximity.present:
                    buffer = np.empty(0, dtype=np.float32)
                    vad.reset()
                    continue
                buffer = np.concatenate([buffer, chunk.reshape(-1)])
                while len(buffer) >= window:
                    vad.accept_waveform(buffer[:window])
                    buffer = buffer[window:]
                while not vad.empty():
                    seconds = len(vad.front.samples) / SAMPLE_RATE
                    vad.pop()
                    self.event("turn_ended", speech_seconds=round(seconds, 2))
                    self.set_state("thinking")

    def run(self) -> None:
        self.set_state("idle" if self.proximity else "listening")
        self.worker = threading.Thread(target=self.sense, daemon=True)
        self.worker.start()
        for key, text in PROMPTS.items():
            print(f"  {key}: {text}")
        print("Number = preset, text = say it, /note ..., /quit\n")
        while True:
            line = input().strip()
            if self.stopped.is_set():
                raise RuntimeError(f"Session stopped: {self.sensor_error}")
            if line == "/quit":
                break
            if line.startswith("/note "):
                self.event("note", text=line[6:])
            elif line:
                self.say(PROMPTS.get(line, line))

    def close(self) -> None:
        self.stopped.set()
        sd.stop()
        if self.worker:
            self.worker.join(timeout=2)
        if self.screen:
            self.screen.close()
        print(f"Session log: {self.log.relative_to(LAB_DIR)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--min-silence", type=float, default=0.8,
                        help="seconds of silence before THINKING shows (default: 0.8)")
    parser.add_argument("--near", type=int, default=30,
                        help="proximity reading that counts as someone present (default: 30)")
    parser.add_argument("--leave-after", type=float, default=5.0,
                        help="seconds without presence before going idle (default: 5)")
    parser.add_argument("--no-screen", action="store_true")
    sensor = parser.add_mutually_exclusive_group()
    sensor.add_argument("--sensor", action="store_true",
                        help="use an attached APDS-9960; default uses the microphone alone")
    sensor.add_argument("--no-sensor", dest="sensor", action="store_false")
    parser.set_defaults(sensor=False)
    args = parser.parse_args()

    for path in (VAD_MODEL, VOICE):
        if not path.is_file():
            sys.exit(f"{path} not found. Run speech-scripts/setup.sh first.")

    wizard = Wizard(args)
    try:
        wizard.run()
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        wizard.close()


if __name__ == "__main__":
    main()
