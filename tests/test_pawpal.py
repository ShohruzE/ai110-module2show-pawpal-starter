from datetime import datetime, timedelta, date

from pawpal_system import Task, Pet, Schedule


def test_mark_complete_changes_status():
    task = Task(title="Feed breakfast")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Rex")
    assert len(pet.tasks) == 0

    pet.add_task(Task(title="Morning walk"))
    pet.add_task(Task(title="Evening walk"))

    assert len(pet.tasks) == 2


def test_sort_by_time_orders_chronologically():
    t1 = Task(title="A", due_time=datetime(2026, 3, 28, 9, 0))
    t2 = Task(title="B", due_time=datetime(2026, 3, 28, 8, 0))
    t3 = Task(title="C")  # no due_time

    tasks = [t1, t2, t3]
    sorted_tasks = Task.sort_by_time(tasks)

    assert sorted_tasks[0] is t2
    assert sorted_tasks[1] is t1
    assert sorted_tasks[-1] is t3


def test_mark_complete_daily_creates_next_day_task():
    pet = Pet(name="Luna")
    t = Task(title="Walk", due_time=datetime(2026, 3, 28, 7, 0), frequency="daily")
    pet.add_task(t)

    when = datetime(2026, 3, 28, 7, 5)
    new_task = t.mark_complete(when=when, by="owner", owner_pets=[pet])

    assert new_task is not None
    # new task should be scheduled for the following day at the original time
    assert new_task.due_time == datetime(2026, 3, 29, 7, 0)
    assert new_task in pet.tasks


def test_detect_desired_time_conflict_flags_duplicate_times():
    pet = Pet(name="Milo")
    t1 = Task(title="Feed", due_time=datetime(2026, 3, 28, 9, 0))
    t2 = Task(title="Groom", due_time=datetime(2026, 3, 28, 9, 0))
    pet.add_task(t1)
    pet.add_task(t2)

    tasks_pool = [t1, t2]
    schedule = Schedule(owner_id="u", date_for=date(2026, 3, 28))

    task_lookup = {t1.id: t1, t2.id: t2}
    pet_lookup = {pet.id: pet}

    warnings = schedule.detect_desired_time_conflicts(
        tasks_pool, task_lookup=task_lookup, pet_lookup=pet_lookup
    )

    assert len(warnings) >= 1
    assert "Desired-time conflict" in warnings[0] or "multiple tasks" in warnings[0]
