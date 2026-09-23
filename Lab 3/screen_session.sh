#!/usr/bin/env bash
# Optional display mode. Temporarily releases the screen from Lab 2 and restores it.
set -euo pipefail
cd "$(dirname "$0")"
[[ -x /home/pi/venv/bin/python ]] || { echo 'Lab 2 display environment is missing. Use menu 9.'; exit 1; }
active=()
screen_pid=''
cleanup() {
  if [[ -n "$screen_pid" ]]; then
    kill -INT "$screen_pid" 2>/dev/null || true
    sleep .2
    kill "$screen_pid" 2>/dev/null || true
    wait "$screen_pid" 2>/dev/null || true
  fi
  for service in "${active[@]}"; do sudo systemctl start "$service"; done
}
trap cleanup EXIT
trap 'exit 130' INT TERM
sudo -v
for service in window-clock.service piscreen.service; do
  if systemctl is-active --quiet "$service"; then
    active+=("$service")
    sudo systemctl stop "$service"
  fi
done
mkdir -p results
printf '{"state":"idle"}\n' > results/state.json
/home/pi/venv/bin/python status_display.py &
screen_pid=$!
sleep 1
kill -0 "$screen_pid" 2>/dev/null || { echo 'Display failed. Use menu 9 for audio only.'; exit 1; }
.venv/bin/python wizard.py --record
