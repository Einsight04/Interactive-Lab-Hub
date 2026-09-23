# Lab 3: finish both parts in class

The report, storyboard, scripts, and controller are prepared. Today you need actual audio results, an initial interaction, a revision based on that interaction, and two tests of the revised version. No results or participant feedback have been filled in in advance.

## At home: connect and deploy

Connect the USB microphone and speaker to the Pi, and connect the Pi to the laptop as before. Keep internet available for system packages. On the Mac:

```sh
cd "/Users/ghaith/Code/Interactive-Lab-Hub/Lab 3"
bash deploy.sh
```

The laptop already has the Pi Python packages and speech models cached. Installation can still exceed ten minutes. Wait for **Software ready**. Then open the menu:

```sh
ssh -t pi 'cd /home/pi/lab-hub/"Lab 3" && bash class.sh'
```

Choose **15** for the software/device check, then **1** to record and hear your voice. Choose **2** to check spoken output. A passing software check does not replace listening to the speaker.

If `pi` cannot resolve, use `bash deploy.sh pi@CURRENT_IP` and use the same address in place of `pi` in SSH commands. If audio uses the wrong device, run `wpctl status` on the Pi and `wpctl set-default ID` for the USB source and sink. Unmute with `wpctl set-mute @DEFAULT_AUDIO_SOURCE@ 0` and `wpctl set-mute @DEFAULT_AUDIO_SINK@ 0`. If PipeWire is unavailable, use `arecord -l` and `aplay -l` to diagnose ALSA with the TA or send the output here.

Pack the Pi, microphone, speaker, power, cables, laptop, and phone. Before unplugging, exit the menu and run `ssh pi 'sudo poweroff'`; wait for shutdown.

## In class: do these in order

### 1. Speech experiments

Open the menu with the SSH command above.

| Menu | What to do | What gets saved / what to note |
| --- | --- | --- |
| 2 | Hear the same greeting in three voices | Note a concrete difference and your preferred voice |
| 3 | Record one five-second sentence, then type the exact words | WAV, tiny.en/base.en transcripts, timing, and RTF save automatically |
| 4 | Answer the Pi's question about minutes after pressing Enter | WAV, actual answer you type, recognized answer, and timing save automatically |
| 5, 6, 7 | Try a thinking pause at 0.2, 0.8, and 1.5 seconds | Transcripts and timings save to text logs; note interruptions or awkward delay |
| 8 | Say a sentence and hear it echoed | Terminal output saves; note how responsive it feels |
| 11 | Answer the observation prompts | Saves your observations as you enter them |

For options 5 through 7, try “I want to start... my reading” and “Ten... actually, fifteen minutes.” Press Ctrl+C when finished with each continuous listening exercise. You do not need a separate video of every exercise.

### 2. Initial partner interaction

- Ask a partner to try the device and ask permission to record.
- Start a phone video with the Pi, participant, and audible conversation. Keep the prepared dialogue and your controller hidden from the participant.
- Choose **9**, label the session `initial-P1`, and answer the recording-permission prompt accurately.
- Tell them: “This helps you choose a small next step. Try it using something you actually need to do.”
- Select **1**, **2**, and **3** when appropriate to ask about the task, time, and first step. Wait for their full answers. Type a custom confirmation such as “Ten minutes to choose your report photos. Does that sound right?” using their actual answers.
- Respond naturally to corrections. `/think` and `/listen` change the state; `/note text` saves a silent operator note. End with `/quit`.
- Ask: “What confused you?”, “Did it interrupt you or wait too long?”, and “What would you change?”
- Choose **13** and save what actually happened and what they said, including the video filename.

The session directory printed at the end contains `events.jsonl` and, if enabled, `interaction.wav`. Phone video is still needed for visual evidence.

### 3. Revise from that feedback

Choose **12**. Enter the observed problem, select a reply, and write improved wording. For example, if a participant did not understand “smallest first step,” a more concrete question might help. Only make that claim if it actually happened.

The change saves with its before/after wording and reason. The next controller session loads it automatically. This produces a revised dialogue script based on real evidence. If the feedback calls for a different kind of change, save it with option 13 and make the appropriate change before claiming the revised version was tested.

### 4. Test the revised version with two people

Run **10** for each test if the Pi screen check passes. It adds listening/thinking/speaking labels and temporarily replaces the Lab 2 clock. Use **9** if the display fails, record the issue, and get help checking the display before claiming it worked.

- Label the sessions `revised-P1` and `revised-P2` and use two distinct people for this revised-version test.
- Record the device and participant on your phone with permission.
- Also record the controller terminal. On the Mac, press **Shift+Command+5**, choose **Record Selected Portion**, select the terminal area, and start recording before the interaction. Keep that screen out of the participant's view.
- Get their actual feedback afterward and use **13** after each session.
- Note what worked or failed in both the device interaction and your experience operating it.

The initial participant may also try the revised version, but the revised test must still include two distinct people. Do not count the initial session as a revised test.

### 5. Save everything before leaving

Choose **14** to build the report evidence worksheet. Exit the menu. On the Mac:

```sh
cd "/Users/ghaith/Code/Interactive-Lab-Hub/Lab 3"
bash collect.sh
```

Each collection creates a separate backup under `results/`. The script copies the Pi results without removing the originals. Keep the phone videos and controller recordings too. Send the videos and the backup folder here so the measured results, revised dialogue, and study reflections can be incorporated into the report.

## Leave class with this evidence

- [ ] Voice preference and concrete voice comparison.
- [ ] Same audio transcribed by tiny.en and base.en, actual timing/RTF, and error comparison.
- [ ] Numerical answer recording and transcript.
- [ ] Observations for all three silence settings and the echo loop.
- [ ] Initial interaction video and partner feedback.
- [ ] A revision with an actual reason and before/after wording.
- [ ] Revised-version interaction videos for two distinct people and their feedback.
- [ ] Controller screen recording showing how the prototype was operated.
- [ ] Results backed up to the laptop.

The [report](README.md) still needs these observations, videos, and reflections before submission. The course handout does not establish separate class-day deadlines for its two stages; this checklist aims to gather evidence for both today.
