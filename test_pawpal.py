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

def test_scheduler_mark_task_complete_returns_false_if_not_found():
    owner = Owner("Jordan", 60)
    owner.add_pet(Pet("Mochi", "dog", 3))
    assert Scheduler(owner).mark_task_complete("Nonexistent") is False

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
