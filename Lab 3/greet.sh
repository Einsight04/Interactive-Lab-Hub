#!/usr/bin/env bash
# Part A: the Pi greets a person by name with Piper, streamed straight to the speaker.
#
#   ./greet.sh Ghaith           # Piper (our pick)
#   ./greet.sh Ghaith compare   # same greeting in espeak, festival, then Piper

set -euo pipefail
VOICES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/voices"
GREETING="Hello ${1:-there}. Let's find one small thing to start with today."

piper() {
  python3 -m piper \
    --model en_US-lessac-medium \
    --data-dir "$VOICES_DIR" \
    --output-raw \
    -- "$GREETING" \
    | aplay -q -r 22050 -f S16_LE -t raw -
}

if [[ "${2:-}" == "compare" ]]; then
  echo "espeak";   espeak-ng "$GREETING"
  echo "festival"; echo "$GREETING" | festival --tts
  echo "piper"
fi
piper
