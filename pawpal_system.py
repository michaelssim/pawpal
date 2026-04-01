class Task:
    def __init__(self, title, duration_minutes, priority, category):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority  # "low", "medium", "high"
        self.category = category  # e.g. "walk", "feeding", "meds", "grooming"

    def is_high_priority(self):
        return self.priority == "high"

    def __repr__(self):
        return f"Task({self.title!r}, {self.duration_minutes}min, {self.priority})"


class Pet:
    def __init__(self, name, species, age):
        self.name = name
        self.species = species
        self.age = age
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def get_tasks(self):
        return self.tasks


class Owner:
    def __init__(self, name, available_minutes, preferences=None):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences or []

    def get_available_minutes(self):
        return self.available_minutes


class Scheduler:
    def __init__(self, owner, pet):
        self.owner = owner
        self.pet = pet

    def generate_plan(self):
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

    def _sort_tasks(self):
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(self.pet.get_tasks(), key=lambda t: priority_order[t.priority])

    def _fits_in_time(self, task, time_used):
        return time_used + task.duration_minutes <= self.owner.get_available_minutes()


class DailyPlan:
    def __init__(self, scheduled_tasks, skipped_tasks, total_duration):
        self.scheduled_tasks = scheduled_tasks
        self.skipped_tasks = skipped_tasks
        self.total_duration = total_duration

    def display(self):
        if not self.scheduled_tasks:
            return "No tasks scheduled."
        lines = ["Scheduled tasks:"]
        for task in self.scheduled_tasks:
            lines.append(f"  - {task.title} ({task.duration_minutes} min, {task.priority} priority)")
        lines.append(f"Total time: {self.total_duration} min")
        return "\n".join(lines)

    def explain(self):
        lines = []
        for task in self.scheduled_tasks:
            lines.append(f"  - '{task.title}' was scheduled because it is {task.priority} priority.")
        for task in self.skipped_tasks:
            lines.append(f"  - '{task.title}' was skipped due to insufficient time remaining.")
        return "\n".join(lines) if lines else "Nothing to explain."
