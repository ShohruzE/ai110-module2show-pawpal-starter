"""Minimal PawPal system skeleton.

- Keep scope small: `User`, `Pet`, `Task`, `Schedule`, `Reminder`.
- Use `dataclasses` for `Task` and `Pet` as requested.

This file is intentionally lightweight and suitable for the small app.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, time
from typing import List, Optional
from uuid import uuid4


@dataclass
class Task:
    id: str = field(default_factory=lambda: uuid4().hex)
    pet_id: str = ""
    title: str = ""
    due_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    priority: int = 2  # 1=low,2=medium,3=high
    frequency: str = "once"  # once|daily|weekly|monthly
    completed: bool = False
    completed_at: Optional[datetime] = None
    completed_by: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate priority and frequency after initialization."""
        if not (1 <= self.priority <= 3):
            raise ValueError("priority must be 1..3")
        valid_frequencies = {"once", "daily", "weekly", "monthly"}
        if self.frequency not in valid_frequencies:
            raise ValueError(f"frequency must be one of {valid_frequencies}")

    def is_due(self, when: Optional[datetime] = None) -> bool:
        """Return True if the task is due (time passed) and not completed."""
        when = when or datetime.now()
        return (
            (self.due_time is not None)
            and (when >= self.due_time)
            and (not self.completed)
        )

    def mark_complete(
        self,
        when: Optional[datetime] = None,
        by: Optional[str] = None,
        owner_pets: Optional[List["Pet"]] = None,
    ) -> Optional["Task"]:
        """Mark the task complete and record timestamp and actor."""
        self.completed = True
        self.completed_at = when or datetime.now()
        self.completed_by = by

        # If this is a recurring task (daily/weekly), create the next occurrence.
        if self.frequency in {"daily", "weekly"}:
            # Calculate next due time using timedelta; preserve time-of-day when possible.
            base_dt = when or datetime.now()
            if self.frequency == "daily":
                delta = timedelta(days=1)
            else:
                delta = timedelta(weeks=1)

            if self.due_time:
                # Preserve original time-of-day
                next_date = (base_dt + delta).date()
                next_due = datetime.combine(next_date, self.due_time.time())
            else:
                next_due = base_dt + delta

            new_task = Task(
                pet_id=self.pet_id,
                title=self.title,
                due_time=next_due,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                frequency=self.frequency,
            )

            # If owner_pets provided, attempt to attach the new task to the matching Pet
            if owner_pets:
                for pet in owner_pets:
                    if pet.id == self.pet_id:
                        pet.add_task(new_task)
                        break

            return new_task

        return None

    def reschedule(self, new_time: datetime) -> None:
        """Set a new due time for the task."""
        self.due_time = new_time

    @staticmethod
    def sort_by_time(tasks: List["Task"]) -> List["Task"]:
        """Return a new list of tasks sorted by `due_time` (earliest first).

        Tasks with no `due_time` sort to the end.
        """
        return sorted(tasks, key=lambda t: t.due_time or datetime.max)


@dataclass
class Pet:
    id: str = field(default_factory=lambda: uuid4().hex)
    owner_id: str = ""
    name: str = ""
    species: str = "dog"
    birth_date: Optional[date] = None
    tasks: List[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate that the pet has a non-empty name."""
        if not self.name:
            raise ValueError("Pet.name must not be empty")

    def add_task(self, task: Task) -> None:
        """Attach a Task to this pet and set the task's pet_id."""
        task.pet_id = self.id
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a Task from this pet by its id."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def age_years(self) -> Optional[int]:
        """Return pet age in whole years, or None if birth date unknown."""
        if not self.birth_date:
            return None
        today = date.today()
        years = (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )
        return years


@dataclass
class ScheduleSlot:
    id: str = field(default_factory=lambda: uuid4().hex)
    task_id: str = ""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = field(default_factory=datetime.now)
    status: str = "planned"  # planned|complete|skipped

    def overlaps(self, other: "ScheduleSlot") -> bool:
        """Return True if this slot overlaps the other slot."""
        return not (
            self.end_time <= other.start_time or self.start_time >= other.end_time
        )


class Schedule:
    def __init__(self, owner_id: str, date_for: date):
        self.owner_id = owner_id
        self.date = date_for
        self.slots: List[ScheduleSlot] = []
        self.generated_at: Optional[datetime] = None
        self.warnings: List[str] = []

    def generate(self, tasks_pool: List[Task], day_start: time = time(8, 0)) -> None:
        """Greedy pack tasks into non-overlapping slots.

        - Tasks without a duration get a default of 10 minutes.
        - Tasks are ordered by priority (desc), then due_time.
        - Start at `day_start` and avoid overlaps by shifting later.
        """
        """Pack tasks into non-overlapping schedule slots for this date."""
        # clear previous warnings and build today's tasks
        self.warnings = []
        tasks = [t for t in tasks_pool if t.due_time and t.due_time.date() == self.date]
        tasks.sort(key=lambda t: (-t.priority, t.due_time or datetime.min))

        self.slots = []
        current_dt = datetime.combine(self.date, day_start)

        for t in tasks:
            duration = timedelta(minutes=(t.duration_minutes or 10))
            # prefer task due_time if it's later than current pointer
            preferred_start = (
                t.due_time if t.due_time and t.due_time > current_dt else current_dt
            )
            start = preferred_start
            end = start + duration

            # if overlapping previous slot, shift to previous end
            if self.slots and start < self.slots[-1].end_time:
                start = self.slots[-1].end_time
                end = start + duration

            slot = ScheduleSlot(task_id=t.id, start_time=start, end_time=end)
            self.slots.append(slot)
            current_dt = end

        self.generated_at = datetime.now()

    def detect_conflicts(
        self, task_lookup: Optional[dict] = None, pet_lookup: Optional[dict] = None
    ) -> List[str]:
        """Detect overlapping schedule slots and return human-friendly warning messages.

        If `task_lookup` and `pet_lookup` are provided they will be used to include
        task titles and pet names in the warning messages; otherwise task ids are used.
        """
        warnings: List[str] = []
        n = len(self.slots)
        for i in range(n):
            a = self.slots[i]
            for j in range(i + 1, n):
                b = self.slots[j]
                if a.overlaps(b):

                    def desc(slot):
                        if task_lookup and slot.task_id in task_lookup:
                            t = task_lookup[slot.task_id]
                            pet_name = (
                                pet_lookup[t.pet_id].name
                                if pet_lookup and t.pet_id in pet_lookup
                                else t.pet_id
                            )
                            return f"'{t.title}' (pet: {pet_name})"
                        return slot.task_id

                    msg = (
                        f"Conflict: {desc(a)} [{a.start_time.strftime('%H:%M')} - {a.end_time.strftime('%H:%M')}] "
                        f"overlaps {desc(b)} [{b.start_time.strftime('%H:%M')} - {b.end_time.strftime('%H:%M')}]"
                    )
                    warnings.append(msg)

        self.warnings = warnings
        return warnings

    def detect_desired_time_conflicts(
        self,
        tasks_pool: List[Task],
        task_lookup: Optional[dict] = None,
        pet_lookup: Optional[dict] = None,
    ) -> List[str]:
        """Detect tasks that share the exact same desired `due_time` on this schedule's date.

        This method warns when two or more tasks are scheduled to start at the exact
        same datetime (useful because the greedy scheduler will shift tasks and hide
        that original conflict). Returns a list of warning messages.
        """
        groups = {}
        for t in tasks_pool:
            if not t.due_time or t.due_time.date() != self.date:
                continue
            key = t.due_time
            groups.setdefault(key, []).append(t)

        warnings: List[str] = []
        for dt, tasks in groups.items():
            if len(tasks) > 1:
                names = []
                for t in tasks:
                    if task_lookup and t.id in task_lookup:
                        tt = task_lookup[t.id]
                        pet_name = (
                            pet_lookup[tt.pet_id].name
                            if pet_lookup and tt.pet_id in pet_lookup
                            else tt.pet_id
                        )
                        names.append(f"'{tt.title}' (pet: {pet_name})")
                    else:
                        names.append(f"{t.title} (id:{t.id})")
                timestr = dt.strftime("%H:%M")
                warnings.append(
                    f"Desired-time conflict at {timestr}: multiple tasks start then: {', '.join(names)}"
                )

        # do not overwrite slot-based warnings — append for caller convenience
        self.warnings = list(self.warnings) + warnings
        return warnings


class Reminder:
    def __init__(
        self,
        id: Optional[str],
        user_id: str,
        message: str,
        trigger: datetime,
        pet_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ):
        self.id = id or uuid4().hex
        self.user_id = user_id
        self.pet_id = pet_id
        self.task_id = task_id
        self.message = message
        self.trigger = trigger

    def snooze(self, minutes: int = 10) -> None:
        """Postpone the reminder by the given number of minutes."""
        self.trigger = self.trigger + timedelta(minutes=minutes)


class User:
    def __init__(self, id: Optional[str], name: str, email: Optional[str] = None):
        self.id = id or uuid4().hex
        self.name = name
        self.email = email
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Attach a pet to this user and set ownership."""
        pet.owner_id = self.id
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        """Remove a pet from the user by id."""
        self.pets = [p for p in self.pets if p.id != pet_id]

    def get_tasks_for_date(self, target_date: date) -> List[Task]:
        """Collect tasks across all pets that are due on target_date."""
        tasks: List[Task] = []
        for pet in self.pets:
            for t in pet.tasks:
                if t.due_time and t.due_time.date() == target_date:
                    tasks.append(t)
        return tasks

    def filter_tasks(
        self, completed: Optional[bool] = None, pet_name: Optional[str] = None
    ) -> List[Task]:
        """Return tasks optionally filtered by completion status and/or pet name.

        - `completed` if set will filter tasks by their `completed` flag.
        - `pet_name` if set will match pet name case-insensitively.
        """
        results: List[Task] = []
        for pet in self.pets:
            if pet_name and pet.name.lower() != pet_name.lower():
                continue
            for t in pet.tasks:
                if completed is None or t.completed == completed:
                    results.append(t)
        return results


# Small usage example (kept minimal for the project)
if __name__ == "__main__":
    user = User(None, "Alex")
    pet = Pet(name="Rex", species="dog")
    task = Task(title="Feed breakfast", due_time=datetime.now(), duration_minutes=15)
    pet.add_task(task)
    user.add_pet(pet)

    today_schedule = Schedule(owner_id=user.id, date_for=date.today())
    today_schedule.generate(user.get_tasks_for_date(date.today()))
    print(
        "Schedule slots:",
        [
            (s.task_id, s.start_time.time(), s.end_time.time())
            for s in today_schedule.slots
        ],
    )
