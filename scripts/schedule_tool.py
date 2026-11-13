#!/usr/bin/env python3
"""Offline manifest validator and iCalendar exporter (Python 3.9+ stdlib only).

No network, API keys, calendar modifications, or household profile persistence.
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

UTC = dt.timezone.utc
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
TIME_RE = re.compile(r"(?:[01]\d|2[0-3]):[0-5]\d\Z")


class ManifestError(ValueError):
    pass


def local_datetime(day: dt.date, clock: str, zone: ZoneInfo) -> dt.datetime:
    if not isinstance(clock, str) or not TIME_RE.fullmatch(clock):
        raise ManifestError(f"Invalid clock time {clock!r}; expected HH:MM (24-hour)")
    hh, mm = map(int, clock.split(":"))
    naive = dt.datetime.combine(day, dt.time(hh, mm))
    first = naive.replace(tzinfo=zone, fold=0)
    second = naive.replace(tzinfo=zone, fold=1)
    # A wall time may not exist on a spring-forward day, or may occur twice in fall.
    back_first = first.astimezone(UTC).astimezone(zone).replace(tzinfo=None)
    back_second = second.astimezone(UTC).astimezone(zone).replace(tzinfo=None)
    if back_first != naive or back_second != naive:
        raise ManifestError(f"Nonexistent local time {day} {clock} in {zone.key}; clarify")
    if first.utcoffset() != second.utcoffset():
        raise ManifestError(f"Ambiguous local time {day} {clock} in {zone.key}; specify the offset")
    return first


def parse_date(value: object) -> dt.date:
    if not isinstance(value, str) or not DATE_RE.fullmatch(value):
        raise ManifestError(f"Invalid date {value!r}; expected YYYY-MM-DD")
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise ManifestError(f"Invalid date {value!r}") from exc


def parse_limit(limits: object, key: str, upper: float) -> float | None:
    if not isinstance(limits, dict) or key not in limits:
        return None
    value = limits[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not (0 < value <= upper):
        raise ManifestError(f"limits.{key} must be a number > 0 and <= {upper}")
    return float(value)


def split_by_local_day(start: dt.datetime, end: dt.datetime, zone: ZoneInfo):
    """Yield local-date, elapsed minutes, splitting overnight shifts at local midnight."""
    cur = start.astimezone(UTC)
    stop = end.astimezone(UTC)
    while cur < stop:
        local_date = cur.astimezone(zone).date()
        next_day = local_date + dt.timedelta(days=1)
        # Midnight can theoretically be a DST boundary in some zones. Explicit
        # local time resolution catches ambiguous/nonexistent boundaries.
        boundary = local_datetime(next_day, "00:00", zone).astimezone(UTC)
        segment_end = min(stop, boundary)
        if segment_end <= cur:
            raise ManifestError("Could not split overnight shift at local midnight")
        yield local_date, (segment_end - cur).total_seconds() / 60
        cur = segment_end


def validate(manifest: object) -> dict:
    errors = []
    warnings = []
    if not isinstance(manifest, dict):
        return {"ok": False, "errors": ["Manifest must be a JSON object"], "warnings": [], "events": []}
    if manifest.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")
    if manifest.get("status", "draft") not in {"draft", "approved"}:
        errors.append("status must be draft or approved")
    timezone = manifest.get("timezone")
    try:
        if not isinstance(timezone, str):
            raise ZoneInfoNotFoundError("Missing IANA timezone")
        zone = ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        errors.append(f"Invalid timezone: {timezone!r} ({exc})")
        zone = None
    limits = manifest.get("limits", {})
    try:
        daily_max = parse_limit(limits, "daily_hours", 24)
        weekly_max = parse_limit(limits, "weekly_hours", 168)
    except ManifestError as exc:
        errors.append(str(exc))
        daily_max = weekly_max = None
    if daily_max is None or weekly_max is None:
        warnings.append("Daily/weekly hour ceilings are not fully specified; validate local program rules before publishing")
    if manifest.get("program") == "us-standard-au-pair":
        if daily_max is None or weekly_max is None or daily_max > 10 or weekly_max > 45:
            warnings.append("U.S. standard au pair requires review of 10h/day and 45h/week ceilings")
    if manifest.get("program") == "us-educare":
        if daily_max is None or weekly_max is None or daily_max > 10 or weekly_max > 30:
            warnings.append("U.S. EduCare requires review of 10h/day and 30h/week ceilings")
    shifts = manifest.get("shifts", [])
    if not isinstance(shifts, list):
        errors.append("shifts must be an array")
        shifts = []
    no_shift_dates = set()
    for item in manifest.get("no_shift_dates", []):
        try:
            day = parse_date(item)
            if day in no_shift_dates:
                warnings.append(f"Repeated no-shift date {day}")
            no_shift_dates.add(day)
        except ManifestError as exc:
            errors.append(f"no_shift_dates: {exc}")
    events = []
    day_minutes = collections.defaultdict(float)
    week_minutes = collections.defaultdict(float)
    for idx, row in enumerate(shifts, start=1):
        try:
            if not isinstance(row, dict):
                raise ManifestError("shift must be a JSON object")
            if zone is None:
                raise ManifestError("valid timezone required to interpret shifts")
            if row.get("confidence", "high") == "unresolved":
                raise ManifestError("unresolved time cannot be exported or published")
            day = parse_date(row.get("date"))
            start = local_datetime(day, row.get("start"), zone)
            end_next_day = row.get("end_next_day", False)
            if not isinstance(end_next_day, bool):
                raise ManifestError("end_next_day must be a boolean")
            end_day = day + dt.timedelta(days=1) if end_next_day else day
            end = local_datetime(end_day, row.get("end"), zone)
            start_utc = start.astimezone(UTC)
            end_utc = end.astimezone(UTC)
            if end_utc <= start_utc:
                raise ManifestError("shift end must follow start; set end_next_day=true for overnight work")
            title = row.get("title", manifest.get("event_title", "Au Pair — Shift"))
            if not isinstance(title, str) or not title.strip():
                raise ManifestError("title must be nonblank text")
            notes = row.get("notes", "")
            if not isinstance(notes, str):
                raise ManifestError("notes must be text")
            events.append({"date": day.isoformat(), "start": start, "end": end, "start_utc": start_utc, "end_utc": end_utc, "title": title, "notes": notes})
            for local_day, minutes in split_by_local_day(start, end, zone):
                if local_day in no_shift_dates:
                    errors.append(f"Shift {idx} overlaps no-shift date {local_day}")
                day_minutes[local_day] += minutes
                monday = local_day - dt.timedelta(days=local_day.weekday())
                week_minutes[monday] += minutes
        except (ManifestError, OverflowError) as exc:
            errors.append(f"Shift {idx}: {exc}")
    events.sort(key=lambda e: e["start_utc"])
    for left, right in zip(events, events[1:]):
        if left["end_utc"] > right["start_utc"]:
            errors.append(f"Overlapping caregiver shifts: {left['start'].isoformat()} and {right['start'].isoformat()}")
    if daily_max is not None:
        for day, minutes in sorted(day_minutes.items()):
            if minutes > daily_max * 60 + 1e-7:
                errors.append(f"Daily ceiling exceeded on {day}: {minutes/60:.2f}h > {daily_max:g}h")
    if weekly_max is not None:
        for monday, minutes in sorted(week_minutes.items()):
            if minutes > weekly_max * 60 + 1e-7:
                errors.append(f"Weekly ceiling exceeded starting {monday}: {minutes/60:.2f}h > {weekly_max:g}h")
    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "events": events,
        "daily_hours": {str(d): round(m / 60, 3) for d, m in sorted(day_minutes.items())},
        "weekly_hours": {str(d): round(m / 60, 3) for d, m in sorted(week_minutes.items())},
        "total_hours": round(sum((e["end_utc"] - e["start_utc"]).total_seconds() / 3600 for e in events), 3),
    }


def ics_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;")


def fold_ics_line(line: str) -> str:
    """RFC 5545 fold with max 75 octets per physical line."""
    parts = []
    current = ""
    for ch in line:
        max_octets = 75 if not parts else 74  # continuation begins with space
        if len((current + ch).encode("utf-8")) > max_octets:
            parts.append(current)
            current = ch
        else:
            current += ch
    parts.append(current)
    return "\r\n ".join(parts)


def export_ics(manifest: dict, report: dict) -> str:
    if not report["ok"]:
        raise ManifestError("Cannot export: manifest validation failed")
    stamp = dt.datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Au Pair Family Scheduler//EN", "CALSCALE:GREGORIAN", "METHOD:PUBLISH"]
    for event in report["events"]:
        fingerprint = "\u241e".join([event["start_utc"].isoformat(), event["end_utc"].isoformat(), event["title"], event["notes"]])
        uid = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:32] + "@au-pair-family-scheduler.local"
        detail = "Exported by Au Pair Family Scheduler (not a live calendar sync)."
        if event["notes"]:
            detail += "\n" + event["notes"]
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{stamp}",
            f"DTSTART:{event['start_utc'].strftime('%Y%m%dT%H%M%SZ')}",
            f"DTEND:{event['end_utc'].strftime('%Y%m%dT%H%M%SZ')}",
            f"SUMMARY:{ics_escape(event['title'])}",
            f"DESCRIPTION:{ics_escape(detail)}",
            "STATUS:TENTATIVE" if manifest.get("status", "draft") == "draft" else "STATUS:CONFIRMED",
            "END:VEVENT",
        ])
    lines.append("END:VCALENDAR")
    return "\r\n".join(fold_ics_line(s) for s in lines) + "\r\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    v = sub.add_parser("validate", help="Check schedule manifest, hours and overlaps")
    v.add_argument("manifest", type=Path)
    i = sub.add_parser("ics", help="Validate then export a portable ICS file")
    i.add_argument("manifest", type=Path)
    i.add_argument("-o", "--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        report = validate(manifest)
        for msg in report["warnings"]:
            print("WARNING:", msg, file=sys.stderr)
        for msg in report["errors"]:
            print("ERROR:", msg, file=sys.stderr)
        print(f"Shifts: {len(report['events'])} | total: {report['total_hours']} hours")
        for day, hours in report["daily_hours"].items():
            print(f"  {day}: {hours:g} h")
        for monday, hours in report["weekly_hours"].items():
            print(f"  Week of {monday}: {hours:g} h")
        if not report["ok"]:
            return 2
        if args.command == "ics":
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(export_ics(manifest, report).encode("utf-8"))
            print(f"Wrote {args.output} (manual import; possible duplicates on reimport)")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
