import pytest
from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler, DailyPlan


# --- Task ---

def test_task_is_high_priority():
    task = Task("Give meds", 5, "high", "meds")
    assert task.is_high_priority() is True

def test_task_not_high_priority():
    task = Task("Enrichment toy", 15, "low", "enrichment")
    assert task.is_high_priority() is False

def test_task_repr():
    task = Task("Morning walk", 30, "high", "walk")
    assert "Morning walk" in repr(task)

def test_task_default_frequency():
    task = Task("Walk", 20, "high", "walk")
    assert task.frequency == "daily"

def test_task_custom_frequency():
    task = Task("Grooming", 30, "low", "grooming", frequency="weekly")
    assert task.frequency == "weekly"

def test_task_starts_incomplete():
    task = Task("Walk", 20, "high", "walk")
    assert task.completed is False

def test_task_mark_complete():
    task = Task("Walk", 20, "high", "walk")
    task.mark_complete()
    assert task.completed is True

def test_task_reset():
    task = Task("Walk", 20, "high", "walk")
    task.mark_complete()
    task.reset()
    assert task.completed is False


# --- Pet ---

def test_pet_add_and_get_tasks():
    pet = Pet("Mochi", "dog", 3)
    task = Task("Walk", 20, "high", "walk")
    pet.add_task(task)
    assert task in pet.get_tasks()

def test_pet_starts_with_no_tasks():
    pet = Pet("Mochi", "dog", 3)
    assert pet.get_tasks() == []

def test_pet_remove_task():
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Walk", 20, "high", "walk"))
    pet.add_task(Task("Feeding", 10, "high", "feeding"))
    pet.remove_task("Walk")
    titles = [t.title for t in pet.get_tasks()]
    assert "Walk" not in titles
    assert "Feeding" in titles

def test_pet_get_pending_tasks_excludes_completed():
    pet = Pet("Mochi", "dog", 3)
    walk = Task("Walk", 20, "high", "walk")
    meds = Task("Give meds", 5, "high", "meds")
    pet.add_task(walk)
    pet.add_task(meds)
    walk.mark_complete()
    pending = pet.get_pending_tasks()
    assert walk not in pending
    assert meds in pending


# --- Owner ---

def test_owner_get_available_minutes():
    owner = Owner("Jordan", 60)
    assert owner.get_available_minutes() == 60

def test_owner_default_preferences():
    owner = Owner("Jordan", 60)
    assert owner.preferences == []

def test_owner_add_and_get_pets():
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog", 3)
    owner.add_pet(pet)
    assert pet in owner.get_pets()

def test_owner_get_all_tasks_across_pets():
    owner = Owner("Jordan", 120)
    dog = Pet("Mochi", "dog", 3)
    cat = Pet("Luna", "cat", 2)
    dog.add_task(Task("Walk", 20, "high", "walk"))
    cat.add_task(Task("Feeding", 10, "high", "feeding"))
    owner.add_pet(dog)
    owner.add_pet(cat)
    titles = [t.title for t in owner.get_all_tasks()]
    assert "Walk" in titles
    assert "Feeding" in titles


# --- Scheduler ---

def test_sort_tasks_full_order():
    """_sort_tasks returns tasks ordered high→medium→low, shortest-first within same priority."""
    owner = Owner("Jordan", 120)
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Enrichment",  20, "low",    "enrichment"))
    pet.add_task(Task("Long walk",   30, "high",   "walk"))
    pet.add_task(Task("Give meds",    5, "high",   "meds"))
    pet.add_task(Task("Bath",        25, "medium", "grooming"))
    pet.add_task(Task("Feeding",     10, "medium", "feeding"))
    owner.add_pet(pet)

    sorted_titles = [t.title for t in Scheduler(owner)._sort_tasks()]
    assert sorted_titles == ["Give meds", "Long walk", "Feeding", "Bath", "Enrichment"]

def test_scheduler_schedules_high_priority_first():
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Enrichment", 20, "low", "enrichment"))
    pet.add_task(Task("Give meds", 10, "high", "meds"))
    pet.add_task(Task("Walk", 30, "medium", "walk"))
    owner.add_pet(pet)

    plan = Scheduler(owner).generate_plan()
    assert plan.scheduled_tasks[0].title == "Give meds"

def test_scheduler_skips_tasks_that_dont_fit():
    owner = Owner("Jordan", 30)
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Walk", 20, "high", "walk"))
    pet.add_task(Task("Grooming", 60, "medium", "grooming"))
    owner.add_pet(pet)

    plan = Scheduler(owner).generate_plan()
    scheduled_titles = [t.title for t in plan.scheduled_tasks]
    skipped_titles = [t.title for t in plan.skipped_tasks]
    assert "Walk" in scheduled_titles
    assert "Grooming" in skipped_titles

def test_scheduler_respects_available_time():
    owner = Owner("Jordan", 30)
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Walk", 20, "high", "walk"))
    pet.add_task(Task("Feeding", 15, "medium", "feeding"))
    owner.add_pet(pet)

    plan = Scheduler(owner).generate_plan()
    assert plan.total_duration <= 30

def test_scheduler_shorter_task_scheduled_before_longer_same_priority():
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Long walk", 55, "high", "walk"))
    pet.add_task(Task("Give meds", 5, "high", "meds"))
    owner.add_pet(pet)

    plan = Scheduler(owner).generate_plan()
    assert plan.scheduled_tasks[0].title == "Give meds"

def test_scheduler_invalid_priority_does_not_crash():
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Mystery task", 10, "urgent", "other"))
    owner.add_pet(pet)

    plan = Scheduler(owner).generate_plan()
    assert len(plan.scheduled_tasks) == 1

def test_scheduler_no_tasks_produces_empty_plan():
    owner = Owner("Jordan", 60)
    owner.add_pet(Pet("Mochi", "dog", 3))
    plan = Scheduler(owner).generate_plan()
    assert plan.scheduled_tasks == []
    assert plan.skipped_tasks == []
    assert plan.total_duration == 0

def test_scheduler_skips_completed_tasks():
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog", 3)
    walk = Task("Walk", 20, "high", "walk")
    walk.mark_complete()
    pet.add_task(walk)
    pet.add_task(Task("Feeding", 10, "high", "feeding"))
    owner.add_pet(pet)

    plan = Scheduler(owner).generate_plan()
    titles = [t.title for t in plan.scheduled_tasks]
    assert "Walk" not in titles
    assert "Feeding" in titles

def test_scheduler_aggregates_tasks_across_multiple_pets():
    owner = Owner("Jordan", 120)
    dog = Pet("Mochi", "dog", 3)
    cat = Pet("Luna", "cat", 2)
    dog.add_task(Task("Walk", 20, "high", "walk"))
    cat.add_task(Task("Feeding", 10, "high", "feeding"))
    owner.add_pet(dog)
    owner.add_pet(cat)

    plan = Scheduler(owner).generate_plan()
    titles = [t.title for t in plan.scheduled_tasks]
    assert "Walk" in titles
    assert "Feeding" in titles

def test_scheduler_mark_task_complete():
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Walk", 20, "high", "walk"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    result = scheduler.mark_task_complete("Walk")
    assert result is True
    assert pet.get_tasks()[0].completed is True

def test_scheduler_mark_task_complete_requeues_daily_task():
    """Completing a daily task adds a fresh pending instance due tomorrow."""
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Walk", 20, "high", "walk", frequency="daily"))
    owner.add_pet(pet)

    Scheduler(owner).mark_task_complete("Walk")

    tasks = pet.get_tasks()
    assert tasks[0].completed is True
    assert tasks[1].completed is False
    assert tasks[1].title == "Walk"
    assert tasks[1].frequency == "daily"
    assert tasks[1].due_date == date.today() + timedelta(days=1)

def test_scheduler_mark_task_complete_requeues_weekly_task():
    """Completing a weekly task adds a fresh pending instance due in 7 days."""
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Grooming", 30, "low", "grooming", frequency="weekly"))
    owner.add_pet(pet)

    Scheduler(owner).mark_task_complete("Grooming")

    tasks = pet.get_tasks()
    assert tasks[0].completed is True
    assert tasks[1].completed is False
    assert tasks[1].frequency == "weekly"
    assert tasks[1].due_date == date.today() + timedelta(days=7)

def test_scheduler_mark_task_complete_does_not_requeue_as_needed_task():
    """Completing an as-needed task does not add a new instance to the pet's task list."""
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Vet visit", 60, "high", "other", frequency="as-needed"))
    owner.add_pet(pet)

    Scheduler(owner).mark_task_complete("Vet visit")

    assert len(pet.get_tasks()) == 1          # no new instance added
    assert pet.get_tasks()[0].completed is True

def test_scheduler_mark_task_complete_returns_false_if_not_found():
    owner = Owner("Jordan", 60)
    owner.add_pet(Pet("Mochi", "dog", 3))
    assert Scheduler(owner).mark_task_complete("Nonexistent") is False

def test_detect_conflicts_finds_overlap():
    """Two tasks on the same pet with overlapping time windows produce one warning."""
    owner = Owner("Jordan", 120)
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Walk",     30, "high", "walk",    start_time=480))  # 8:00–8:30
    pet.add_task(Task("Feeding",  15, "high", "feeding", start_time=490))  # 8:10–8:25  ← overlaps
    owner.add_pet(pet)

    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1
    assert "Walk" in warnings[0]
    assert "Feeding" in warnings[0]

def test_detect_conflicts_no_overlap():
    """Adjacent tasks that touch but do not overlap produce no warnings."""
    owner = Owner("Jordan", 120)
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Walk",     30, "high", "walk",    start_time=480))  # 8:00–8:30
    pet.add_task(Task("Feeding",  15, "high", "feeding", start_time=510))  # 8:30–8:45  ← adjacent, no overlap
    owner.add_pet(pet)

    warnings = Scheduler(owner).detect_conflicts()
    assert warnings == []

def test_detect_conflicts_across_pets():
    """Overlapping tasks belonging to different pets are still flagged as conflicts."""
    owner = Owner("Jordan", 120)
    dog = Pet("Mochi", "dog", 3)
    cat = Pet("Luna",  "cat", 2)
    dog.add_task(Task("Walk",    30, "high", "walk",    start_time=480))   # 8:00–8:30
    cat.add_task(Task("Feeding", 20, "high", "feeding", start_time=470))   # 7:50–8:10  ← overlaps walk
    owner.add_pet(dog)
    owner.add_pet(cat)

    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1

def test_detect_conflicts_ignores_tasks_without_start_time():
    """Tasks with no start_time are excluded from conflict checking entirely."""
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Walk",    30, "high", "walk"))     # no start_time
    pet.add_task(Task("Feeding", 15, "high", "feeding"))  # no start_time
    owner.add_pet(pet)

    warnings = Scheduler(owner).detect_conflicts()
    assert warnings == []

def test_scheduler_reset_all_tasks():
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog", 3)
    task = Task("Walk", 20, "high", "walk")
    task.mark_complete()
    pet.add_task(task)
    owner.add_pet(pet)

    Scheduler(owner).reset_all_tasks()
    assert task.completed is False


# --- DailyPlan ---

def test_daily_plan_display_lists_scheduled_tasks():
    tasks = [Task("Walk", 20, "high", "walk")]
    plan = DailyPlan(tasks, [], 20)
    output = plan.display()
    assert "Walk" in output

def test_daily_plan_display_empty():
    plan = DailyPlan([], [], 0)
    assert plan.display() == "No tasks scheduled."

def test_daily_plan_explain_mentions_skipped():
    skipped = [Task("Grooming", 60, "low", "grooming")]
    plan = DailyPlan([], skipped, 0)
    assert "skipped" in plan.explain()
