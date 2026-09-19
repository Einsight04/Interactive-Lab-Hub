"""Timing and physical-button edge cases; run with python -m unittest -v."""
import unittest
from window_clock import Clock, Buttons, render


class ClockTests(unittest.TestCase):
    def test_pause_does_not_consume_time(self):
        c = Clock(work=25, rest=5)
        c.action('a'); c.tick(10); c.action('a'); c.tick(900)
        self.assertEqual(c.elapsed, 10)
        c.action('a'); c.tick(15)
        self.assertTrue(c.done)
        self.assertFalse(c.running)
        c.tick(100)
        self.assertEqual(c.elapsed, 25)

    def test_completion_waits_for_deliberate_break(self):
        c = Clock(work=25, rest=5, running=True)
        c.tick(26); c.action('a')
        self.assertEqual(c.phase, 'work')
        self.assertFalse(c.running)
        c.action('b')
        self.assertEqual((c.phase, c.elapsed, c.running), ('break', 0, True))
        c.tick(5)
        self.assertTrue(c.done)
        c.action('b')
        self.assertEqual((c.phase, c.elapsed, c.done), ('work', 0, False))

    def test_reset_and_clock_adjustment(self):
        c = Clock(running=True)
        c.tick(-5)
        self.assertEqual(c.elapsed, 0)
        c.action('b'); c.tick(12); c.action('reset')
        self.assertEqual((c.phase, c.elapsed, c.running, c.done), ('work', 0, False, False))

    def test_invalid_duration(self):
        for n in (0, -1, float('inf'), float('nan')):
            with self.assertRaises(ValueError):
                Clock(work=n)

    def test_render_each_state(self):
        c = Clock(work=1, rest=1)
        for event in ('a', 'a', 'a', 'b', 'reset'):
            c.action(event)
            self.assertEqual(render(c).size, (240, 135))
            c.tick(1)
            self.assertEqual(render(c).mode, 'RGB')


class ButtonTests(unittest.TestCase):
    def test_bounce_produces_one_release(self):
        b = Buttons()
        events = []
        for a, t in [(True, 0), (False, .01), (True, .02), (True, .07),
                     (False, .1), (True, .11), (False, .12), (False, .18)]:
            events += b.update(a, False, t)
        self.assertEqual(events, ['a'])

    def test_chord_resets_once_and_suppresses_release(self):
        b = Buttons()
        events = []
        for a, c, t in [(True, False, 0), (True, False, .05),
                        (True, True, .1), (True, True, .16), (True, True, 1.2),
                        (True, True, 2), (False, True, 2.1), (False, True, 2.2),
                        (False, False, 2.3), (False, False, 2.4)]:
            events += b.update(a, c, t)
        self.assertEqual(events, ['reset'])

    def test_short_chord_does_nothing(self):
        b = Buttons()
        events = []
        for a, c, t in [(True, True, 0), (True, True, .05),
                        (False, False, .2), (False, False, .3)]:
            events += b.update(a, c, t)
        self.assertEqual(events, [])


if __name__ == '__main__':
    unittest.main()
