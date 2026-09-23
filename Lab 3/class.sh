#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -x .venv/bin/python ]]; then echo 'First run: bash setup.sh'; exit 1; fi
source .venv/bin/activate
export HF_HOME="$PWD/.cache/huggingface"
mkdir -p results
while true; do
  printf '\n1 Audio devices and recording check\n2 Compare voices and greet Ghaith\n3 Record speech and compare tiny.en / base.en\n4 Ask for a number and record the answer\n5 Turn-taking: 0.2 seconds\n6 Turn-taking: 0.8 seconds\n7 Turn-taking: 1.5 seconds\n8 Echo bot\n9 One Thing wizard controller + audio recording\n10 Wizard with Mini PiTFT states\n11 Save experiment observations\n12 Revise a reply after initial feedback\n13 Save participant feedback\n14 Build report evidence worksheet\n15 Software and audio readiness check\n0 Exit\n'
  read -r -p 'Choose: ' choice
  case "$choice" in
    1) python exercises.py audio || true ;;
    2) espeak-ng "Hello Ghaith. Let's find one small thing to start with today."; printf '%s\n' "Hello Ghaith. Let's find one small thing to start with today." | festival --tts; bash greet.sh ;;
    3) python exercises.py compare || true ;;
    4) python exercises.py number || true ;;
    5|6|7) case "$choice" in 5) silence=0.2;; 6) silence=0.8;; 7) silence=1.5;; esac
      python -u speech-scripts/listen.py --min-silence "$silence" 2>&1 | tee "results/vad-${silence}-$(date +%Y%m%d-%H%M%S).txt" || true ;;
    8) python -u speech-scripts/echo_bot.py 2>&1 | tee "results/echo-$(date +%Y%m%d-%H%M%S).txt" || true ;;
    9) python wizard.py --record || true ;;
    10) bash screen_session.sh || true ;;
    11) python evidence.py experiments || true ;;
    12) python evidence.py revise || true ;;
    13) python evidence.py feedback || true ;;
    14) python evidence.py worksheet || true ;;
    15) python preflight.py || true ;;
    0) exit 0 ;;
    *) echo 'Choose 0 through 15.' ;;
  esac
  read -r -p 'Press Enter for the menu.' _
done
