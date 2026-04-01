from pawpal_system import Task, Pet, Owner, Scheduler

# --- Setup ---
owner = Owner("Jordan", available_minutes=90)

dog = Pet("Mochi", "dog", 3)
cat = Pet("Luna", "cat", 2)

# --- Tasks for Mochi (dog) ---
dog.add_task(Task("Morning walk",    30, "high",   "walk"))
dog.add_task(Task("Give heartworm meds", 5, "high", "meds", frequency="weekly"))
dog.add_task(Task("Fetch / playtime", 20, "medium", "enrichment"))

# --- Tasks for Luna (cat) ---
cat.add_task(Task("Wet food feeding", 10, "high",  "feeding"))
cat.add_task(Task("Brush coat",       15, "low",   "grooming", frequency="weekly"))

owner.add_pet(dog)
owner.add_pet(cat)

# --- Generate plan ---
plan = Scheduler(owner).generate_plan()

# --- Print schedule ---
print("=" * 40)
print("       TODAY'S SCHEDULE")
print(f"       Owner : {owner.name}")
print(f"       Budget: {owner.available_minutes} min")
print("=" * 40)

if plan.scheduled_tasks:
    print("\nScheduled:")
    for task in plan.scheduled_tasks:
        pet_name = next(
            p.name for p in owner.get_pets() if task in p.get_tasks()
        )
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
