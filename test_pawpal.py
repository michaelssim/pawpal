import pytest
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


# --- Pet ---

def test_pet_add_and_get_tasks():
    pet = Pet("Mochi", "dog", 3)
    task = Task("Walk", 20, "high", "walk")
    pet.add_task(task)
    assert task in pet.get_tasks()

def test_pet_starts_with_no_tasks():
    pet = Pet("Mochi", "dog", 3)
    assert pet.get_tasks() == []


# --- Owner ---

def test_owner_get_available_minutes():
    owner = Owner("Jordan", 60)
    assert owner.get_available_minutes() == 60

def test_owner_default_preferences():
    owner = Owner("Jordan", 60)
    assert owner.preferences == []


# --- Scheduler ---

def test_scheduler_schedules_high_priority_first():
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Enrichment", 20, "low", "enrichment"))
    pet.add_task(Task("Give meds", 10, "high", "meds"))
    pet.add_task(Task("Walk", 30, "medium", "walk"))

    plan = Scheduler(owner, pet).generate_plan()
    assert plan.scheduled_tasks[0].title == "Give meds"

def test_scheduler_skips_tasks_that_dont_fit():
    owner = Owner("Jordan", 30)
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Walk", 20, "high", "walk"))
    pet.add_task(Task("Grooming", 60, "medium", "grooming"))  # won't fit

    plan = Scheduler(owner, pet).generate_plan()
    scheduled_titles = [t.title for t in plan.scheduled_tasks]
    skipped_titles = [t.title for t in plan.skipped_tasks]
    assert "Walk" in scheduled_titles
    assert "Grooming" in skipped_titles

def test_scheduler_respects_available_time():
    owner = Owner("Jordan", 30)
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Walk", 20, "high", "walk"))
    pet.add_task(Task("Feeding", 15, "medium", "feeding"))  # 20+15=35 > 30

    plan = Scheduler(owner, pet).generate_plan()
    assert plan.total_duration <= 30

def test_scheduler_shorter_task_scheduled_before_longer_same_priority():
    # Two high-priority tasks: short one should come first so more tasks fit
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Long walk", 55, "high", "walk"))
    pet.add_task(Task("Give meds", 5, "high", "meds"))

    plan = Scheduler(owner, pet).generate_plan()
    assert plan.scheduled_tasks[0].title == "Give meds"

def test_scheduler_invalid_priority_does_not_crash():
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Mystery task", 10, "urgent", "other"))  # invalid priority

    plan = Scheduler(owner, pet).generate_plan()
    assert len(plan.scheduled_tasks) == 1  # still scheduled, treated as lowest priority

def test_scheduler_no_tasks_produces_empty_plan():
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog", 3)
    plan = Scheduler(owner, pet).generate_plan()
    assert plan.scheduled_tasks == []
    assert plan.skipped_tasks == []
    assert plan.total_duration == 0


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
