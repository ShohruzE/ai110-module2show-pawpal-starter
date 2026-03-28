from datetime import date, datetime
from pawpal_system import Task, Pet, User, Schedule

# --- Setup ---
owner = User(id=None, name="Alex")

rex = Pet(name="Rex", species="dog", birth_date=date(2020, 6, 15))
luna = Pet(name="Luna", species="cat", birth_date=date(2022, 3, 1))

today = date.today()

rex.add_task(
    Task(
        title="Morning walk",
        due_time=datetime.combine(today, datetime.strptime("07:30", "%H:%M").time()),
        duration_minutes=30,
        priority=3,
        frequency="daily",
    )
)
rex.add_task(
    Task(
        title="Feed breakfast",
        due_time=datetime.combine(today, datetime.strptime("08:00", "%H:%M").time()),
        duration_minutes=10,
        priority=3,
        frequency="daily",
    )
)
luna.add_task(
    Task(
        title="Vet checkup",
        due_time=datetime.combine(today, datetime.strptime("11:00", "%H:%M").time()),
        duration_minutes=45,
        priority=2,
        frequency="once",
    )
)

# Add tasks out of order to validate sorting/filtering later
rex.add_task(
    Task(
        title="Evening play",
        due_time=datetime.combine(today, datetime.strptime("19:00", "%H:%M").time()),
        duration_minutes=20,
        priority=1,
    )
)
luna.add_task(
    Task(
        title="Lunch treat",
        due_time=datetime.combine(today, datetime.strptime("12:30", "%H:%M").time()),
        duration_minutes=5,
        priority=2,
    )
)
# Add a task that is due earlier but appended last (out-of-order addition)
rex.add_task(
    Task(
        title="Quick brush",
        due_time=datetime.combine(today, datetime.strptime("06:50", "%H:%M").time()),
        duration_minutes=10,
        priority=2,
    )
)

owner.add_pet(rex)
owner.add_pet(luna)

# --- Generate schedule ---
# Add two tasks at the same time to demonstrate conflict detection
conflict_time = datetime.combine(today, datetime.strptime("09:00", "%H:%M").time())
rex.add_task(
    Task(title="Call vet", due_time=conflict_time, duration_minutes=30, priority=2)
)
luna.add_task(
    Task(title="Medication", due_time=conflict_time, duration_minutes=15, priority=2)
)

all_tasks = owner.get_tasks_for_date(today)
print("\n-- Unsorted tasks (ids and due_times in addition order) --")
for t in all_tasks:
    print(
        f"{t.title}: {t.due_time.time() if t.due_time else 'no-time'} (completed={t.completed})"
    )

# Demonstrate Task.sort_by_time
sorted_tasks = Task.sort_by_time(all_tasks)
print("\n-- Tasks sorted by time --")
for t in sorted_tasks:
    print(f"{t.due_time.time() if t.due_time else 'no-time'}  {t.title} [{t.pet_id}]")

# Demonstrate filtering: mark one task complete and filter
if sorted_tasks:
    # mark the first (earliest) task complete for demo
    new_task = sorted_tasks[0].mark_complete(by=owner.name, owner_pets=owner.pets)
    if new_task:
        print(
            f"Created recurring task for next occurrence: {new_task.title} at {new_task.due_time}"
        )

print("\n-- Tasks for pet 'Luna' --")
for t in owner.filter_tasks(pet_name="Luna"):
    print(
        f"{t.title} at {t.due_time.time() if t.due_time else 'no-time'} (completed={t.completed})"
    )

print("\n-- Completed tasks --")
for t in owner.filter_tasks(completed=True):
    print(f"{t.title} ({t.completed_at}) by {t.completed_by}")
schedule = Schedule(owner_id=owner.id, date_for=today)
pet_lookup = {pet.id: pet for pet in owner.pets}
task_lookup = {task.id: task for pet in owner.pets for task in pet.tasks}

# Detect desired-time conflicts before generating the schedule
dt_warnings = schedule.detect_desired_time_conflicts(
    all_tasks, task_lookup=task_lookup, pet_lookup=pet_lookup
)
if dt_warnings:
    print("\nDesired-time Schedule Warnings:")
    for w in dt_warnings:
        print("WARNING:", w)

# Now generate the actual schedule (generator may shift tasks to avoid overlaps)
schedule.generate(all_tasks)

# --- Print Today's Schedule ---
print(f"=== Today's Schedule for {owner.name} ({today}) ===\n")

# Detect and print schedule slot overlaps (non-fatal warnings)
warnings = schedule.detect_conflicts(task_lookup=task_lookup, pet_lookup=pet_lookup)
if warnings:
    print("\nSchedule Slot Warnings:")
    for w in warnings:
        print("WARNING:", w)
else:
    print("\nNo schedule slot conflicts detected.")

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
