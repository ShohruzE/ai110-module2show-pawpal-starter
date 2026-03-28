# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## Smarter Scheduling

The project includes several small but impactful scheduler improvements that make plans more useful and robust:

- **Priority-first greedy scheduling:** tasks are ordered by `priority` (high → low) then `due_time`, and packed from a configurable day start. Overlaps are resolved by shifting lower-priority tasks later so urgent items stay scheduled.
- **Desired-time conflict detection:** the system warns when multiple tasks share the exact same requested `due_time` (so you can fix accidental collisions before the scheduler shifts tasks).
- **Slot-overlap detection and non-fatal warnings:** after building a schedule the `Schedule` object can detect overlapping slots and return human-friendly warnings (includes task title and pet name when available).
- **Recurring-task auto-creation:** marking a `daily` or `weekly` task complete automatically creates the next occurrence (preserves time-of-day) and attaches it to the same pet.
- **Sorting & filtering helpers:** `Task.sort_by_time()` and `User.filter_tasks(completed=..., pet_name=...)` make it easy to inspect and manipulate task lists for UI/debugging.
- **Simpler, clearer generator logic:** the scheduler refactor precomputes durations and preferred starts and uses a single `last_end` pointer — this improves readability and slightly reduces overhead.

All warnings are non-fatal and printed or returned so the UI can surface them without crashing. See `main.py` for a small demo that adds conflicting tasks and prints desired-time and slot warnings.

## Testing PawPal+

To run the test suite execute:

```bash
python -m pytest
```

What the tests cover:
- Sorting correctness: verifies `Task.sort_by_time()` returns tasks in chronological order (tasks without a due time sort last).
- Recurrence logic: confirms marking a `daily` recurring task complete creates a new task scheduled for the following day and attaches it to the same `Pet`.
- Conflict detection: ensures `Schedule.detect_desired_time_conflicts()` flags duplicate desired start times and `Schedule.detect_conflicts()` reports overlapping schedule slots.

Confidence Level: ★★★★☆ (4/5)

Reasoning: tests for the critical scheduling behaviors pass locally (sorting, recurrence advancement, desired-time and slot conflict detection). Edge cases like DST handling, leap-day yearly recurrences, and complex monthly rules are not yet exhaustively covered, so the system is mostly reliable for common workflows but may need more tests for rare calendar edge cases.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
