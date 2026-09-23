#!/usr/bin/env bash
# Run on the Mac after connecting the Pi. Optional argument: pi@IP_ADDRESS.
set -euo pipefail
cd "$(dirname "$0")"
TARGET="${1:-pi}"
ssh -o ConnectTimeout=8 "$TARGET" 'mkdir -p /home/pi/lab-hub/"Lab 3"'
# Copy only this lab, including downloaded models. Keep recordings and environments on the Pi.
tar --exclude='./.venv' --exclude='./results' --exclude='__pycache__' -cf - . | ssh "$TARGET" 'tar -xf - -C /home/pi/lab-hub/"Lab 3"'
ssh -t "$TARGET" 'cd /home/pi/lab-hub/"Lab 3" && bash setup.sh'
printf '\nDeployment finished. Open the class menu with:\n'
printf '%s\n' "ssh -t $TARGET 'cd /home/pi/lab-hub/\"Lab 3\" && bash class.sh'"
