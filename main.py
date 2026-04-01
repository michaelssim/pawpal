from pawpal_system import Task, Pet, Owner, Scheduler

def mins_to_time(m):
    """Convert minutes-from-midnight to a HH:MM string."""
    return f"{m // 60:02}:{m % 60:02}"

# --- Conflict detection demo ---
print("=" * 40)
print("  CONFLICT DETECTION")
print("=" * 40)

conflict_owner = Owner("Jordan", 120)
conflict_dog = Pet("Mochi", "dog", 3)
conflict_cat = Pet("Luna",  "cat", 2)

# Intentionally overlapping: Walk starts at 8:00 (480 min), runs 30 min → ends 8:30
#                             Feeding starts at 8:10 (490 min), runs 20 min → ends 8:30
conflict_dog.add_task(Task("Morning walk",    30, "high", "walk",    start_time=480))
conflict_cat.add_task(Task("Wet food feeding",20, "high", "feeding", start_time=490))
# Non-overlapping: Grooming starts at 8:30 (510 min), no conflict
conflict_dog.add_task(Task("Grooming",        15, "low",  "grooming", start_time=510))

conflict_owner.add_pet(conflict_dog)
conflict_owner.add_pet(conflict_cat)

for pet in conflict_owner.get_pets():
    for task in pet.get_pending_tasks():
        if task.start_time is not None:
            end = task.start_time + task.duration_minutes
            print(f"  {pet.name}: '{task.title}' {mins_to_time(task.start_time)}–{mins_to_time(end)}")

print()
conflicts = Scheduler(conflict_owner).detect_conflicts()
if conflicts:
    for w in conflicts:
        print(f"  {w}")
else:
    print("  No conflicts found.")

print("=" * 40)
print()

# --- Setup ---
owner = Owner("Jordan", available_minutes=90)

dog = Pet("Mochi", "dog", 3)
cat = Pet("Luna", "cat", 2)

# --- Tasks added intentionally out of priority/duration order ---
dog.add_task(Task("Fetch / playtime",    20, "medium", "enrichment"))        # medium, 20 min
dog.add_task(Task("Morning walk",        30, "high",   "walk"))              # high,   30 min
dog.add_task(Task("Give heartworm meds",  5, "high",   "meds", frequency="weekly"))  # high, 5 min

cat.add_task(Task("Brush coat",          15, "low",    "grooming", frequency="weekly"))  # low, 15 min
cat.add_task(Task("Wet food feeding",    10, "high",   "feeding"))           # high,  10 min

owner.add_pet(dog)
owner.add_pet(cat)

scheduler = Scheduler(owner)

# --- 1. Raw order (as added) ---
print("=" * 40)
print("  RAW ORDER (as added)")
print("=" * 40)
for pet in owner.get_pets():
    for task in pet.get_tasks():
        print(f"  [{task.priority.upper():6}] {task.title} ({task.duration_minutes} min) — {pet.name}")

# --- 2. Sorted order (priority + duration tiebreaker) ---
print("\n" + "=" * 40)
print("  SORTED ORDER (_sort_tasks)")
print("=" * 40)
for task in scheduler._sort_tasks():
    pet_name = next(p.name for p in owner.get_pets() if task in p.get_tasks())
    print(f"  [{task.priority.upper():6}] {task.title} ({task.duration_minutes} min) — {pet_name}")

# --- 3. Mark one task complete, then show pending vs all ---
print("\n" + "=" * 40)
print("  MARK 'Morning walk' COMPLETE")
print("  THEN COMPARE get_tasks() vs get_pending_tasks()")
print("=" * 40)
scheduler.mark_task_complete("Morning walk")

print("\n  All tasks (get_tasks):")
for task in dog.get_tasks():
    status = "done" if task.completed else "pending"
    print(f"    {task.title} — {status}")

print("\n  Pending only (get_pending_tasks):")
for task in dog.get_pending_tasks():
    print(f"    {task.title}")

# --- 4. Generate plan (completed task should be excluded) ---
print("\n" + "=" * 40)
print("  TODAY'S SCHEDULE (after marking walk done)")
print(f"  Owner : {owner.name} | Budget: {owner.available_minutes} min")
print("=" * 40)

plan = scheduler.generate_plan()

if plan.scheduled_tasks:
    print("\nScheduled:")
    for task in plan.scheduled_tasks:
        pet_name = next(p.name for p in owner.get_pets() if task in p.get_tasks())
        print(f"  [{task.priority.upper():6}] {task.title} ({task.duration_minutes} min) — {pet_name}")
else:
    print("\nNo tasks scheduled.")

if plan.skipped_tasks:
    print("\nSkipped (not enough time):")
    for task in plan.skipped_tasks:
        print(f"  - {task.title} ({task.duration_minutes} min)")

print(f"\nTotal time used: {plan.total_duration} / {owner.available_minutes} min")
print("\nReasoning:")
print(plan.explain())
print("=" * 40)

# --- 5. Reset all and confirm ---
print("\n" + "=" * 40)
print("  AFTER reset_all_tasks()")
print("=" * 40)
scheduler.reset_all_tasks()
for task in dog.get_tasks():
    status = "done" if task.completed else "pending"
    print(f"  {task.title} — {status}")
