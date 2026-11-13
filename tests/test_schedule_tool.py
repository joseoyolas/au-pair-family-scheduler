"""Run with python3 -m unittest discover -s tests -v."""

import copy
import datetime as dt
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("schedule_tool", HERE / "scripts" / "schedule_tool.py")
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class ScheduleToolTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((HERE / "examples" / "example-week.json").read_text(encoding="utf-8"))

    def test_example_week_valid_with_split_shifts(self):
        report = tool.validate(self.manifest)
        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(len(report["events"]), 6)
        self.assertEqual(report["daily_hours"]["2026-11-16"], 9)
        self.assertEqual(report["weekly_hours"]["2026-11-16"], 44)
        self.assertEqual(report["total_hours"], 44)

    def test_overlapping_shifts_rejected(self):
        m = copy.deepcopy(self.manifest)
        m["shifts"].append({"date": "2026-11-16", "start": "11:00", "end": "14:00"})
        report = tool.validate(m)
        self.assertFalse(report["ok"])
        self.assertTrue(any("Overlapping" in x for x in report["errors"]))

    def test_daily_limit_rejected(self):
        m = copy.deepcopy(self.manifest)
        m["shifts"][2]["end"] = "19:00"
        report = tool.validate(m)
        self.assertFalse(report["ok"])
        self.assertTrue(any("Daily ceiling" in x for x in report["errors"]))

    def test_overnight_split_into_two_days(self):
        m = {"schema_version": "1.0", "timezone": "America/New_York", "limits": {"daily_hours": 10, "weekly_hours": 45},
             "shifts": [{"date": "2026-11-16", "start": "22:00", "end": "02:00", "end_next_day": True}]}
        r = tool.validate(m)
        self.assertTrue(r["ok"], r["errors"])
        self.assertEqual(r["daily_hours"]["2026-11-16"], 2)
        self.assertEqual(r["daily_hours"]["2026-11-17"], 2)

    def test_overnight_week_boundary(self):
        m = {"schema_version": "1.0", "timezone": "America/New_York", "limits": {"daily_hours": 10, "weekly_hours": 45},
             "shifts": [{"date": "2026-11-15", "start": "23:00", "end": "02:00", "end_next_day": True}]}
        r = tool.validate(m)
        self.assertTrue(r["ok"], r["errors"])
        self.assertEqual(r["weekly_hours"]["2026-11-09"], 1)
        self.assertEqual(r["weekly_hours"]["2026-11-16"], 2)

    def test_dst_gap_is_rejected(self):
        m = {"schema_version": "1.0", "timezone": "America/New_York", "shifts": [
             {"date": "2026-03-08", "start": "02:30", "end": "04:00"}]}
        r = tool.validate(m)
        self.assertFalse(r["ok"])
        self.assertTrue(any("Nonexistent" in x for x in r["errors"]))

    def test_dst_fall_ambiguity_rejected(self):
        m = {"schema_version": "1.0", "timezone": "America/New_York", "shifts": [
             {"date": "2026-11-01", "start": "01:30", "end": "04:00"}]}
        r = tool.validate(m)
        self.assertFalse(r["ok"])
        self.assertTrue(any("Ambiguous" in x for x in r["errors"]))

    def test_duplicate_no_shift_overlap_rejected(self):
        m = copy.deepcopy(self.manifest)
        m["no_shift_dates"] = ["2026-11-16"]
        r = tool.validate(m)
        self.assertFalse(r["ok"])
        self.assertTrue(any("no-shift" in x for x in r["errors"]))

    def test_ics_events_tentative_utc_and_folded(self):
        m = copy.deepcopy(self.manifest)
        m["shifts"][0]["notes"] = "Morning coverage with long text " * 10
        r = tool.validate(m)
        self.assertTrue(r["ok"], r["errors"])
        ics = tool.export_ics(m, r)
        self.assertEqual(ics.count("BEGIN:VEVENT"), 6)
        self.assertIn("DTSTART:20261116T123000Z", ics)
        self.assertIn("STATUS:TENTATIVE", ics)
        for line in ics.split("\r\n"):
            self.assertLessEqual(len(line.encode("utf-8")), 75)

    def test_ics_stable_uids_on_repeat_exports(self):
        r = tool.validate(self.manifest)
        a = tool.export_ics(self.manifest, r)
        b = tool.export_ics(self.manifest, r)
        ids = lambda s: sorted(x for x in s.split("\r\n") if x.startswith("UID:"))
        self.assertEqual(ids(a), ids(b))


if __name__ == "__main__":
    unittest.main()
