# Recreating the Masters of Interactive Light

**COLLABORATORS:** Elliot Waxman, Ghaith Khalil

**THE MASTERWORK YOU DREW FROM THE HAT:** Project Blinkenlights (Chaos Computer Club, 2001)

![Our draw from the hat: Project Blinkenlights](images/masterwork-draw.png)

---

# The Report

## Part 0. Know Your Master

In September 2001 the Chaos Computer Club, Europe's largest hacker association, celebrated its 20th birthday by turning a building into a screen. The building was the Haus des Lehrers on Alexanderplatz in Berlin. Behind each window of the top eight floors they placed a lamp, 144 lamps in total, giving an 18 by 8 pixel display that filled a whole side of the building. A computer switched every lamp on and off through a relay, so the whole facade could show animations frame by frame. It ran every night until February 2002 and became one of the best known pieces of interactive public light art.

**The core interaction:** Anyone could call a phone number and play Pong on the building against another caller, moving their paddle with the keys on their phone. People could also send their own animations and text to be shown on the facade, including love letters. The novelty was not the game itself. It was that a building the size of a city block was answering an ordinary phone in someone's hand, in front of everyone in the square.

**Strengths:** It made a huge, ordinary building feel alive and responsive. The input was something everyone already carried, a phone, so there was no barrier to joining in. And because the display was public, one person's input became a shared moment for the whole square.

**Weaknesses:** Only two people could play at a time and everyone else could only watch. The resolution was tiny, so text had to scroll and detail was impossible. And the piece depended entirely on the building's owners, which is why it had a fixed end date.

**Sources:**
- [Project Blinkenlights on Wikipedia](https://en.wikipedia.org/wiki/Project_Blinkenlights)
- [blinkenlights.net, the project archive](http://blinkenlights.net/)

## Part A. Plan

- **Setting:** A long, boring line at night. Our version is a trendy pop-up restaurant, with a pixel-grid "building" visible to everyone in the line.
- **Players:** A bored person in the line (the sender); the strangers around them in the line (the audience, who can become senders too); the building's pixel grid (the light).
- **Activity:** Someone texts a number and their message appears on the grid for everyone in the line to see. Others in the line look up, and some text back, so the line starts talking to itself through the building. Alternatively two people in line play Pong on the grid using their phones, and the winner decides whether to swap places with the loser.
- **Goals:** The sender wants to be seen and to kill time. The strangers want something to look at, and then want to reply. The building wants to keep everyone entertained while they wait.

### Storyboards
**Iteration 1:** A straightforward visual of the original Blinkenlights interaction. A user calls the number on the building, plays Pong on the facade with their keypad, and the building thanks them when the game ends.<br><br>
![storyboard_1](images/storyboard-1.png)


**Iteration 2:** We swapped the phone call for a text message, since that is what people in a line would actually do. The interesting moment became the stranger next to the sender looking up at the grid and texting back.<br><br>
![storyboard_2](images/storyboard-2.png)


**Iteration 3:** After acting out the scene (see Part B below) we found two situations the light has to handle: two people texting at once, and nobody texting at all. This storyboard covers both.<br><br>
![storyboard_3](images/storyboard-3.png)

**Feedback we got:**

What people liked:
- It was a very cool, engaging interaction
- Latency was really good, the visuals updated super fast
- Easy to use; you can interact from any phone
- "Very cool application, I can see the relevant factor with your masterwork, like the real-time text interaction feed"

What could have been better:
- Would be cool if you could make ASCII art
- Would be fun if you could change colors or customize
- Make the letters smaller, or somehow add a second line
- Emojis!

## Part B. Act out the Interaction

Our first run-through, acting it out before the light was working: https://youtube.com/shorts/tsh5MOguhmc?feature=share

When we acted out the sequence, we discovered the following:
- The moment that sells the piece is not the sender looking at their phone, it is the stranger next to them looking up at the building. We needed to keep the camera on the line, not on the phone.
- Two people will text at the same time. On paper we had one sender and one grid; in the room, messages collided. The grid needs a queue and a way to show whose turn it is.
- A dark building between messages looks broken, not idle. The grid should keep playing its own animations when nobody is texting, so there is always something to look up at.
- Text on a low-resolution grid has to be short. Long messages scroll and lose the audience.

We used these findings to iterate on our storyboard, resulting in the final storyboard above (Iteration 3).

## Part C. Prototype the Light (light first!)

**We only focused on light this week; no other modalities.**

Instead of the Tinkerbelle tool we built our own: **Pocket Blinkenlights**, a phone-scale recreation of the original. A phone opens a web page that shows an 18 by 8 grid of windows, the same size as the real facade on the Haus des Lehrers. Each cell is one window, on or off, like the original relay-driven lamps. The grid is driven three ways, matching the original piece:

- **Text messages.** Anyone texts a real phone number and their message scrolls across the building in a 5 by 7 pixel font.
- **Phone-keypad Pong.** Two callers each get a paddle and move it with the keys on their phone.
- **Submitted animations.** A pixel editor at `/submit` lets anyone draw frames for the building; approved animations join the rotation and play whenever nobody is texting or playing.

The light drives itself from the incoming texts and calls, so no wizard is needed for the basic interaction. When there is no input, the scheduler plays the animation archive, so the building never goes dark.

**Live page:** https://pocket-blinkenlights.fly.dev (open it on a phone for the full effect)

**Code:** https://github.com/Einsight04/pocket-blinkenlights (public copy of Elliot's repo, full commit history)

The live grid, captured from the page while it was playing an idle animation between messages:<br><br>
![Pocket Blinkenlights grid, 18 by 8, mid-animation](images/grid-screenshot.png)

> **TODO (optional):** swap this for a photo of the phone showing a real text message if you have one.

**Feedback on Tinkerbelle:** Tinkerbelle controls one light at a time from a laptop, which is right for a lamp or a watch but not for a 144-pixel building. We needed many pixels responding to text and phone input at once, so it made more sense to write a small server of our own. A grid mode in Tinkerbelle, where a message or pattern drives many pixels on one phone, would have made it usable for a piece like this.

## Part D. Wizard the Device

Our system drives the light directly from texts, so the first prototype did not need a wizard. To compare, we also staged a wizarded version: one of us hid off camera and drove the grid by hand from the laptop, while the other acted the scene with the phone in the line. We recorded over Zoom.

> **TODO:** paste the link to the wizarded run-through video here.

What the comparison showed: the wizard could improvise, for example answering an unexpected message with an animation the real system does not have. The real system was faster and never missed a cue, but it can only do what we coded.

## Part E. Costume the Device

> **TODO:** if you costumed the phone as a building (cardboard shell with cut-out windows, for example), add a photo here as `images/costume.png` and a sentence on why. If not, delete this section's TODO and write "We did not costume the device this week."

**Concerns/opportunities in shaping the look:** The grid has to read as a building at a glance, so the cells should look like windows and the whole thing should stand upright, like a facade. It also has to be bright enough to be seen from the back of a line at night.

## Part F. Record

**Video Sketch:** https://youtube.com/shorts/RPhKJcqeU8U?feature=share

**Our aim:** A viewer who knows Blinkenlights should recognize the building-as-screen and the phone-as-controller immediately. A viewer who has never heard of it should come away understanding that a building can answer an ordinary phone in someone's hand, and that the fun is in everyone around seeing it happen. We tested it with three people who had not seen the project before, each texting the grid in turn.

> **TODO:** add one or two sentences on how the three users reacted (what they texted, what surprised them, what they tried that we did not expect).

**Collaborators and influences:**
- Elliot Waxman (TODO: role, e.g. built the grid page, acted the sender)
- Ghaith Khalil (TODO: role, e.g. filmed, acted the stranger)
- The Chaos Computer Club, for the original Project Blinkenlights and the archive at blinkenlights.net
- The IRL-CT Tinkerbelle tool, which we studied before deciding to build our own grid
- Neeha, Marisol, and the other groups who gave us feedback

---

# Part 2 — ReMastering the light

*This describes the second week's work for this lab activity.*

## Prep (before the next lab)

Find three other groups. (How? Maybe Slack?) Visit their Lab Hub pages, watch their
videos, and give them reactions and feedback: tell them what you saw happening,
guess the masterwork and the goals of the characters, and ask about anything that
wasn't clear.

**Group 1: [Timex Indiglo](https://github.com/neeharavula/Interactive-Lab-Hub/blob/Fall2026/Lab%201/README.md)** (Neeha Ravula, Marisol Park)<br>
What we liked:
- TODO
What could have been better:<br>
- TODO

**Group 2: [Light-Up Sneakers](https://github.com/ga386-hash/Interactive-Lab-Hub/blob/Fall2026/Lab%201/README.md)** (Gal Alon, Jonathan Sharpy)<br>
What we liked:
- The timing of the steps: the red light turning on and the footstep sound playing exactly when the shoe hits the ground
- The rhythm of walking felt realistic
What could have been better:<br>
- Better animate how stepping harder makes the display brighter

**Group 3: [E.T.'s Glowing Heart](https://github.com/rohilsaraf97/Interactive-Lab-Hub/blob/Fall2026/Lab%201/README.md)** (Rohil Saraf, Aryan Palave)<br>
What we liked:
- TODO
What could have been better:<br>
- TODO

## Remix, Update, or Critique the Master

Now that you understand your masterwork from the inside, respond to it. Do the
recreation again, but this time make it your own — pick one of these moves (or
combine them):

1. **Remix the modality.** Your recreation no longer has to (just) use light. Use
   vibration, sound, motion, heat — whatever best carries the interaction. Feel
   free to fork and modify the Tinkerbelle code. (Add your updates to this lab's folder!)
2. **Update it.** Redesign the piece for today's context, or for a setting its
   creators never imagined (the piece with roommates in the room, with children
   present, on a phone, in a car).
3. **Fix its weaknesses.** You identified this master's strengths and weaknesses
   in Part 0 — now address a weakness, or push a strength further.

We will grade this second pass with an emphasis on **creativity** and on how well
your response engages with what your master was really doing.

**Document everything here — especially the storyboard and video. Photos of the
prototype are great too.**

---



*Assignment lineage: this lab merges "Staging Interaction" (Interactive Lab Hub)
with "Recreating the Masters" (Interaction Design Studio, Profs. Scott Minneman &
Wendy Ju). Massive list of interactive light masterworks generated by Claude.ai.*
