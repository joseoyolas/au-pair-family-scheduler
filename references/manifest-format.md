# Version 1.0 manifest format

A plan is portable JSON. Separate a household's *private* manifest from the public, sample-only skill package.

```json
{
  "schema_version": "1.0",
  "status": "draft",
  "timezone": "America/New_York",
  "role_label": "Au Pair",
  "event_title": "Au Pair — Shift",
  "program": "us-standard-au-pair",
  "limits": { "daily_hours": 10, "weekly_hours": 45 },
  "shifts": [
    { "date": "2026-11-16", "start": "07:30", "end": "12:00", "notes": "School morning", "source": "proposed", "confidence": "high" },
    { "date": "2026-11-16", "start": "13:00", "end": "17:00", "notes": "Afternoon coverage", "source": "proposed", "confidence": "high" }
  ],
  "no_shift_dates": ["2026-11-17"]
}
```

## Field meanings

- `schema_version`: must be `1.0` for the bundled optional helper.
- `status`: `draft` or `approved` (metadata only; it is **not** calendar write authorization).
- `timezone`: IANA zone, e.g. `America/New_York`; timestamps are interpreted there with daylight-saving rules.
- `program`: informative choice such as `us-standard-au-pair`, `us-educare`, or `other`; `limits` is explicitly set by the household. Program strings do not silently override explicit limits.
- `limits`: numerical hours ceilings for local calendar **days** and Monday–Sunday weeks. They are not hours targets. Other constraints (rest, days off, sponsor terms) require conversational review.
- `shifts`: one entry per uninterrupted interval. Required fields: `date`, `start`, `end`; exact clock times use `HH:MM` (24h). `end_next_day: true` explicitly indicates an overnight shift. Optional `notes`, `source`, `confidence` and `title` (per-shift override).
- `no_shift_dates`: dates explicitly marked off. The helper warns if a shift overlaps one of these dates.

The optional helper validates dates, overlapping shifts, time zones, ambiguous DST transitions, numeric limits, and creates a portable `.ics` export from fully validated shifts. It does **not** read calendars, decide how to resolve conflicts, contact the au pair, or authorize writes. Rest-period and rest-day requirements are not mechanically certified.

If a source has unresolved time/date ambiguities, preserve them in the draft preview outside this *publishable* manifest; do not invent times merely to make the helper accept the file.
