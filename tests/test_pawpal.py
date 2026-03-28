from pawpal_system import Task, Pet


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
