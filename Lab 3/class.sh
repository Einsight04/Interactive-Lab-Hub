#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -x .venv/bin/python ]]; then echo 'First run: bash setup.sh'; exit 1; fi
source .venv/bin/activate
export HF_HOME="$PWD/.cache/huggingface"
mkdir -p results
while true; do
  printf '\n1 Audio devices and recording check\n2 Compare voices and greet Ghaith\n3 Record speech and compare tiny.en / base.en\n4 Ask for a number and record the answer\n5 Turn-taking: 0.2 seconds\n6 Turn-taking: 0.8 seconds\n7 Turn-taking: 1.5 seconds\n8 Echo bot\n9 One Thing wizard controller\n0 Exit\n'
  read -r -p 'Choose: ' choice
  case "$choice" in
    1) python exercises.py audio ;;
    2) espeak-ng "Hello Ghaith. Let's find one small thing to start with today."; printf '%s\n' "Hello Ghaith. Let's find one small thing to start with today." | festival --tts; bash greet.sh ;;
    3) python exercises.py compare ;;
    4) python exercises.py number ;;
    5|6|7) case "$choice" in 5) silence=0.2;; 6) silence=0.8;; 7) silence=1.5;; esac
      python speech-scripts/listen.py --min-silence "$silence" || true ;;
    8) python speech-scripts/echo_bot.py || true ;;
    9) python wizard.py || true ;;
    0) exit 0 ;;
    *) echo 'Choose 0 through 9.' ;;
  esac
  read -r -p 'Press Enter for the menu.' _
done
