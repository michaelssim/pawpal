# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

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

## Testing PawPal+

### Run the tests

```bash
python3 -m pytest test_pawpal.py -v
```

### What the tests cover

| Area | Tests |
|---|---|
| **Task lifecycle** | `completed` starts `False`; `mark_complete()` and `reset()` toggle it correctly; `frequency` and `due_date` stored accurately |
| **Sorting correctness** | `_sort_tasks()` returns tasks ordered high → medium → low, shortest-first within the same priority level |
| **Recurrence logic** | Completing a `daily` task re-queues a fresh instance due tomorrow; `weekly` due in 7 days; `as-needed` tasks are not re-queued |
| **Pet management** | `add_task()`, `remove_task()`, `get_tasks()`, and `get_pending_tasks()` (excludes completed tasks) |
| **Multi-pet scheduling** | `Owner` aggregates tasks across all pets; `Scheduler` generates a plan from the combined pending task list |
| **Time budget enforcement** | Total scheduled duration never exceeds `available_minutes`; tasks that don't fit are placed in `skipped_tasks` |
| **Conflict detection** | `detect_conflicts()` flags overlapping time windows within and across pets; adjacent tasks are not flagged; tasks without a `start_time` are ignored |
| **Edge cases** | Empty task list, invalid priority value, completed tasks excluded from scheduling, `mark_task_complete` returns `False` when title not found |

### Confidence level

Confidence level: 4/5

Core scheduling, sorting, recurrence, and conflict detection are all tested end-to-end with 38 passing tests. The confidence gap is in boundary conditions not yet covered — zero available time, an owner with no pets, and duplicate task titles across pets.

---

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
