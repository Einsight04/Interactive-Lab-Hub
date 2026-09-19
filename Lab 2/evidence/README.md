# Evidence and recording checklist

## Recorded by automated checks

- [Pi environment](pi-environment.txt): device model, hostname, Wi-Fi MAC, SPI devices.
- [Pi tests and hardware smoke run](pi-smoke-test.txt): eight tests and a 28-second accelerated run using the SPI display driver. Successful execution confirms software/driver operation, not visual appearance or physical button presses.
- [CLI clock](cli-clock.txt): terminal output captured on the Pi.
- [Display checks](display-checks.txt): bounded runs of the supplied screen test and completed Part D clock.
- [Software demo](software-demo.mp4): rendered from the real clock model. This is **not footage of the Pi**.

- [Startup service](service-status.txt): enabled, active, and running with zero restarts at verification.

## User-confirmed checks

Ghaith confirmed the hardware checks are complete, following the request to check the buttons and kit contents. This is user-reported confirmation; the automated logs above do not document physical button presses.

## Camera evidence

[Startup-screen photo](pi-startup.jpg), supplied by Ghaith as IMG_0854.jpg. Shows the actual Pi and Mini PiTFT running the startup information screen, with MAC `88:a2:9e:c8:53:9d` readable. Original image copied without editing.

[Color-test photo](pi-color-test.jpg), supplied by Ghaith as image.jpg while the blue test was running. Shows the lower button being held and blue light around the display; the center is overexposed. Original image copied without editing.

[Basic prototype camera video](pi-basic-demo.mp4), supplied by Ghaith as IMG_0866.mov. The 26.17-second recording shows the actual display losing windows and reaching “STEP AWAY” at the end. MOV remuxed to MP4 without re-encoding; video and audio preserved.

[Final timer camera video](pi-final-demo.mp4), supplied by Ghaith as IMG_0867.mov. Duration 38.31 seconds; shows the work-to-break sequence and ends on “READY?” MOV remuxed to MP4 without re-encoding, preserving video and audio. [Device log during recording](pi-button-recording.txt) confirms physical A start/pause/resume and B break events.

## Still needed for the assignment

1. Real comments from three peers and confirmation that outgoing feedback was delivered.

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
