"""Optional Mini PiTFT status display, using the installed Lab 2 driver."""
import importlib.util
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parent
LABELS = {
    'loading': ('GETTING READY', 'One moment', '#bda7ff'),
    'listening': ('LISTENING', 'Your turn', '#6ee7c7'),
    'thinking': ('THINKING', 'Please wait', '#ffc66d'),
    'speaking': ('SPEAKING', 'My turn', '#93c5fd'),
    'idle': ('ONE THING', 'Ready when you are', '#aab2c0'),
}


def main():
    from PIL import Image, ImageDraw
    spec = importlib.util.spec_from_file_location('clock_display', ROOT.parent / 'Lab 2/window_clock.py')
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    import signal
    def stop(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    display = module.Display()
    previous = None
    try:
        while True:
            try:
                state = json.loads((ROOT / 'results/state.json').read_text())['state']
            except (FileNotFoundError, ValueError, KeyError):
                state = 'idle'
            if state != previous:
                title, subtitle, color = LABELS.get(state, LABELS['idle'])
                image = Image.new('RGB', (240, 135), '#111827')
                draw = ImageDraw.Draw(image)
                draw.text((12, 12), 'ONE THING', font=module.font(12), fill='#aab2c0')
                draw.text((12, 45), title, font=module.font(22), fill=color)
                draw.text((12, 88), subtitle, font=module.font(15), fill='white')
                display.show(image)
                previous = state
            time.sleep(.1)
    finally:
        display.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
