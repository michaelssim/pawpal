from datetime import date, timedelta


class Task:
    def __init__(self, title, duration_minutes, priority, category, frequency="daily", due_date=None, start_time=None):
        """Create a Task with a title, duration, priority, category, frequency, optional due date, and optional start time."""
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority      # "low", "medium", "high"
        self.category = category      # e.g. "walk", "feeding", "meds", "grooming"
        self.frequency = frequency    # "daily", "weekly", "as-needed"
        self.due_date = due_date      # date object or None
        self.start_time = start_time  # minutes from midnight, e.g. 480 = 8:00am; None = unscheduled
        self.completed = False

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True

    def reset(self):
        """Reset this task to incomplete so it can be scheduled again."""
        self.completed = False

    def score(self):
        """Return a numeric urgency score; higher scores are scheduled first.

        Base score comes from priority (high=100, medium=50, low=10).
        An urgency bonus is added when a due_date is set:
          overdue → +50, due today → +40, tomorrow → +30,
          2–3 days → +20, 4–7 days → +10, further out → +0.
        """
        base = {"high": 100, "medium": 50, "low": 10}.get(self.priority, 5)
        if self.due_date is None:
            return base
        days_left = (self.due_date - date.today()).days
        if days_left < 0:
            urgency = 50
        elif days_left == 0:
            urgency = 40
        elif days_left == 1:
            urgency = 30
        elif days_left <= 3:
            urgency = 20
        elif days_left <= 7:
            urgency = 10
        else:
            urgency = 0
        return base + urgency

    def is_high_priority(self):
        """Return True if this task's priority is 'high'."""
        return self.priority == "high"

    def __repr__(self):
        """Return a readable string representation of the task."""
        status = "done" if self.completed else "pending"
        return f"Task({self.title!r}, {self.duration_minutes}min, {self.priority}, {status})"


class Pet:
    def __init__(self, name, species, age):
        """Create a Pet with a name, species, and age; starts with an empty task list."""
        self.name = name
        self.species = species
        self.age = age
        self.tasks = []

    def add_task(self, task):
        """Add a Task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title):
        """Remove the task with the given title from this pet's task list."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def get_tasks(self):
        """Return all tasks assigned to this pet."""
        return self.tasks

    def get_pending_tasks(self):
        """Return only the tasks that have not yet been completed."""
        return [t for t in self.tasks if not t.completed]


class Owner:
    def __init__(self, name, available_minutes, preferences=None):
        """Create an Owner with a name, daily time budget, and optional preferences; starts with no pets."""
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences or []
        self.pets = []

    def add_pet(self, pet):
        """Add a Pet to this owner's list of pets."""
        self.pets.append(pet)

    def get_pets(self):
        """Return all pets belonging to this owner."""
        return self.pets

    def get_all_tasks(self):
        """Return every task across all of this owner's pets."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks())
        return tasks

    def get_available_minutes(self):
        """Return the number of minutes the owner has available today."""
        return self.available_minutes


class Scheduler:
    def __init__(self, owner):
        """Create a Scheduler bound to a specific Owner."""
        self.owner = owner

    def get_all_pending_tasks(self):
        """Collect and return all incomplete tasks across every pet."""
        tasks = []
        for pet in self.owner.get_pets():
            tasks.extend(pet.get_pending_tasks())
        return tasks

    def generate_plan(self):
        """Build and return a DailyPlan by fitting tasks into the owner's time budget."""
        sorted_tasks = self._sort_tasks()
        scheduled = []
        skipped = []
        time_used = 0

        for task in sorted_tasks:
            if self._fits_in_time(task, time_used):
                scheduled.append(task)
                time_used += task.duration_minutes
            else:
                skipped.append(task)

        return DailyPlan(scheduled, skipped, time_used)

    def mark_task_complete(self, title):
        """Mark a task complete; re-queue a fresh instance with the next due date if recurring."""
        intervals = {"daily": timedelta(days=1), "weekly": timedelta(days=7)}
        for pet in self.owner.get_pets():
            for task in pet.get_tasks():
                if task.title == title:
                    task.mark_complete()
                    if task.frequency in intervals:
                        next_due = date.today() + intervals[task.frequency]
                        pet.add_task(Task(
                            task.title,
                            task.duration_minutes,
                            task.priority,
                            task.category,
                            task.frequency,
                            due_date=next_due,
                        ))
                    return True
        return False

    def detect_conflicts(self):
        """Return a list of warning strings for any tasks whose time windows overlap; never raises."""
        warnings = []
        timed_tasks = [
            (task, pet.name)
            for pet in self.owner.get_pets()
            for task in pet.get_pending_tasks()
            if task.start_time is not None
        ]
        for i, (a, pet_a) in enumerate(timed_tasks):
            for b, pet_b in timed_tasks[i + 1:]:
                a_end = a.start_time + a.duration_minutes
                b_end = b.start_time + b.duration_minutes
                if a.start_time < b_end and b.start_time < a_end:
                    overlap_start = max(a.start_time, b.start_time)
                    overlap_end = min(a_end, b_end)
                    warnings.append(
                        f"WARNING: '{a.title}' ({pet_a}) and '{b.title}' ({pet_b}) "
                        f"overlap by {overlap_end - overlap_start} min "
                        f"(both active around minute {overlap_start})"
                    )
        return warnings

    def reset_all_tasks(self):
        """Reset every task across all pets back to incomplete."""
        for pet in self.owner.get_pets():
            for task in pet.get_tasks():
                task.reset()

    def _sort_tasks(self):
        """Sort pending tasks by weighted urgency score descending, then duration ascending as tiebreaker."""
        return sorted(
            self.get_all_pending_tasks(),
            key=lambda t: (-t.score(), t.duration_minutes)
        )

    def _fits_in_time(self, task, time_used):
        """Return True if adding this task would not exceed the owner's available time."""
        return time_used + task.duration_minutes <= self.owner.get_available_minutes()


class DailyPlan:
    def __init__(self, scheduled_tasks, skipped_tasks, total_duration):
        """Store the scheduled tasks, skipped tasks, and total time used for a day's plan."""
        self.scheduled_tasks = scheduled_tasks
        self.skipped_tasks = skipped_tasks
        self.total_duration = total_duration

    def display(self):
        """Return a formatted string listing all scheduled tasks and total time used."""
        if not self.scheduled_tasks:
            return "No tasks scheduled."
        lines = ["Scheduled tasks:"]
        for task in self.scheduled_tasks:
            lines.append(f"  - {task.title} ({task.duration_minutes} min, {task.priority} priority)")
        lines.append(f"Total time: {self.total_duration} min")
        return "\n".join(lines)

    def explain(self):
        """Return a plain-language explanation of why each task was scheduled or skipped."""
        lines = []
        for task in self.scheduled_tasks:
            lines.append(f"  - '{task.title}' was scheduled because it is {task.priority} priority.")
        for task in self.skipped_tasks:
            lines.append(f"  - '{task.title}' was skipped due to insufficient time remaining.")
        return "\n".join(lines) if lines else "Nothing to explain."
