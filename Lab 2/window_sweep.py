"""First iteration: a building loses one window per minute, then holds.
Use --demo for one window per second. No buttons in this iteration.
"""
import argparse
import time
from window_clock import Clock, Display, render
from PIL import ImageDraw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--demo', action='store_true')
    parser.add_argument('--seconds', type=float)
    args = parser.parse_args()
    clock = Clock(work=25 if args.demo else 1500, running=True)
    display = Display()
    start = previous = time.monotonic()
    try:
        while args.seconds is None or time.monotonic() - start < args.seconds:
            now = time.monotonic()
            clock.tick(now - previous)
            previous = now
            im = render(clock, demo=args.demo)
            # This first pass has no controls; do not show the final version's hints.
            draw = ImageDraw.Draw(im)
            draw.rectangle((0, 119, 239, 134), fill='#111827')
            if clock.done:
                draw.rectangle((125, 79, 239, 112), fill='#111827')
            display.show(im)
            time.sleep(.1)
    except KeyboardInterrupt:
        pass
    finally:
        display.close()


if __name__ == '__main__':
    main()
