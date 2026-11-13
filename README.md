# Au Pair Family Scheduler 📅

An open [Agent Skill](https://agentskills.io/) for drafting realistic au pair or other in-home childcare work schedules, reading photographed/text schedules, and safely publishing *approved* shifts to connected family calendars.

It does **not** connect to calendar accounts by itself. It instructs a compatible AI agent how to discover, use, and verify the calendar tools that are actually available in that agent's environment. Without an integration, it can still draft schedules and generate an optional `.ics` file locally.

## What it does

- **First-use setup:** short, adaptive questions about timezone, caregiver/program rules, coverage windows, preferences, and discovered writable calendars. Does not force a full interview every time.
- **Plan:** suggest one or more viable coverage options, note gaps, check hour limits and rest-day constraints, and keep draft options off the actual calendar.
- **Import:** read typed shifts or photographed handwritten weekly grids, including multi-column arrows, split shifts, and handoff notes. Never invent an ambiguous time.
- **Publish:** after clear authorization, use existing calendar integration to check for duplicates/conflicts, create missing intervals, and re-read the calendar to verify.
- **Fallback:** with Python 3.9+, validate a schedule manifest and export an ICS file for manual calendar import.

## Installation

With a compatible agent that supports [Vercel's `skills` CLI](https://www.skills.sh/docs), after publishing this folder at a public GitHub repo root:

```bash
npx skills add YOUR-GITHUB-USERNAME/au-pair-family-scheduler
```

You can also copy the `au-pair-family-scheduler` folder into a compatible agent's skills directory or use its documented custom-skill upload flow. Installation/auto-trigger behavior is platform-dependent; a GitHub link or a ChatGPT file-library upload is not in itself an installation.

## Example prompts

- "Help me create two au pair coverage options next week. We need care 7:30–9:00 and 3:00–6:00 on school days."
- "Here's a photo of our au pair's handwritten week. Read the shifts and show me the total hours."
- "Add option B to our shared family calendar, skipping shifts that already exist."
- "Compare the revised schedule with what's on our calendar and highlight conflicts before changing anything."

## Optional offline tools

Requires only Python 3.9+ (standard library):

```bash
python3 scripts/schedule_tool.py validate examples/example-week.json
python3 scripts/schedule_tool.py ics examples/example-week.json -o example-week.ics
python3 -m unittest discover -s tests -v
```

The validated `.ics` file is an **export**, not a live sync. Reimporting it may create duplicates in some calendar apps. An `approved` manifest is not permission for an agent to write to a connected calendar; the user must authorize the specific operation.

## Structure

```text
au-pair-family-scheduler/
├── SKILL.md                      # Agent entry point
├── README.md
├── LICENSE                       # MIT
├── references/
│   ├── onboarding-and-planning.md
│   ├── import-and-calendar.md
│   └── manifest-format.md
├── examples/
│   ├── example-week.json
│   └── example-import-regression.md
├── scripts/
│   └── schedule_tool.py
└── tests/
    └── test_schedule_tool.py
```

## Privacy and limitations

This repository includes **synthetic examples only**. Do not commit real household schedules, child names, addresses, school information, private calendar IDs, credentials, or OAuth tokens. Calendar connectors and their permissions remain controlled by the host agent/user. Validate applicable legal/program rules directly, including sponsor obligations, days off and local labor law; the skill is a planning tool, not legal/immigration advice. Always consult the caregiver about a proposed schedule.

## References

- [Agent Skills open specification](https://agentskills.io/specification)
- [skills.sh documentation](https://www.skills.sh/docs)
- [U.S. State Department: au pair rights and protections](https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/wilberforce-english.html)

## Status

v1.0.0. Offline manifest validation and ICS export have automated tests. Live calendar write workflows are **host-dependent and not yet end-to-end integration tested** across providers. Contributions with privacy-safe synthetic fixtures and provider-specific compatibility notes are welcome.
