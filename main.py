from datetime import date, datetime
from pawpal_system import Task, Pet, User, Schedule

# --- Setup ---
owner = User(id=None, name="Alex")

rex = Pet(name="Rex", species="dog", birth_date=date(2020, 6, 15))
luna = Pet(name="Luna", species="cat", birth_date=date(2022, 3, 1))

today = date.today()

rex.add_task(Task(
    title="Morning walk",
    due_time=datetime.combine(today, datetime.strptime("07:30", "%H:%M").time()),
    duration_minutes=30,
    priority=3,
    frequency="daily",
))
rex.add_task(Task(
    title="Feed breakfast",
    due_time=datetime.combine(today, datetime.strptime("08:00", "%H:%M").time()),
    duration_minutes=10,
    priority=3,
    frequency="daily",
))
luna.add_task(Task(
    title="Vet checkup",
    due_time=datetime.combine(today, datetime.strptime("11:00", "%H:%M").time()),
    duration_minutes=45,
    priority=2,
    frequency="once",
))

owner.add_pet(rex)
owner.add_pet(luna)

# --- Generate schedule ---
all_tasks = owner.get_tasks_for_date(today)
schedule = Schedule(owner_id=owner.id, date_for=today)
schedule.generate(all_tasks)

# --- Print Today's Schedule ---
print(f"=== Today's Schedule for {owner.name} ({today}) ===\n")

pet_lookup = {pet.id: pet for pet in owner.pets}
task_lookup = {task.id: task for pet in owner.pets for task in pet.tasks}

for slot in schedule.slots:
    task = task_lookup[slot.task_id]
    pet = pet_lookup[task.pet_id]
    status = "Done" if task.completed else "Pending"
    print(
        f"  {slot.start_time.strftime('%H:%M')} - {slot.end_time.strftime('%H:%M')}"
        f"  [{pet.name}]  {task.title}"
        f"  (priority={task.priority}, freq={task.frequency}, status={status})"
    )

print("\nTotal tasks scheduled:", len(schedule.slots))
