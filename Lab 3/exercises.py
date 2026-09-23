"""Audio checks and actual measurements for Lab 3, saved locally in results/."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time
from datetime import datetime

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("HF_HOME", str(ROOT / ".cache/huggingface"))
RESULTS = ROOT / "results"


def record(path, seconds=5):
    import sounddevice as sd
    import soundfile as sf
    input("Press Enter when ready to speak for five seconds. ")
    print("Recording now...")
    samples = sd.rec(int(seconds * 16000), samplerate=16000, channels=1, dtype="float32")
    sd.wait()
    sf.write(str(path), samples, 16000, subtype="PCM_16")
    print("Saved", path)


def say(text):
    import sys
    wav = RESULTS / "prompt.wav"
    subprocess.run([sys.executable, "-m", "piper", "--model",
                    str(ROOT / "voices/en_US-lessac-medium.onnx"),
                    "--output-file", str(wav), "--", text], check=True)
    subprocess.run(["aplay", str(wav)], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exercise", choices=["audio", "compare", "number"])
    args = parser.parse_args()
    RESULTS.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    wav = RESULTS / f"{args.exercise}-{stamp}.wav"
    if args.exercise == "audio":
        import sounddevice as sd
        print(sd.query_devices())
        print("Defaults:", sd.default.device)
        subprocess.run(["aplay", "-l"], check=True)
        subprocess.run(["arecord", "-l"], check=True)
        record(wav)
        subprocess.run(["aplay", str(wav)], check=True)
        print("Confirm you heard your own voice clearly before continuing.")
        return
    if args.exercise == "number":
        say("How many minutes do you have for one small task?")
    record(wav)
    expected = input("Type what you actually said, for the accuracy comparison: ")
    import soundfile as sf
    from faster_whisper import WhisperModel
    duration = sf.info(str(wav)).duration
    rows = []
    for name in (("tiny.en", "base.en") if args.exercise == "compare" else ("tiny.en",)):
        start = time.perf_counter()
        model = WhisperModel(name, device="cpu", compute_type="int8")
        load_seconds = time.perf_counter() - start
        start = time.perf_counter()
        segments, _ = model.transcribe(str(wav), beam_size=1, language="en")
        transcript = " ".join(s.text.strip() for s in segments)
        elapsed = time.perf_counter() - start
        row = dict(model=name, audio_seconds=duration, load_seconds=load_seconds,
                   transcription_seconds=elapsed, real_time_factor=elapsed/duration,
                   transcript=transcript, actual_words=expected)
        rows.append(row)
        print(json.dumps(row, indent=2))
        del model
    result = wav.with_suffix(".json")
    result.write_text(json.dumps(rows, indent=2) + "\n")
    print("Measurements saved:", result)


if __name__ == "__main__":
    main()
