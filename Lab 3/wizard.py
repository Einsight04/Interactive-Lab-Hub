#!/usr/bin/env python3
"""One Thing: local Wizard-of-Oz controller, microphone, speech and Pi screen.
Run python wizard.py, then SSH-forward port 5000 to the laptop browser.
The operator chooses replies and fills the plan. ASR only suggests transcripts.
"""

import argparse
import io
import json
import logging
import queue
import signal
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import sounddevice as sd
import sherpa_onnx
from flask import Flask, jsonify, request, send_file
from piper import PiperVoice
from faster_whisper import WhisperModel
from device_ui import render

ROOT = Path(__file__).resolve().parent
RATE = 16000
PROMPTS = {
    "task": "Hi. What is one thing you want to get started on?",
    "time": "How many minutes do you have?",
    "step": "What is the smallest first step you could take?",
    "repeat": "Sorry, could you say that once more?",
    "smaller": "What could you do in just the first two minutes?",
    "wait": "Take your time. There is no rush.",
    "unclear": "Was that fifteen or fifty minutes?",
    "correct": "Of course. What would you like to change?",
}


class Engine:
    def __init__(self, no_screen=False, min_silence=0.8):
        self.lock = threading.RLock()
        self.done = threading.Event()
        self.audio_lock = threading.Lock()
        self.tts = queue.Queue()
        self.asr = queue.Queue(maxsize=2)
        self.epoch = 0
        self.muted_until = 0
        self.min_silence = min_silence
        self.history = []
        self.data = dict(
            state="idle",
            level=0,
            task="",
            step="",
            minutes=15,
            heard="",
            error="",
            mic=False,
        )
        self.start = time.monotonic()
        self.display = None
        self.threads = []
        (ROOT / "results").mkdir(exist_ok=True)
        self.log = ROOT / "results" / f"session-{datetime.now():%Y%m%d-%H%M%S-%f}.jsonl"
        self.voice = PiperVoice.load(str(ROOT / "voices/en_US-lessac-medium.onnx"))
        self.output_device = next(
            (
                i
                for i, d in enumerate(sd.query_devices())
                if "UACDemo" in d["name"] and d["max_output_channels"] > 0
            ),
            sd.default.device[1],
        )
        self.output_rate = 48000
        sd.check_output_settings(
            device=self.output_device,
            channels=1,
            dtype="int16",
            samplerate=self.output_rate,
        )
        self.recognizer = WhisperModel("tiny.en", device="cpu", compute_type="int8")
        if not no_screen:
            sys.path.insert(0, str(ROOT.parent / "Lab 2"))
            from window_clock import Display

            self.display = Display()
        for method in (self.speaker, self.microphone, self.transcribe, self.screen):
            t = threading.Thread(target=self.guard, args=(method,), daemon=True)
            t.start()
            self.threads.append(t)
        self.event(
            "session",
            detail="Wizard chooses replies; transcripts are automatic. Raw audio is not retained.",
        )

    def guard(self, method):
        try:
            method()
        except Exception as exc:
            with self.lock:
                self.data.update(error=f"{method.__name__}: {exc}", state="error")
                if method == self.microphone:
                    self.data["mic"] = False
            self.event("error", text=str(exc), source=method.__name__)

    def event(self, kind, **fields):
        with self.lock:
            item = dict(t=round(time.monotonic() - self.start, 2), event=kind, **fields)
            self.history.append(item)
            self.history = self.history[-250:]
            with self.log.open("a") as f:
                f.write(json.dumps(item) + "\n")

    def state(self, value):
        with self.lock:
            if self.data["state"] != value:
                self.data["state"] = value
                self.event("state", state=value)

    def snapshot(self):
        with self.lock:
            return dict(
                self.data,
                history=list(self.history),
                min_silence=self.min_silence,
                session=self.log.name,
            )

    def cancel(self, state="idle"):
        # Invalidate synthesis and recognition work already in flight.
        with self.audio_lock, self.lock:
            self.epoch += 1
            sd.stop()
            self.muted_until = time.monotonic() + 0.4
            self.data["error"] = ""
            self.state(state)
            self.data["level"] = 0

    def say(self, text, after="listening"):
        if not isinstance(text, str) or not text.strip() or len(text) > 500:
            raise ValueError("Reply must contain 1 to 500 characters.")
        self.cancel("thinking")
        with self.lock:
            self.tts.put((self.epoch, text.strip(), after))

    def action(self, action, payload):
        if action == "preset":
            if payload.get("key") not in PROMPTS:
                raise ValueError("Unknown prompt.")
            self.say(PROMPTS[payload["key"]])
        elif action == "say":
            self.say(payload.get("text", ""))
        elif action == "stop":
            self.cancel()
            self.event("stop")
        elif action == "listen":
            self.cancel("listening")
        elif action == "plan":
            task = str(payload.get("task", "")).strip()
            step = str(payload.get("step", "")).strip()
            try:
                minutes = int(payload.get("minutes", 0))
            except (TypeError, ValueError):
                raise ValueError("Enter whole minutes.")
            if (
                not task
                or not step
                or len(task) > 100
                or len(step) > 100
                or not 1 <= minutes <= 240
            ):
                raise ValueError(
                    "Enter a task, a first step (up to 100 characters each), and 1 to 240 minutes."
                )
            with self.lock:
                self.data.update(task=task, step=step, minutes=minutes)
            self.event("plan", task=task, step=step, minutes=minutes)
            self.say(
                f"{minutes} minutes to {step}. Does that sound right? Press the top button to confirm, or the bottom button to change it.",
                "confirm",
            )
        elif action == "confirm":
            with self.lock:
                if self.data["state"] != "confirm":
                    raise ValueError("Read back a plan before confirming.")
            self.event("confirmed")
            self.say("Ready when you are. One small step is enough.", "ready")
        elif action == "change":
            self.say(PROMPTS["correct"])
        elif action == "note":
            text = str(payload.get("text", "")).strip()
            if not text or len(text) > 1000:
                raise ValueError("Note must contain 1 to 1000 characters.")
            self.event("note", text=text)
        elif action == "silence":
            try:
                value = float(payload["value"])
            except (KeyError, TypeError, ValueError):
                raise ValueError("Choose a silence threshold.")
            if value not in (0.2, 0.8, 1.5):
                raise ValueError("Choose 0.2, 0.8, or 1.5 seconds.")
            self.cancel("listening")
            with self.lock:
                self.min_silence = value
            self.event("silence", seconds=value)
        else:
            raise ValueError("Unknown action.")

    def speaker(self):
        while not self.done.is_set():
            try:
                epoch, text, after = self.tts.get(timeout=0.2)
            except queue.Empty:
                continue
            if epoch != self.epoch:
                continue
            self.event("reply", text=text)
            try:
                for chunk in self.voice.synthesize(text):
                    with self.audio_lock:
                        if epoch != self.epoch or self.done.is_set():
                            break
                        audio = np.frombuffer(chunk.audio_int16_bytes, dtype=np.int16)
                        if chunk.sample_rate != self.output_rate:
                            positions = (
                                np.arange(
                                    round(
                                        len(audio)
                                        * self.output_rate
                                        / chunk.sample_rate
                                    )
                                )
                                * chunk.sample_rate
                                / self.output_rate
                            )
                            audio = np.interp(
                                positions, np.arange(len(audio)), audio
                            ).astype(np.int16)
                        sd.play(audio, self.output_rate, device=self.output_device)
                        self.state("speaking")
                    sd.wait()
                with self.lock:
                    if epoch == self.epoch:
                        self.muted_until = time.monotonic() + 0.45
                        self.state(after)
            except Exception as exc:
                with self.lock:
                    self.data["error"] = f"Speech playback: {exc}"
                self.state("error")
                self.event("error", text=str(exc))

    def microphone(self):
        threshold = None
        epoch = -1
        buffer = np.empty(0, dtype=np.float32)
        with sd.InputStream(channels=1, dtype="float32", samplerate=RATE) as stream:
            with self.lock:
                self.data["mic"] = True
            while not self.done.is_set():
                chunk, overflow = stream.read(1600)
                with self.lock:
                    current = self.epoch
                    silence = self.min_silence
                    listening = (
                        self.data["state"] == "listening"
                        and time.monotonic() > self.muted_until
                    )
                if threshold != silence:
                    config = sherpa_onnx.VadModelConfig()
                    config.sample_rate = RATE
                    config.silero_vad.model = str(ROOT / "models/silero_vad.onnx")
                    config.silero_vad.min_silence_duration = silence
                    vad = sherpa_onnx.VoiceActivityDetector(
                        config, buffer_size_in_seconds=30
                    )
                    window = config.silero_vad.window_size
                    threshold = silence
                if current != epoch or not listening or overflow:
                    vad.reset()
                    buffer = np.empty(0, dtype=np.float32)
                    epoch = current
                if not listening:
                    continue
                with self.lock:
                    self.data["level"] = min(1, float(np.sqrt(np.mean(chunk**2))) * 25)
                buffer = np.concatenate((buffer, chunk[:, 0]))
                while len(buffer) >= window:
                    vad.accept_waveform(buffer[:window])
                    buffer = buffer[window:]
                if not vad.empty():
                    audio = np.array(vad.front.samples, dtype=np.float32)
                    vad.reset()
                    with self.lock:
                        if current != self.epoch or self.data["state"] != "listening":
                            continue
                        self.state("thinking")
                        self.event(
                            "turn_ended", speech_seconds=round(len(audio) / RATE, 2)
                        )
                        try:
                            self.asr.put_nowait((current, audio))
                        except queue.Full:
                            self.event(
                                "error", text="Recognition busy; ask for a repeat."
                            )

    def transcribe(self):
        while not self.done.is_set():
            try:
                epoch, audio = self.asr.get(timeout=0.2)
            except queue.Empty:
                continue
            if epoch != self.epoch:
                continue
            start = time.monotonic()
            segments, _ = self.recognizer.transcribe(audio, beam_size=1, language="en")
            text = " ".join(s.text.strip() for s in segments)
            with self.lock:
                if epoch != self.epoch:
                    continue
                self.data["heard"] = text
                self.event(
                    "transcript", text=text, seconds=round(time.monotonic() - start, 2)
                )

    def screen(self):
        pressed = [False, False]
        changed = [0.0, 0.0]
        while not self.done.is_set():
            if self.display:
                self.display.show(render(self.snapshot(), time.monotonic()))
                for i, pin in enumerate((self.display.a, self.display.b)):
                    down = not pin.value
                    now = time.monotonic()
                    if down != pressed[i] and now - changed[i] > 0.15:
                        pressed[i] = down
                        changed[i] = now
                        if down:
                            mode = self.snapshot()["state"]
                            action = (
                                ("confirm" if i == 0 else "change")
                                if mode == "confirm"
                                else ("listen" if i == 0 else "stop")
                            )
                            self.event("button", button="A" if i == 0 else "B")
                            self.action(action, {})
            self.done.wait(0.1)

    def close(self):
        self.done.set()
        self.cancel()
        for t in self.threads:
            t.join(timeout=3)
        if self.display:
            self.display.close()


def create_app(engine):
    app = Flask(__name__)

    @app.get("/")
    def index():
        return send_file(ROOT / "controller.html")

    @app.get("/api/state")
    def status():
        return jsonify(engine.snapshot())

    @app.get("/screen.png")
    def screen():
        out = io.BytesIO()
        render(engine.snapshot(), time.monotonic()).save(out, format="PNG")
        out.seek(0)
        response = send_file(out, mimetype="image/png")
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.post("/api/action")
    def action():
        if not request.is_json:
            return jsonify(error="JSON required."), 415
        origin = request.headers.get("Origin")
        if origin and origin != request.host_url.rstrip("/"):
            return jsonify(error="Origin not allowed."), 403
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="Object required."), 400
        try:
            engine.action(payload.get("action"), payload)
        except ValueError as exc:
            return jsonify(error=str(exc)), 400
        return jsonify(ok=True)

    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-screen", action="store_true")
    parser.add_argument(
        "--min-silence", type=float, choices=[0.2, 0.8, 1.5], default=0.8
    )
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    engine = Engine(args.no_screen, args.min_silence)
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    try:
        create_app(engine).run(
            host="127.0.0.1", port=args.port, threaded=True, use_reloader=False
        )
    finally:
        engine.close()
