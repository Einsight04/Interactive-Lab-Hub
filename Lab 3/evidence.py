"""Collect real observations and make a local report worksheet from saved evidence."""
import argparse
from datetime import datetime
import json
from pathlib import Path
from exercises import RESULTS

QUESTIONS = {
    'experiments': [
        ('voices', 'How did the three voices feel different? Which did you prefer, and why?'),
        ('accuracy_delay', 'What did each recognition model get wrong? Was base.en worth the delay?'),
        ('number', 'Was your numerical answer transcribed correctly? Describe any error.'),
        ('silence_02', 'At 0.2 seconds, what was cut off or split?'),
        ('silence_08', 'How did 0.8 seconds feel?'),
        ('silence_15', 'At 1.5 seconds, how did waiting feel?'),
        ('echo', 'How did the complete echo loop feel?')],
    'feedback': [
        ('session', 'Session folder name from the controller:'),
        ('stage', 'Initial or revised prototype?'),
        ('participant', 'Participant name or alias:'),
        ('video', 'Phone video filename and controller recording filename:'),
        ('task', 'What real task did the participant choose?'),
        ('surprise', 'What happened differently than the planned dialogue?'),
        ('feedback', 'What did they actually say was confusing or should change?'),
        ('system', 'What worked and what failed in the device interaction?'),
        ('controller', 'What worked and what failed while operating the controller?'),
        ('autonomy', 'What should an autonomous version learn from this session?')],
}


def save(kind, payload):
    RESULTS.mkdir(exist_ok=True)
    path = RESULTS / (kind + '-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.json')
    path.write_text(json.dumps(payload, indent=2) + '\n')
    return path


def collect(kind):
    answers = {}
    print('Enter actual observations. Press Enter to leave unknown items pending.')
    for key, question in QUESTIONS[kind]:
        answers[key] = input(question + '\n> ').strip()
        # Save after every answer so interruptions do not lose earlier notes.
        if len(answers) == 1:
            path = save(kind, answers)
        else:
            path.write_text(json.dumps(answers, indent=2) + '\n')
    print('Saved:', path)


def revise():
    from wizard import PROMPTS
    config = RESULTS / 'prompts.json'
    before = dict(PROMPTS)
    if config.exists():
        before.update(json.loads(config.read_text()))
    for key, value in before.items():
        print(f'{key}: {value}')
    print('Choose a wording change based on the initial interaction.')
    key = input('Reply number to revise (1-8), or Enter to cancel: ').strip()
    if not key:
        return
    if key not in PROMPTS:
        raise ValueError('Choose an existing reply number, 1 through 8.')
    finding = input('What actually happened that motivates this change? ').strip()
    replacement = input('New words the device should say: ').strip()
    if not finding or not replacement:
        raise ValueError('Both the observation and new wording are required.')
    after = {**before, key: replacement}
    path = save('revision', dict(observation=finding, reply=key, before=before[key], after=replacement))
    config.write_text(json.dumps(after, indent=2) + '\n')
    print('Saved:', path)
    print('The next controller session will use the updated wording.')


def worksheet():
    RESULTS.mkdir(exist_ok=True)
    out = ['# Lab 3 collected evidence', '', 'Actual saved measurements and notes. Blank answers remain pending.', '']
    for pattern in ('compare-*.json', 'number-*.json', 'experiments-*.json', 'revision-*.json', 'feedback-*.json'):
        paths = sorted(RESULTS.glob(pattern))
        if not paths:
            out.extend(['## ' + pattern.split('-')[0].title(), '', 'Pending.', ''])
        for path in paths:
            out.extend(['## ' + path.stem, '', '```json', path.read_text().strip(), '```', ''])
    sessions = sorted(RESULTS.glob('session-*/events.jsonl'))
    out.extend(['## Controller sessions', ''])
    for path in sessions:
        out.append('- ' + str(path.relative_to(RESULTS)))
    if not sessions:
        out.append('Pending.')
    out.extend(['', 'The final report still needs interpretation, selected videos, and a revised dialogue based on these findings.'])
    path = RESULTS / 'report-evidence.md'
    path.write_text('\n'.join(out) + '\n')
    print('Saved:', path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['experiments', 'feedback', 'revise', 'worksheet'])
    args = parser.parse_args()
    if args.action in QUESTIONS:
        collect(args.action)
    elif args.action == 'revise':
        revise()
    else:
        worksheet()


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print('\nStopped. Completed answers remain saved.')
