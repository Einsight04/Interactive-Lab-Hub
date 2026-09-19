# Evidence and recording checklist

## Recorded by automated checks

- [Pi environment](pi-environment.txt): device model, hostname, Wi-Fi MAC, SPI devices.
- [Pi tests and hardware smoke run](pi-smoke-test.txt): eight tests and a 28-second accelerated run using the SPI display driver. Successful execution confirms software/driver operation, not visual appearance or physical button presses.
- [CLI clock](cli-clock.txt): terminal output captured on the Pi.
- [Display checks](display-checks.txt): bounded runs of the supplied screen test and completed Part D clock.
- [Software demo](software-demo.mp4): rendered from the real clock model. This is **not footage of the Pi**.

- [Startup service](service-status.txt): enabled, active, and running with zero restarts at verification.

## Still needed for the assignment

1. A photo of this Pi displaying `piscreen.service`, with its MAC visible.
2. A photo of the actual color screen test. Check A (white), B (chosen color), and both (backlight off).
3. A short camera video of `window_sweep.py --demo`, the first iteration.
4. A short camera video of `window_clock.py --demo`. Press A to start, A to pause, A to resume, B to enter a break, then hold A+B for one second to reset. A 25-second work session and 5-second break make transitions visible.
5. Real comments from three peers and confirmation that outgoing feedback was delivered.
6. A physical check of kit contents; the parts list distinguishes detected hardware from unverified items.

## Recording commands (on the Pi)

Only one display process can run at a time. Stop the custom clock first:

```sh
sudo systemctl stop window-clock.service
sudo systemctl start piscreen.service
# Take boot-screen photo, then:
sudo systemctl stop piscreen.service
cd /home/pi/lab-hub/'Lab 2'
/home/pi/venv/bin/python screen_test.py
# Enter blue, test buttons, take photo; Ctrl-C to exit.
/home/pi/venv/bin/python window_sweep.py --demo
# Record first iteration; Ctrl-C.
/home/pi/venv/bin/python window_clock.py --demo
# Record final interaction; Ctrl-C.
sudo systemctl start window-clock.service
```

Save real media here and link them from the report. Do not replace these with synthesized hardware photographs.
