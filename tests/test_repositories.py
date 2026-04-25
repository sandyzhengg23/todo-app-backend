import pytest
from datetime import date

from src.models import Priority, Task
from src.repositories import InMemoryUserRepository, InMemoryTaskRepository
from src.exceptions import TaskNotFoundError


#Happy path
def test_get_by_id_returns_user():
    # Arrange
    repo = InMemoryUserRepository()
    user = repo.add("sandy", "123")

    # Act
    result = repo.get_by_id(user.id)

    # Assert
    assert result.username == "sandy"


#Boundary / edge, Exception handling
def test_update_missing_task_raises_error():
    # Arrange
    repo = InMemoryTaskRepository()
    task = Task(999, 1, "Task", "", Priority.HIGH, date(2026, 4, 24), "School")

    # Act / Assert
    with pytest.raises(TaskNotFoundError):
        repo.update(task)


#Boundary / edge, Exception handling
def test_delete_missing_task_raises_error():
    # Arrange
    repo = InMemoryTaskRepository()

    # Act / Assert
    with pytest.raises(TaskNotFoundError):
        repo.delete(999)