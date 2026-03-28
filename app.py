import streamlit as st
from pawpal_system import User, Pet, Task, Schedule
from datetime import date, datetime, time as dt_time

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan", key="owner_name_main")
pet_name = st.text_input("Pet name", value="Mochi", key="pet_name_main")
species = st.selectbox("Species", ["dog", "cat", "other"], key="species_owner")

st.markdown("### Tasks")
st.caption("Add a pet and tasks; data is stored in `st.session_state.owner`.")

# Ensure owner exists in session state
if "owner" not in st.session_state:
    st.session_state.owner: User = User(None, owner_name)

col_owner1, col_owner2 = st.columns([3, 1])
with col_owner1:
    owner_name_input = st.text_input(
        "Owner name (create/update)",
        value=st.session_state.owner.name,
        key="owner_name_update",
    )
with col_owner2:
    if st.button("Create / Update Owner"):
        st.session_state.owner = User(None, owner_name_input)

st.write(f"Owner: {st.session_state.owner.name}")

st.markdown("#### Add Pet")
pet_col1, pet_col2 = st.columns([2, 1])
with pet_col1:
    pet_name = st.text_input("Pet name", value="Mochi", key="pet_name_selected")
with pet_col2:
    pet_species = st.selectbox("Species", ["dog", "cat", "other"], key="species_pet")

if st.button("Add pet"):
    pet = Pet(name=pet_name, species=pet_species)
    st.session_state.owner.add_pet(pet)

if st.session_state.owner.pets:
    pet_options = {p.name: p.id for p in st.session_state.owner.pets}
    selected_pet_name = st.selectbox("Select pet", list(pet_options.keys()))
    selected_pet = next(
        p for p in st.session_state.owner.pets if p.id == pet_options[selected_pet_name]
    )

    st.markdown("##### Add Task for selected pet")
    t_col1, t_col2, t_col3 = st.columns(3)
    with t_col1:
        task_title = st.text_input(
            "Task title", value="Feed breakfast", key="task_title"
        )
    with t_col2:
        duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=15
        )
    with t_col3:
        priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=1)

    # Optional desired date/time for the task (helps the scheduler)
    due_col1, due_col2 = st.columns([1, 1])
    with due_col1:
        due_date = st.date_input(
            "Desired date", value=date.today(), key="task_due_date"
        )
    with due_col2:
        due_time = st.time_input(
            "Desired time", value=datetime.now().time(), key="task_due_time"
        )

    priority_map = {"low": 1, "medium": 2, "high": 3}
    if st.button("Add task to pet"):
        # compose due_time from inputs
        desired_dt = datetime.combine(due_date, due_time)
        t = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority_map[priority_label],
            due_time=desired_dt,
        )
        selected_pet.add_task(t)

    # Display tasks per pet
    st.write(f"Tasks for {selected_pet.name}:")
    if selected_pet.tasks:
        # show tasks sorted by desired time (tasks without times are shown last)
        sorted_tasks = Task.sort_by_time(list(selected_pet.tasks))
        st.table(
            [
                {
                    "id": t.id,
                    "title": t.title,
                    "due_time": t.due_time.strftime("%Y-%m-%d %H:%M")
                    if t.due_time
                    else "(none)",
                    "duration_min": t.duration_minutes,
                    "priority": t.priority,
                    "completed": t.completed,
                }
                for t in sorted_tasks
            ]
        )
    else:
        st.info("No tasks for this pet yet.")
else:
    st.info("No pets yet. Add a pet to begin.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    # Gather today's tasks from owner and run Schedule
    owner: User = st.session_state.owner
    tasks_today = owner.get_tasks_for_date(date.today())
    sched = Schedule(owner.id, date.today())
    sched.generate(tasks_today)
    # Build lookups for nicer display and warnings
    task_lookup = {t.id: t for pet in owner.pets for t in pet.tasks}
    pet_lookup = {p.id: p for p in owner.pets}

    # Detect slot overlaps and desired-time conflicts
    slot_warnings = sched.detect_conflicts(
        task_lookup=task_lookup, pet_lookup=pet_lookup
    )
    desired_warnings = sched.detect_desired_time_conflicts(
        tasks_today, task_lookup=task_lookup, pet_lookup=pet_lookup
    )

    all_warnings = list(slot_warnings) + list(desired_warnings)

    if all_warnings:
        st.warning("Schedule generation produced warnings — please review:")
        for w in all_warnings:
            st.warning(w)
    else:
        st.success("No scheduling conflicts detected.")

    if sched.slots:
        st.write("Generated schedule:")
        st.table(
            [
                {
                    "task_id": s.task_id,
                    "task_title": task_lookup[s.task_id].title
                    if s.task_id in task_lookup
                    else s.task_id,
                    "pet": pet_lookup[task_lookup[s.task_id].pet_id].name
                    if s.task_id in task_lookup
                    and task_lookup[s.task_id].pet_id in pet_lookup
                    else "-",
                    "start": s.start_time.strftime("%Y-%m-%d %H:%M"),
                    "end": s.end_time.strftime("%Y-%m-%d %H:%M"),
                }
                for s in sched.slots
            ]
        )
    else:
        st.info("No tasks scheduled for today.")
