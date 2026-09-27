#!/usr/bin/env python3
"""Part B: ask out loud for a number, record the spoken answer, transcribe it.

The Pi asks the question with Piper, records until you stop talking (Silero
VAD), transcribes with faster-whisper, and reads back the number it found.
Every answer is appended to results/numbers.csv next to the saved audio, so
recognition errors on digits can be compared afterwards.

    python ask_number.py
    python ask_number.py --question "What is your zip code?" --model base.en
"""

import argparse
import csv
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import sherpa_onnx
import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel
from piper import PiperVoice

SAMPLE_RATE = 16000
LAB_DIR = Path(__file__).resolve().parent
RESULTS = LAB_DIR / "results"
VAD_MODEL = LAB_DIR / "models" / "silero_vad.onnx"
VOICE = LAB_DIR / "voices" / "en_US-lessac-medium.onnx"

WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen "
    "fourteen fifteen sixteen seventeen eighteen nineteen".split())}
WORDS.update({"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "oh": 0})


def say(voice: PiperVoice, text: str) -> None:
    for chunk in voice.synthesize(text):
        sd.play(np.frombuffer(chunk.audio_int16_bytes, dtype=np.int16),
                samplerate=chunk.sample_rate)
        sd.wait()


def record_turn(min_silence: float, timeout: float) -> np.ndarray:
    """Record from the mic until one utterance ends, or `timeout` seconds pass."""
    config = sherpa_onnx.VadModelConfig()
    config.silero_vad.model = str(VAD_MODEL)
    config.silero_vad.min_silence_duration = min_silence
    config.sample_rate = SAMPLE_RATE
    vad = sherpa_onnx.VoiceActivityDetector(config, buffer_size_in_seconds=30)
    window = config.silero_vad.window_size

    buffer = np.empty(0, dtype=np.float32)
    deadline = time.monotonic() + timeout
    with sd.InputStream(channels=1, dtype="float32", samplerate=SAMPLE_RATE) as stream:
        while time.monotonic() < deadline:
            chunk, _ = stream.read(int(0.1 * SAMPLE_RATE))
            buffer = np.concatenate([buffer, chunk.reshape(-1)])
            while len(buffer) >= window:
                vad.accept_waveform(buffer[:window])
                buffer = buffer[window:]
            if not vad.empty():
                return np.array(vad.front.samples, dtype=np.float32)
    return np.empty(0, dtype=np.float32)


def to_number(text: str) -> str:
    """Every number in the answer, in order: digits as written, or number words
    (\"twenty five\" -> 25). \"Ten, actually fifteen\" gives \"10 15\"."""
    numbers = []
    previous_word = None
    for token in re.findall(r"\d+|[a-z]+", text.lower().replace(",", "")):
        if token.isdigit():
            numbers.append(token)
            previous_word = None
        elif token in WORDS:
            value = WORDS[token]
            if previous_word in {"twenty", "thirty", "forty", "fifty", "sixty",
                                 "seventy", "eighty", "ninety"} and 0 < value < 10:
                numbers[-1] = str(int(numbers[-1]) + value)
            else:
                numbers.append(str(value))
            previous_word = token
        else:
            previous_word = None
    return " ".join(numbers)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--question", default="How many minutes do you have for one small task?")
    parser.add_argument("--model", default="tiny.en")
    parser.add_argument("--min-silence", type=float, default=0.8,
                        help="seconds of silence that end the answer (default: 0.8)")
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()

    for path in (VAD_MODEL, VOICE):
        if not path.is_file():
            sys.exit(f"{path} not found. Run speech-scripts/setup.sh first.")

    print("Loading models...", flush=True)
    recognizer = WhisperModel(args.model, device="cpu", compute_type="int8")
    voice = PiperVoice.load(str(VOICE))

    print(f"Asking: {args.question}")
    say(voice, args.question)
    audio = record_turn(args.min_silence, args.timeout)
    if not len(audio):
        say(voice, "I didn't hear an answer.")
        sys.exit("No speech detected.")

    t0 = time.perf_counter()
    segments, _ = recognizer.transcribe(audio, beam_size=1, language="en")
    heard = " ".join(s.text.strip() for s in segments)
    elapsed = time.perf_counter() - t0
    number = to_number(heard)

    print(f"heard:  {heard!r}")
    print(f"number: {number or '(none found)'}")
    print(f"asr:    {elapsed:.2f}s for {len(audio) / SAMPLE_RATE:.2f}s of audio")
    say(voice, f"I heard {number.replace(' ', ', ')}." if number else "Sorry, I didn't catch a number.")

    RESULTS.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    wav = RESULTS / f"number-{stamp}.wav"
    sf.write(str(wav), audio, SAMPLE_RATE, subtype="PCM_16")
    log = RESULTS / "numbers.csv"
    new = not log.exists()
    with log.open("a", newline="") as f:
        writer = csv.writer(f)
        if new:
            writer.writerow(["time", "question", "model", "heard", "number", "asr_seconds", "audio"])
        writer.writerow([stamp, args.question, args.model, heard, number, f"{elapsed:.2f}", wav.name])
    print(f"saved:  results/{wav.name}, results/numbers.csv")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
