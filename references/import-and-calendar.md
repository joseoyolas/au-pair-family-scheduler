# Schedule import, matching, and publication guide

## Grid-based handwritten sources

1. Rotate/crop as needed. Identify day columns, full date range, and time-grid ticks independently.
2. Trace each arrow or line across the day columns and record endpoints. Apply the same time boundary to *every* covered day, including middle columns.
3. Separately transcribe written exact time and the annotation's meaning (`start`, `off`, `end`, `break`). A visually nearby end is not automatically a start.
4. Align written minute precision with approximate grid geometry. If the two materially conflict, re-inspect or ask; never let a weekly total dictate a missing boundary.
5. For each date independently, sort starts/ends and form one event for each continuous pair. Do not merge split shifts. Don't connect across midnight without explicit source evidence.
6. Preserve activities or instructions verbatim; assign note scope (`near start`, `near end`, `shift`, `day`). Keep labels conservative: `Schedule note near shift end: school.` rather than `Pick up child at school` if that action was not specified.
7. Resolve year by explicit text, surrounding context, and weekday/date agreement. If multiple years remain credible, ask before calendar write.
8. Mark confidence qualitatively: high (cross-checked), medium (one weak element but unique interpretation), unresolved (multiple materially different readings). Unresolved intervals must not be written.

## Stable normalized manifest

See `manifest-format.md`. This should not be silently edited after approval. Write actions belong in a separate execution journal so a retry can always distinguish source content from observed writes.

## Reconciliation matching

- Query full date range, with exclusive end covering the last day and any overnight shift, following all pagination.
- Use calendar/provider event IDs for known event updates; when first importing older schedules without IDs, match role/title variants and normalized local times plus provenance/notes.
- Classify exact match: same day, start/end, logical caregiver, title (allow known legacy variants), matching material notes. A missing provenance description can be a **potential update**, not an unrelated event or automatic duplicate.
- A known au pair event on the same date with different or overlapping hours is a **conflict / candidate update**. Show both, ask for an update instruction, and do not create a second event covering the same incorrectly imported shift.
- Events unrelated to au pair work may overlap and can be relevant to childcare needs, but must never be deleted/updated by this workflow.
- If a user authorizes a correction, read the exact existing event, update it in place, verify result, then re-query the entire relevant week.

## Permission semantics

- “Draft some options” → planning only.
- “Preview this schedule” → import/validation only.
- “Add these shifts to [calendar]” → permission to create missing shifts in the specified target, subject to resolving ambiguous times/targets and conflicts.
- “Replace last week's shifts” without specifying which existing items → show diff and obtain explicit scope/approval for updates or removals.
- “Put option B on my calendar” when option B was clearly presented as a candidate → selected-option authorization, provided destination is known and writing is supported.

## Provider behavior

Use current host-provided calendar APIs; this package intentionally contains no OAuth code or hidden credentials. When provider supports transaction IDs or private extended properties, a source-specific stable external ID can help re-identification, but always run the date-bounded duplicate check. On transient failures retry safely and only after inspecting uncertain outcomes. A raw `.ics` file is an *export*, not a live synchronized calendar; repeated user imports can result in duplicates depending on the application.

For Google Calendar, calendar display names are not unique; resolve one writable calendar and use its actual ID throughout the operation. For Microsoft Outlook, Apple Calendar, or other systems, use only the integration that the current runtime actually exposes. If none, provide an ICS/manual-import path without claiming direct integration.
