#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p results
TEXT="Hello Ghaith. Let's find one small thing to start with today."
.venv/bin/python -m piper --model "$PWD/voices/en_US-lessac-medium.onnx" --output-file results/greeting.wav -- "$TEXT"
aplay results/greeting.wav
