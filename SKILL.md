---
name: au-pair-family-scheduler
description: Help families plan, compare, import, and publish au pair or in-home caregiver work schedules. Use when asked to draft weekly childcare coverage, turn handwritten/photo/text shift schedules into calendar events, reconcile split shifts, check working-hour limits, review family calendar conflicts, or add approved caregiver shifts to a connected calendar. Interview first-time users briefly to learn timezone, accessible calendars, caregiver/program constraints, coverage needs, and scheduling preferences. Keep drafts separate from committed calendar entries, prevent duplicates, and verify writes.
license: MIT
compatibility: Works in skill-aware agents; connected calendar reads/writes require a calendar integration with the appropriate permissions. Drafting and optional ICS export work without a calendar integration. Python 3.9+ standard library supports optional validation/ICS tooling.
metadata:
  version: "1.0.0"
  updated: "2026-11-13"
---

# Au Pair Family Scheduler

## Purpose and modes

A family-aware scheduler for an au pair or other in-home childcare caregiver. Use the least intrusive workflow that achieves the user's request:

- **Plan:** Propose one or more childcare coverage schedules, explain trade-offs and uncovered windows. Do not create calendar events.
- **Import / review:** Parse an existing schedule from text, a photo, screenshot, or grid, then validate and preview it. If the user explicitly requested calendar import, continue to the publish workflow after resolving necessary ambiguities.
- **Publish / reconcile:** Compare a specifically selected, approved schedule with a specifically selected, writable calendar, create only missing shifts, and verify the results.

Do not imply an installation, plugin connection, calendar write, or verification occurred unless the host actually supports and completed it. A `SKILL.md` file stored in a file library does not necessarily register as an installed skill.

## 1. Adaptive onboarding, not a compulsory questionnaire

On first meaningful use, gather *only missing information needed for the present mode*. When calendar discovery is available, discover accessible calendars and identify writable targets **before asking the user to type their calendar names**. Never assume the default or primary calendar is the desired shared family calendar.

Minimum inputs for any dated plan: target week/date range and IANA timezone (or reliably supplied calendar timezone). For **planning**, ask about needed childcare windows and unavailable times; for **import**, require a readable source with unambiguous dates and times; for **publishing**, require a selected writable target and a specific finalized schedule plus authorization to write.

Progressively learn these dimensions:

1. **Calendar integration:** which accessible calendars may be read for conflicts, and which single writable calendar should receive shifts; if multiple plausible targets exist, ask which. If no compatible integration exists, offer a draft and optional `.ics` export, not a claim of synchronization.
2. **Location/program:** jurisdiction and applicable au pair program or other employment arrangement; sponsor/contractual scheduling restrictions; timezone and week-start convention. Do not assume U.S. regulations apply worldwide.
3. **Coverage:** childcare demand windows, school/daycare hours, parent work coverage, commuting/pickup buffers, recurring days off, caregiver class/education and personal commitments, other coverage options.
4. **Preferences:** avoid split shifts, preferred start/end times, preferred free days, notice period, maximum scheduled hours (which may be *lower* than legal maximum), title, event privacy, reminders, and notes.

Ask short, targeted questions in natural conversation (usually one or two related questions at a time). Reuse known facts from the current conversation or legitimately available user settings; do not interview again on each use. If a preference store is available, ask before saving a reusable household profile and store only minimal necessary scheduling data. Never publish personal schedules, children's identities, addresses, credentials, account IDs, or private calendar details in the public skill repository.

See `references/onboarding-and-planning.md` for a decision-oriented first-use script and coverage-prioritization procedure.

## 2. Discover tool capabilities; degrade gracefully

Before relying on a provider, discover what the **current runtime** can actually do: list calendars, read date ranges, create/update/delete events, retrieve event IDs, use timezone, and/or export local files. A calendar integration may be absent, read-only, or restricted. Use documented host actions only; don't invent API operations or try to bypass permissions.

- **Plan-only:** works in chat, even offline.
- **Calendar read-only:** use available events for conflicts and show proposals; do not attempt writes.
- **Calendar read/write:** identify the exact calendar, check before writes, and reconcile afterward.
- **No calendar connector, file creation supported:** offer `.ics` export and manual import instructions. ICS imports cannot be assumed idempotent; warn that some calendar clients may create duplicates on repeated imports.
- **No integration or file creation:** provide a date/time table or CSV-style text the user can import manually.

## 3. Read or design a normalized schedule

Represent the planned or extracted schedule as an **immutable proposed manifest**. Use **one shift per uninterrupted work interval**. Two shifts separated by a break are two events. Include explicit no-shift days in the preview; no calendar shift events for those days unless separately requested.

Each interval must have a real calendar date, exact local start/end, timezone, a clear source (proposed, user text, image), confidence or unresolved status, and notes associated with that shift. For overnight intervals, explicitly mark end on the next date, rather than assuming it. Preserve handwritten notes literally where possible; do not turn `at school` into an invented dropoff or pickup instruction.

When importing a photographed weekly grid, first reconstruct independent date columns and approximate time-grid positions, then transcribe exact written times and their **start/end roles**. Trace arrows spanning adjacent columns to *all* covered days, including intermediate days; never reinterpret one multiday arrow as one continuous shift. Pair starts/ends independently per day and recheck illegible or inconsistent cells. Validate weekdays against full dates. Do not guess an unclear year or a boundary that materially changes an event. See `references/import-and-calendar.md`.

When planning, distinguish **hard constraints** (caregiver unavailable, legal/contractual ceilings, confirmed other commitments, required school handoffs) from **soft preferences** (fewer split shifts, longer blocks, preference for mornings). Prioritize hard constraints and essential coverage; identify uncovered intervals when infeasible instead of assigning impossible or unauthorized hours. Explain any assumptions. Hours are a ceiling, **not a target**: never back-solve an ambiguous shift to fill a 45-hour week.

Use `references/manifest-format.md` for the interoperable JSON shape and examples. Optional local checks:

```bash
python3 scripts/schedule_tool.py validate examples/example-week.json
python3 scripts/schedule_tool.py ics examples/example-week.json -o /tmp/au-pair-week.ics
```

## 4. Review hours, rights, and childcare coverage

Calculate each interval's duration, subtract nonworking breaks, sum daily and weekly hours, and account for cross-midnight work accurately. Review applicable daily and weekly limits, consecutive rest/day-off obligations, sponsor rules, and caregiver-specified unavailability. If region/program is unknown, ask rather than silently asserting a particular law. U.S. standard au pair planning references **10 hours/day and 45 hours/week**; U.S. EduCare planning references **10 hours/day and 30 hours/week**, subject to current rules and program terms. Verify regulations when current compliance is material and seek sponsor/legal clarification rather than claiming legal clearance.

Warn explicitly about a violation, insufficient rest, or uncovered essential care; do not silently adjust transcribed hours or exceed a ceiling to satisfy demand. For an imported schedule, report the source accurately, flag issues, and request clarification before treating an apparently noncompliant schedule as approved to publish.

Show a reviewable schedule with date, time windows, total hours, notes, and coverage gaps. For a requested comparison, offer up to 2–3 viable variants and the trade-offs. Seek the caregiver's agreement through the family's ordinary process; a family planner does not establish mutual consent.

## 5. Publishing is a distinct, permissioned transaction

A request to **draft**, **explore**, or **preview** is not permission to write. A clear instruction such as “add this approved schedule to my family calendar” *is* permission to create the specified nonconflicting events; don't add a redundant confirmation when all material details are settled. If the user requests publishing a newly generated *tentative* plan without identifying which variant, get their selection first.

Before writing:

1. Resolve the target calendar by stable ID, display name, timezone and writable status. Never silently substitute another calendar. Confirm the target when ambiguous. Scope reads only to calendars the user authorized for scheduling.
2. Freeze the manifest (one normalized row per shift, including source and notes), verify date range, weekday/date consistency, local times, start-before-end or explicit overnight, nonoverlap within caregiver shifts, and applicable limits. Keep execution outcomes in a separate journal.
3. Read all target-calendar events covering the **full manifest date range**, including overnight endpoints and pagination. Compare locally, by date/time, title variants, caregiver role/name if used, notes and stable source provenance. A simple event-count match is insufficient.
4. Classify each row `create`, `exact_duplicate`, `potential_update`, `conflict`, or `unresolved`. Do not create a duplicate of a known shift with old/wrong hours. Unrelated family events are read-only context, not permission to modify them; report relevant coverage conflicts without treating any overlapping event as an au pair duplicate.
5. For any change to an *existing* event (including changing times or adding notes), show the old and proposed values and obtain the user's clear authorization. Never silently overwrite, move, or delete.

For approved missing events, write time-zone-aware local start/end times, the exact chosen calendar ID, a configurable neutral title (default `Au Pair — Shift`), optional note text, and source-week provenance. Never add attendees, meeting links, or external recipients unless explicitly requested. Respect calendar-default notifications or established user preferences. Keep any private child details out of event descriptions unless the user intended those details to appear to everyone with access to that calendar.

Record event IDs and results as you write. Use bounded concurrency where supported and appropriate; avoid uncontrolled bulk writes. After a timeout or uncertain outcome, query the relevant time range before retrying. Re-run a complete paginated post-write query and verify **one and only one** matching shift per intended interval, correct time, note, title, timezone, and event provenance. Selectively inspect event detail when the listing lacks a field. Do not claim verification of fields the provider did not expose.

For user-authorized corrections, update the existing event **in place** and verify its event ID and resulting fields. Reconcile after partial failures. Never leave a known wrong event alongside a newly created 'fixed' duplicate.

See `references/import-and-calendar.md` for matching and safety details.

## 6. End with a useful, honest summary

- **Draft:** dates, daily/weekly totals, gaps, caveats, and a clear question about whether the family wishes to revise or publish.
- **Imported preview:** exact schedule, no-shift days, source notes, confidence issues, hours, and next action.
- **Published:** target calendar name; dates; created/updated/exact duplicates/conflicts/unresolved counts; whether final reconciliation passed. Show errors or skipped rows explicitly. Do not call an unverified or partially completed import successful.

If asked for a reusable profile, schedule manifest, CSV, or ICS and file tools are available, supply the artifact. Treat configuration and schedules as private user files, not files to commit to the public repository.

## Boundaries

This is a scheduling assistant, not legal or immigration advice, a payroll system, an approval from the au pair, or an authenticated calendar connector. Never invent access; never use personal information from this skill's sample fixtures as real user context; never publish example private data; never hide coverage gaps or compliance issues; never modify unrelated events; never auto-send invitations or messages.
