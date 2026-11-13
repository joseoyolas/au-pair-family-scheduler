# First-use onboarding and planning

## Progressive first-use questions

Before asking, inspect the conversation and available calendar-discovery tools. If a scheduling date range is already provided, do not ask for it again. Discover accessible calendar *names and write capability*, without displaying event contents unless the user authorized reads.

1. For a new **planning** request: “Which week should we plan, and what childcare coverage do you need each day?” If dates/timezone are known, ask only for missing coverage windows.
2. For a new **import** request: inspect the supplied schedule before asking anything. Ask about unreadable dates or times only when essential; no coverage survey is required.
3. Before **calendar publishing**: “I can access [calendar names]. Which writable calendar should receive au pair shifts?” Ask only if a target is missing or ambiguous. If one target was expressly selected earlier, reuse it after validating current permissions.
4. Ask which **jurisdiction/program** applies (U.S. standard au pair, U.S. EduCare, other au pair scheme, nanny/other caregiver) and whether the sponsor/contract has tighter restrictions. For importing historical times, do not block parsing on a missing jurisdiction, but avoid compliance conclusions.
5. Ask for relevant **fixed constraints** (au pair class/study, unavailable days, parental commitments, daycare/school hours, pickups requiring travel buffers, alternate care). Ask for **soft preferences** (avoid split shifts, start time preference, preferred day off) only when a planning choice depends on them.
6. Offer configurable event title and reminders after a usable schedule exists, rather than upfront if the user only asked for a draft.

Do not collect child birth dates, contact details, school names, addresses, medical information, or immigration identifiers unless the actual user task requires them. Use generalized labels such as “school pickup” for calendar notes by default. Don't assert consent from anyone whose schedule is being drafted.

## Calendar availability and conflicts

- Categorize discovered calendars: writable destination, permitted read-only context, inaccessible, missing connector.
- Seek permission to examine events on other adult calendars rather than reading every accessible calendar by default.
- Busy blocks from a calendar are **constraints to discuss**, not automatically caregiver unavailability. Parent meetings may increase demand for childcare; au pair classes may prohibit a shift; these are different semantics.
- The family can plan offline, and the skill may provide `.ics` export if supported, even when calendar access is unavailable.

## Scheduling procedure

1. Build a table of required childcare windows each day; exclude coverage already provided by school/daycare and other confirmed providers. Account for handoff and transit buffers explicitly where the user specified them.
2. Place the caregiver's **unavailable** windows, rest days, existing shifts, and maximum allowable time as hard constraints.
3. Place high-priority coverage segments into valid work intervals. Avoid implied unbroken paid coverage during a break. Split shifts count as separate intervals and their break is excluded from worked hours.
4. Optimize soft preferences only after safety and coverage constraints: fewer split shifts, consistent hours, preferred start/end, fewer last-minute changes, equitable weekend distribution if requested.
5. Calculate day/week hours and rest windows. If essential coverage exceeds available hours, surface the uncovered times and propose alternative childcare or parent coverage. Do not invent an infeasible schedule.
6. For competing options, explain their trade-offs in plain language (e.g., “A covers all morning school runs but uses a split shift Thursday; B avoids split shifts but leaves 45 minutes Friday uncovered”).

## Reuse of household preferences

If a host has a persistence feature and the user opts in, a compact profile may contain: timezone, week start, program/jurisdiction, maximum scheduled hours, preferred shift title, default target calendar display name (not an immutable ID), permitted conflict calendars, school-day time windows expressed without school names, unavailable windows, and preferred handoff buffers. Recheck calendar IDs/permissions each session. Never store OAuth tokens, passwords, or direct identifiers in a skill profile.
