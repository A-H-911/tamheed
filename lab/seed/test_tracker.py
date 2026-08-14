"""Seed tests for tick (SEED CODE, deliberately imperfect: see lab/README.md)."""
import unittest
from datetime import date, datetime

import tracker


class OverdueTest(unittest.TestCase):
    def test_past_due_is_overdue(self):
        task = {"due": "2020-01-01", "done": None}
        self.assertTrue(tracker.overdue(task, today=date(2026, 1, 1)))

    def test_no_due_date_never_overdue(self):
        self.assertFalse(tracker.overdue({"due": None, "done": None}))

    def test_due_today_is_not_overdue(self):
        # This test is CORRECT and fails against the seeded off-by-one bug.
        task = {"due": "2026-06-01", "done": None}
        self.assertFalse(tracker.overdue(task, today=date(2026, 6, 1)))


class FlakyClockTest(unittest.TestCase):
    def test_added_timestamp_is_now(self):
        # SEEDED FLAKY TEST (lab): compares wall-clock seconds — fails whenever the
        # two now() calls straddle a second boundary. A defect, per the Google
        # flaky-test doctrine: quarantine + DEF- row, never delete, never ignore.
        before = datetime.now().isoformat(timespec="seconds")
        task = {"added": datetime.now().isoformat(timespec="seconds")}
        self.assertEqual(task["added"], before)


if __name__ == "__main__":
    unittest.main()
