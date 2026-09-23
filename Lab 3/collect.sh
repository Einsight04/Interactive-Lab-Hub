#!/usr/bin/env bash
# Run on the Mac. Each backup is separate and never overwrites an earlier session.
set -euo pipefail
cd "$(dirname "$0")"
TARGET="${1:-pi}"
mkdir -p results
DEST="$(mktemp -d "$PWD/results/pi-backup-$(date +%Y%m%d-%H%M%S)-XXXXXX")"
ssh -o ConnectTimeout=8 "$TARGET" 'cd /home/pi/lab-hub/"Lab 3" && .venv/bin/python evidence.py worksheet && test -d results' >/dev/null
ssh "$TARGET" 'cd /home/pi/lab-hub/"Lab 3" && tar -cf - results' | tar -xf - -C "$DEST"
printf 'Saved Pi recordings and notes to: %s/results\n' "$DEST"
