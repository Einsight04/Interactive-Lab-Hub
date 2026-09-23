#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export HF_HOME="$PWD/.cache/huggingface"
sudo apt-get update
sudo apt-get install -y python3-venv alsa-utils libportaudio2 espeak-ng festival festvox-kallpc16k flite wget
python3 -m venv .venv
source .venv/bin/activate
if compgen -G '.cache/wheels/*.whl' > /dev/null; then
  python -m pip install --no-index --find-links .cache/wheels -r requirements.txt
else
  python -m pip install -r requirements.txt
fi
SKIP_SYSTEM_PACKAGES=1 bash speech-scripts/setup.sh
python - <<'PYTHON'
from faster_whisper import WhisperModel
for model in ('tiny.en', 'base.en'):
    WhisperModel(model, device='cpu', compute_type='int8')
    print(model, 'ready')
PYTHON
printf '\nSoftware ready. Run: bash class.sh\n'
