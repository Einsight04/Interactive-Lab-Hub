"""Local keyboard controller: the designer listens and speaks through the Pi."""
from pathlib import Path
from datetime import datetime
import json
from exercises import say, RESULTS

PROMPTS = {
    "1": "What is one thing you want to get started on?",
    "2": "How many minutes do you have?",
    "3": "What is the smallest first step you could take?",
    "4": "Sorry, I missed that. Could you say it once more?",
    "5": "Would you like a smaller step, or a different task?",
    "6": "Ready when you are. You can begin, or tell me what to change.",
    "7": "Okay. We can stop here.",
}


def main():
    RESULTS.mkdir(exist_ok=True)
    log = RESULTS / ("wizard-" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".jsonl")
    print("One Thing controller. Run the phone video separately with permission.")
    print("Listen to the participant. Leave at least 0.8 seconds after their speech.")
    print("This log captures device replies, not participant speech.")
    while True:
        for key, text in PROMPTS.items():
            print(f"{key}: {text}")
        answer = input("Number, custom spoken reply, or /quit: ").strip()
        if answer == "/quit":
            break
        if not answer:
            continue
        text = PROMPTS.get(answer, answer)
        print("Speaking:", text)
        say(text)
        with log.open("a") as f:
            f.write(json.dumps({"time": datetime.now().isoformat(), "spoken_reply": text}) + "\n")
        print("Listening. Wait for the participant's full response.")
    print("Reply log saved:", log)


if __name__ == "__main__":
    main()
