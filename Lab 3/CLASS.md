# Lab 3 class kit

## Ten minutes at home

1. Plug the USB microphone and speaker into the Pi. Connect Pi power and the laptop connection as before.
2. On the Mac, open Terminal and run:

   ```sh
   cd "/Users/ghaith/Code/Interactive-Lab-Hub/Lab 3"
   bash deploy.sh
   ```

   Keep internet available during setup. The setup reuses any downloaded files. First installation can exceed ten minutes depending on the connection and system packages. A successful run ends with **Software ready**. If `pi` cannot resolve, use `bash deploy.sh pi@THE_PI_IP` with the current IP shown by the Pi.
3. Open the Pi's menu:

   ```sh
   ssh -t pi 'cd /home/pi/lab-hub/"Lab 3" && bash class.sh'
   ```

4. Choose **1** and record five seconds. Confirm playback is your voice. Choose **2** and confirm you can hear all three greetings.
5. Pack Pi, power, microphone, speaker, laptop, cables, and your phone for recording. Shut down the Pi before unplugging it: `sudo poweroff` from a Pi terminal.

If the wrong device is selected, run `wpctl status` on the Pi, then `wpctl set-default ID` for the USB input and output IDs. Unmute them with `wpctl set-mute @DEFAULT_AUDIO_SOURCE@ 0` and `wpctl set-mute @DEFAULT_AUDIO_SINK@ 0`. Run option 1 again. If there is no PipeWire service, inspect `arecord -l` and `aplay -l` and configure ALSA before continuing.

## In class: Part 1

Open the same menu over SSH. The scripts process speech locally.

- **2: Voices.** Listen to the same greeting in espeak, Festival, and Piper. Note a specific difference in meaning or personality.
- **3: Recognition.** Say the same five-second sentence once. Enter the exact words afterward. The script runs tiny.en and base.en on that recording and saves measured timings and transcripts. RTF is transcription seconds divided by audio seconds; model loading is reported separately.
- **4: Numerical input.** The Pi asks how many minutes you have, then records your spoken answer after Enter. Try a number spoken naturally and compare the transcript to the real answer.
- **5, 6, 7: Turn-taking.** Try “I want to start... [pause] my reading” and a longer explanation at each silence setting. Note premature cuts and the feeling of delay. Ctrl+C returns to the menu.
- **8: Echo bot.** Say one short sentence and listen for the response gap.
- Read the proposed storyboard and dialogue in [the report](README.md#d-design-and-storyboard). Adjust it after the exercises.
- **9: Act it out.** Ask a partner to try the desk coach without showing them the script. Ask permission to record a phone video with audible speech. Use the controller to select or type spoken replies. Record what surprised you and what you would change. Option 9 offers microphone recording after permission; also take a phone video. Type `/note your observation` to save a note without speaking it. End with `/quit`. Option 10 adds the Mini PiTFT status screen if its hardware check passes.

Recordings and measurements are in `results/` on the Pi and are excluded from Git. Copy them back to the Mac after class:

```sh
cd "/Users/ghaith/Code/Interactive-Lab-Hub/Lab 3"
mkdir -p results
ssh pi 'cd /home/pi/lab-hub/"Lab 3" && tar -cf - results' | tar -xf -
```

## Notes to fill in from the actual session

- Voice comparison and preferred voice:
- Exact sentence and errors for each recognition model:
- tiny.en RTF / base.en RTF:
- When the extra accuracy was worth the delay:
- Numerical answer and recognized answer:
- 0.2 / 0.8 / 1.5 second turn-taking observations:
- Partner and interaction video:
- Unexpected response or misunderstanding:
- Change to wording, timing, or dialogue:

## Part 2 later

Use Part 1 observations to revise the storyboard and interaction. Check the prepared listening/thinking/speaking screen in option 10 and revise it as needed. Test the revised Pi prototype with at least two people. Capture videos of both the device and controller, then answer the reflection questions in the assignment README. These activities are still to be completed.

The [report](README.md) has the prepared design and implementation inline. Its pending sections need actual results and recordings before submission.

## Suggested class order

1. **5 minutes:** audio check and three voices (options 1 and 2).
2. **10 minutes:** recognition comparison and numerical answer (3 and 4).
3. **10 minutes:** three silence thresholds, then the echo bot (5 through 8).
4. **10 minutes:** one partner session with option 9, phone video, and short follow-up questions.
5. **5 minutes:** record the main surprise and a specific design change. Keep the measurements and video.

These are planning estimates, not a course time requirement. Part 1 needs a partner interaction. The two-user test of the revised design belongs to Part 2; do it after revising from Part 1, if there is time today, or during the next session.

For each participant, note: session file name, task they chose, exact words around any misunderstanding, where the device interrupted or delayed them, their answer to “What would you change?”, and the revision you made. Keep the script hidden during the interaction.
