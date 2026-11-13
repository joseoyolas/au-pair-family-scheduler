# Synthetic regression for handwritten shift grids

Imagine a Monday-to-Friday arrow labeled `Start at 07:30`, spanning five day columns, while separate daily end arrows terminate Monday at 17:00, Tuesday 16:00, Wednesday 15:00, Thursday 12:15, and Friday 17:00. Thursday also has `Start at 13:00` and `off at 17:15` annotations.

Checks:
- All Monday–Friday dates inherit the 07:30 start boundary, including Thursday.
- Thursday yields *two* shifts: 07:30–12:15 and 13:00–17:15. The 12:15 is an end, not a new start.
- A weekly total must not be used to infer missing or ambiguous times.
- If a wrong Thursday event already exists, classify as conflict and update the same event only after user authorization; don't add a second overlapping event.
- Day-off columns with no valid start/end should produce no event.
