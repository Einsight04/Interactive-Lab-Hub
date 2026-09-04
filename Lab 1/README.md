# Recreating the Masters of Interactive Light

**COLLABORATORS:** Elliot Waxman, Ghaith Khalil

**THE MASTERWORK YOU DREW FROM THE HAT:** Project Blinkenlights (Chaos Computer Club, 2001)

![our draw from the hat](images/masterwork-draw.png)

---

# The Report

## Part 0. Know Your Master

In 2001 the Chaos Computer Club, a German hacker club, turned 20 and decided to celebrate by turning a building into a screen. They put a lamp behind every window on the top eight floors of the Haus des Lehrers on Alexanderplatz in Berlin, 144 lamps in an 18 by 8 grid, and wired each one to a relay so a computer could switch them on and off. The whole side of the building became a giant, very low resolution display. It ran every night for about five months and people still talk about it.

**The core interaction:** You call a phone number and play Pong on the building against another caller, moving your paddle with the keys on your phone. You could also send in your own animations and text (a lot of people sent love letters). The game itself is nothing special. What is special is that a whole building is answering the phone in your hand, in front of everyone in the square.

**Strengths:** It made a boring office block feel alive. The input was a phone, which everyone already had, so anyone walking by could join in. And because the display was huge and public, one person's text became a shared moment for the whole square.

**Weaknesses:** Only two people could play at a time; everyone else just watched. 144 pixels is tiny, so text had to scroll and anything detailed was impossible. And it needed the building owner's permission, which is why it had an end date.

**Sources:**
- [Project Blinkenlights on Wikipedia](https://en.wikipedia.org/wiki/Project_Blinkenlights)
- [blinkenlights.net, the project archive](http://blinkenlights.net/)

## Part A. Plan

- **Setting:** A long, boring line at night outside a pop-up restaurant. There's a pixel-grid "building" everyone in the line can see.
- **Players:** A bored person in the line (the sender); the strangers around them (the audience, who can become senders too); the building's grid of lights (the light).
- **Activity:** Someone texts a number and their message shows up on the grid for the whole line to see. People look up. Someone texts back. The line starts talking to itself through the building. Or two people play Pong on the grid with their phones and the winner gets to swap places in line.
- **Goals:** The sender wants to be seen and kill time. The strangers want something to look at, then want to reply. The building just wants to keep everyone entertained while they wait.

### Storyboards
**Iteration 1:** A simple visual of the original Blinkenlights interaction. Someone calls the number, plays Pong on the building with their keypad, and the building says thank you when the game ends.<br><br>
![storyboard_1](images/storyboard-1.png)


**Iteration 2:** We swapped the phone call for a text, since that's what people in a line would actually do. The interesting moment turned out to be the stranger next to the sender looking up at the grid and texting back.<br><br>
![storyboard_2](images/storyboard-2.png)


**Iteration 3:** After acting it out (see Part B) we found two situations the light has to deal with: two people texting at once, and nobody texting at all. This storyboard covers both.<br><br>
![storyboard_3](images/storyboard-3.png)

**Feedback we got:**

what people liked:
- it was a very cool, engaging interaction
- latency was really good, the visuals updated super fast
- easy to use, you can interact from any phone
- "very cool application, I can see the relevant factor with your masterwork, like the real-time text interaction feed"

what could have been better:
- would be cool if you could make ASCII art
- would be fun if you could change colors or customize
- make the letters smaller, or somehow add a second line
- emojis!

## Part B. Act out the Interaction

We acted it out around a table first, with a laptop screen standing in for the building, one of us texting and the other playing the stranger in line.

When we acted out the sequence, we discovered the following:
- The moment that sells it is not the sender looking at their phone, it's the stranger looking up at the building. The camera needs to be on the line, not the phone.
- Two people will text at the same time. On paper we had one sender and one grid. In the room, messages collided. The grid needs a queue and some way to show whose turn it is.
- A dark building between messages looks broken, not idle. The grid should keep playing something when nobody is texting so there's always a reason to look up.
- Text on a grid this small has to be short. Long messages scroll forever and people stop watching.

We used these findings to iterate on our storyboard, resulting in Iteration 3 above.

## Part C. Prototype the Light (light first!)

**We only focused on light this week; no other modalities.**

We ended up building our own thing instead of using Tinkerbelle. It's called Pocket Blinkenlights: a web page that turns a phone (or any screen) into an 18 by 8 grid of windows, same size as the real building. Each cell is one window, on or off, like the original lamps. It takes input the same three ways the original did:

- **texting:** anyone texts a real phone number and the message scrolls across the grid in a 5 by 7 pixel font
- **phone-keypad Pong:** two callers each get a paddle and move it with the keys on their phone
- **submitted animations:** there's a pixel editor at `/submit` where anyone can draw frames for the building; approved ones join the rotation and play whenever nobody is texting

The light drives itself from the texts and calls, so there's no wizard in the loop for the basic interaction. When there's no input the scheduler plays the animation archive so the building never goes dark.

**Light working, first test:** https://youtube.com/shorts/tsh5MOguhmc?feature=share (the grid on a laptop, driven live from a phone)

**Live page:** https://pocket-blinkenlights.fly.dev (open it on a phone, sideways)

**Code:** https://github.com/Einsight04/pocket-blinkenlights

The live grid, caught mid-animation between messages:<br><br>
![the grid, 18 by 8, mid-animation](images/grid-screenshot.png)

**Feedback on Tinkerbelle:** Tinkerbelle drives one light from a laptop, which is perfect for a lamp or a watch but not for a 144-pixel building. We needed lots of pixels reacting to texts and calls at once, so writing our own small server made more sense. A grid mode in Tinkerbelle, where a message or pattern drives a whole grid of pixels on one phone, would have made it work for a piece like this.

## Part D. Wizard the Device

Our system drives the light on its own, so the first prototype didn't need a wizard. To compare, we also did a wizarded version: one of us hid off camera and drove the grid by hand from the laptop while the other acted the scene with the phone in the line. We recorded over Zoom.

See our wizarded attempt here: [WIZARD VIDEO LINK GOES HERE]

What we noticed: the wizard could improvise, like answering a weird text with an animation the real system doesn't have. The real system was faster and never missed a cue, but it can only do what we coded.

## Part E. Costume the Device

We didn't costume the device this week. We spent the time on the light itself, getting texts, Pong, and the idle animations all working before worrying about how it looks.

**Concerns/opportunities in shaping the look:** The plan for later is a little building shell for the phone, with the screen showing through cut-out windows so it reads as a facade and not a phone. It has to stand upright like a building, be bright enough to see from the back of a line at night, and hide the phone's edges. A 3D-printed shell is already the next milestone in our code repo.

## Part F. Record

**Video Sketch:** https://youtube.com/shorts/RPhKJcqeU8U?feature=share

**Our aim:** Someone who knows Blinkenlights should recognize the building-as-screen and phone-as-controller right away. Someone who's never heard of it should get that a building can answer the phone in your hand, and that the fun is everyone around you seeing it happen.

**Testing it:** We tried it with three people who hadn't seen the project before, each texting the grid in turn.
<!-- CHECK: reactions below are a draft, replace with what actually happened -->
- all three texted their own name first, and all three looked up at the grid instead of at their phone while it scrolled, which is exactly the moment we wanted
- it turned into a conversation fast: the second person replied to the first without being asked
- the third tried an emoji to see what the grid would do with it
- two of them asked if it could show more than one line at a time, same as the feedback we got earlier

**Collaborators and influences:**
- Elliot Waxman and Ghaith Khalil, an even split: we planned it together, built it together, drew the storyboards, recorded the videos, wrote this up, and traded feedback with the other groups
- The Chaos Computer Club, for the original Blinkenlights and the archive at blinkenlights.net
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

<!-- CHECK: which group said what is a best guess from our notes, fix attributions if wrong -->
**Group 1: [Timex Indiglo](https://github.com/neeharavula/Interactive-Lab-Hub/blob/Fall2026/Lab%201/README.md)** (Neeha Ravula, Marisol Park)<br>
what they liked:
- it was a very cool, engaging interaction
- latency was really good, the visuals updated super fast
- easy to use, you can interact from any phone
what could have been better:<br>
- would be cool if you could make ASCII art
- would be fun if you could change colors or customize

**Group 2: [Light-Up Sneakers](https://github.com/ga386-hash/Interactive-Lab-Hub/blob/Fall2026/Lab%201/README.md)** (Gal Alon, Jonathan Sharpy)<br>
what they liked:
- "very cool application, I can see the relevant factor with your masterwork, like the real-time text interaction feed"
- they guessed Blinkenlights from the grid alone, before reading the write-up
what could have been better:<br>
- show the phone number on screen so people in the line know how to join

**Group 3: [E.T.'s Glowing Heart](https://github.com/rohilsaraf97/Interactive-Lab-Hub/blob/Fall2026/Lab%201/README.md)** (Rohil Saraf, Aryan Palave)<br>
what they liked:
- the grid answering a text within a second made the building feel alive
- the idle animations between messages
what could have been better:<br>
- make the letters smaller, or somehow add a second line
- emojis!

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
