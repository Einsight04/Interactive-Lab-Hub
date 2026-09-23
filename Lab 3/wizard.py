"""One Thing: human-controlled dialogue with local audio and timestamped events."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import threading
import time

from exercises import ROOT, RESULTS

PROMPTS = {
    "1": "What is one thing you want to get started on?",
    "2": "How many minutes do you have?",
    "3": "What is the smallest first step you could take?",
    "4": "Sorry, I missed that. Could you say it once more?",
    "5": "Would you like a smaller step, or a different task?",
    "6": "Ready when you are. You can begin, or tell me what to change.",
    "7": "Okay. We can stop here.",
    "8": "Would you like more time?",
}


class Recorder:
    """Read audio on a worker, keeping disk writes out of an audio callback."""
    def __init__(self, path):
        import sounddevice as sd
        import soundfile as sf
        self.stop = threading.Event()
        self.error = None
        self.overflows = 0
        self.file = sf.SoundFile(str(path), mode="w", samplerate=16000,
                                 channels=1, subtype="PCM_16")
        try:
            self.stream = sd.InputStream(samplerate=16000, channels=1, dtype="float32")
            self.stream.start()
        except Exception:
            self.file.close()
            raise
        self.worker = threading.Thread(target=self.run, daemon=True)
        self.worker.start()

    def run(self):
        try:
            while not self.stop.is_set():
                audio, overflow = self.stream.read(1600)
                self.overflows += int(overflow)
                self.file.write(audio)
        except Exception as exc:
            self.error = str(exc)

    def close(self):
        self.stop.set()
        self.worker.join(timeout=2)
        if self.worker.is_alive():
            self.stream.abort()
            self.worker.join()
        self.stream.close()
        self.file.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="store_true", help="offer local microphone recording")
    args = parser.parse_args()
    RESULTS.mkdir(exist_ok=True)
    session = RESULTS / ("session-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    session.mkdir()
    start = time.monotonic()
    state_path = RESULTS / "state.json"

    def event(kind, **fields):
        row = dict(time=datetime.now().isoformat(), elapsed=round(time.monotonic()-start, 3),
                   event=kind, **fields)
        with (session / "events.jsonl").open("a") as f:
            f.write(json.dumps(row) + "\n")

    def state(value):
        temp = state_path.with_suffix(".tmp")
        temp.write_text(json.dumps({"state": value}))
        temp.replace(state_path)
        event("state", value=value)
        print("\n" + value.upper(), flush=True)

    prompts = dict(PROMPTS)
    config = RESULTS / "prompts.json"
    if config.exists():
        saved = json.loads(config.read_text())
        if not isinstance(saved, dict) or any(k not in PROMPTS or not isinstance(v, str) or not v.strip() for k, v in saved.items()):
            raise ValueError("Invalid prompts.json: expected reply numbers and nonempty text")
        prompts.update(saved)
    print("Initial session or revised test? Label this session before starting.")
    label = input("Session label (for example initial-P1 or revised-P2): ").strip()
    event("session_metadata", label=label, prompts=prompts)
    recorder = None
    audio_device = None
    try:
        state("loading")
        import numpy as np
        import sounddevice as sd
        audio_device = sd
        from piper import PiperVoice
        voice = PiperVoice.load(str(ROOT / "voices/en_US-lessac-medium.onnx"))
        if args.record and input("Has the participant agreed to audio recording? [y/N] ").lower() == "y":
            recorder = Recorder(session / "interaction.wav")
            event("recording_started")
            print("Microphone recording started. Also record a phone video of the interaction.")
        else:
            print("No microphone recording. Use an agreed phone recording for study evidence.")
        print("Controls: number or custom reply; /think; /listen; /note text; /quit.")
        print("Do not show the participant your dialogue. Wait for their full answer.")
        for key, text in prompts.items():
            print(f"{key}: {text}")
        state("listening")
        while True:
            if recorder and recorder.error:
                print("RECORDING ERROR:", recorder.error)
                event("recording_error", detail=recorder.error)
                break
            answer = input("Reply or command: ").strip()
            if answer == "/quit":
                break
            if not answer:
                continue
            if answer in ("/think", "/listen"):
                state("thinking" if answer == "/think" else "listening")
                continue
            if answer.startswith("/note "):
                event("operator_note", text=answer[6:])
                continue
            if answer.startswith("/"):
                print("Unknown command. Use /think, /listen, /note text, or /quit.")
                continue
            text = prompts.get(answer, answer)
            state("thinking")
            t0 = time.monotonic()
            chunks = list(voice.synthesize(text))
            if not chunks:
                raise RuntimeError("Piper returned no audio")
            samples = np.concatenate([np.frombuffer(c.audio_int16_bytes, dtype=np.int16) for c in chunks])
            event("reply_ready", text=text, synthesis_seconds=time.monotonic()-t0)
            state("speaking")
            event("speech_started", text=text)
            sd.play(samples, samplerate=chunks[0].sample_rate)
            sd.wait()
            event("speech_finished", text=text)
            state("listening")
    except (KeyboardInterrupt, EOFError):
        print("\nSession stopped.")
    finally:
        if audio_device is not None:
            audio_device.stop()
        if recorder:
            recorder.close()
            event("recording_stopped", overflows=recorder.overflows, error=recorder.error)
        state("idle")
        print("Session saved:", session)


if __name__ == "__main__":
    main()
