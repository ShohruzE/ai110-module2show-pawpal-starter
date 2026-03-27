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
    completed: bool = False
    completed_at: Optional[datetime] = None
    completed_by: Optional[str] = None

    def __post_init__(self) -> None:
        if not (1 <= self.priority <= 3):
            raise ValueError("priority must be 1..3")

    def is_due(self, when: Optional[datetime] = None) -> bool:
        when = when or datetime.now()
        return (
            (self.due_time is not None)
            and (when >= self.due_time)
            and (not self.completed)
        )

    def mark_complete(
        self, when: Optional[datetime] = None, by: Optional[str] = None
    ) -> None:
        self.completed = True
        self.completed_at = when or datetime.now()
        self.completed_by = by

    def reschedule(self, new_time: datetime) -> None:
        self.due_time = new_time


@dataclass
class Pet:
    id: str = field(default_factory=lambda: uuid4().hex)
    owner_id: str = ""
    name: str = ""
    species: str = "dog"
    birth_date: Optional[date] = None
    tasks: List[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Pet.name must not be empty")

    def add_task(self, task: Task) -> None:
        task.pet_id = self.id
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def age_years(self) -> Optional[int]:
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
        return not (
            self.end_time <= other.start_time or self.start_time >= other.end_time
        )


class Schedule:
    def __init__(self, owner_id: str, date_for: date):
        self.owner_id = owner_id
        self.date = date_for
        self.slots: List[ScheduleSlot] = []
        self.generated_at: Optional[datetime] = None

    def generate(self, tasks_pool: List[Task], day_start: time = time(8, 0)) -> None:
        """Greedy pack tasks into non-overlapping slots.

        - Tasks without a duration get a default of 10 minutes.
        - Tasks are ordered by priority (desc), then due_time.
        - Start at `day_start` and avoid overlaps by shifting later.
        """
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
        self.trigger = self.trigger + timedelta(minutes=minutes)


class User:
    def __init__(self, id: Optional[str], name: str, email: Optional[str] = None):
        self.id = id or uuid4().hex
        self.name = name
        self.email = email
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pet.owner_id = self.id
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        self.pets = [p for p in self.pets if p.id != pet_id]

    def get_tasks_for_date(self, target_date: date) -> List[Task]:
        tasks: List[Task] = []
        for pet in self.pets:
            for t in pet.tasks:
                if t.due_time and t.due_time.date() == target_date:
                    tasks.append(t)
        return tasks


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
