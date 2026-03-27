"""Minimal PawPal system skeleton.

- Keep scope small: `User`, `Pet`, `Task`, `Schedule`, `Reminder`.
- Use `dataclasses` for `Task` and `Pet` as requested.

This file is intentionally lightweight and suitable for the small app.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import List, Optional


@dataclass
class Task:
    id: int
    pet_id: int
    title: str
    due_time: Optional[datetime] = None
    priority: int = 2  # 1=low,2=medium,3=high
    completed: bool = False

    def is_due(self, when: Optional[datetime] = None) -> bool:
        when = when or datetime.now()
        return (
            (self.due_time is not None)
            and (when >= self.due_time)
            and (not self.completed)
        )

    def mark_complete(self, when: Optional[datetime] = None) -> None:
        self.completed = True

    def reschedule(self, new_time: datetime) -> None:
        self.due_time = new_time


@dataclass
class Pet:
    id: int
    owner_id: int
    name: str
    species: str = "dog"
    birth_date: Optional[date] = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task_id: int) -> None:
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


class User:
    def __init__(self, id: int, name: str, email: Optional[str] = None):
        self.id = id
        self.name = name
        self.email = email
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, pet_id: int) -> None:
        self.pets = [p for p in self.pets if p.id != pet_id]

    def get_tasks_for_date(self, target_date: date) -> List[Task]:
        tasks: List[Task] = []
        for pet in self.pets:
            for t in pet.tasks:
                if t.due_time and t.due_time.date() == target_date:
                    tasks.append(t)
        return tasks


class Schedule:
    def __init__(self, owner_id: int, date_for: date):
        self.owner_id = owner_id
        self.date = date_for
        self.tasks: List[Task] = []
        self.generated_at: Optional[datetime] = None

    def generate(self, tasks_pool: List[Task]) -> None:
        # minimal: include tasks due on the schedule date, sort by priority desc
        self.tasks = sorted(
            [t for t in tasks_pool if t.due_time and t.due_time.date() == self.date],
            key=lambda t: t.priority,
            reverse=True,
        )
        self.generated_at = datetime.now()


class Reminder:
    def __init__(self, id: int, user_id: int, message: str, trigger: datetime):
        self.id = id
        self.user_id = user_id
        self.message = message
        self.trigger = trigger

    def snooze(self, minutes: int = 10) -> None:
        self.trigger = self.trigger + timedelta(minutes=minutes)


# Small usage example (kept minimal for the project)
if __name__ == "__main__":
    user = User(1, "Alex")
    pet = Pet(id=1, owner_id=user.id, name="Rex", species="dog")
    task = Task(id=1, pet_id=pet.id, title="Feed breakfast", due_time=datetime.now())
    pet.add_task(task)
    user.add_pet(pet)

    today_schedule = Schedule(owner_id=user.id, date_for=date.today())
    today_schedule.generate(user.get_tasks_for_date(date.today()))
    print("Schedule tasks:", [t.title for t in today_schedule.tasks])
