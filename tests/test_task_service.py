import pytest
from datetime import date

from src.models import Priority
from src.repositories import InMemoryUserRepository, InMemoryTaskRepository
from src.services import AuthService, TaskService
from src.exceptions import InvalidTaskInputError, TaskNotFoundError, UnauthorizedTaskAccessError

class DummyReminder:
    def send(self, user, task):
        pass

def make_services():
    auth = AuthService(InMemoryUserRepository())
    service = TaskService(InMemoryTaskRepository(), DummyReminder())
    return auth, service

#Happy path
def test_create_task_adds_task():
    #Arrange
    auth, service = make_services()
    user = auth.sign_up("sandy", "sandy123")

    #Act 
    service.create_task(user, "Study", "mfml exam", Priority.HIGH, date(2026, 4, 24), "School")

    #Assert
    assert len(service.list_tasks(user)) == 1

#Happy Path
def test_gets_correct_task():
    #Arrange
    auth, service = make_services()
    user = auth.sign_up("sandy", "123")
    task = service.create_task(user, "Study", "formalexam", Priority.HIGH, date(2026, 4, 24), "School")

    # Act
    result = service.get_task(user, task.id)

    # Assert
    assert result.title == "Study"

#Happy path, Business logic
def test_delete_task():
    #Arrange
    auth, service = make_services()
    user = auth.sign_up("sandy", "123")
    task = service.create_task(user, "Task", "", Priority.HIGH, date(2026, 4, 24), "School")

    #Act
    service.delete_task(user, task.id)

    #Assert
    assert service.list_tasks(user) == []

#Happy path, Business logic
def test_mark_complete_true():
    #Arrange
    auth, service = make_services()
    user = auth.sign_up("sandy", "sandy123")
    task = service.create_task(user, "Task", "", Priority.HIGH, date(2026, 4, 24), "School")

    # Act
    result = service.mark_complete(user, task.id)

    # Assert
    assert result.completed == True

#Invalid input, Boundary / edge, Exception handling
def test_create_task_with_empty_title():
    #Arrange
    auth, service = make_services()
    user = auth.sign_up("sandy", "sandy123")

    #Act/Assert
    with pytest.raises(InvalidTaskInputError):
        service.create_task(user, "", "exam", Priority.HIGH, date(2026, 4, 24), "School")

#Boundary / edge, Exception handling
def test_get_missing_task_raises():
    # Arrange
    auth, service = make_services()
    user = auth.sign_up("sandy", "123")

    # Act/Assert
    with pytest.raises(TaskNotFoundError):
        service.get_task(user, 1)

    
#Business logic, Exception handling
def test_other_user_cannot_access_task():
    # Arrange
    auth, service = make_services()
    user1 = auth.sign_up("sandy", "123")
    user2 = auth.sign_up("alex", "456")
    task = service.create_task(user1, "Private", "", Priority.HIGH, date(2026, 4, 24), "School")

    # Act/Assert
    with pytest.raises(UnauthorizedTaskAccessError):
        service.get_task(user2, task.id)

#Happy path, Business logic
def test_mark_incomplete_sets_completed_false():
    #Arrange
    auth, service = make_services()
    user = auth.sign_up("sandy", "123")
    task = service.create_task(user, "Task", "", Priority.HIGH, date(2026, 4, 24), "School")
    service.mark_complete(user, task.id)

    #Act
    result = service.mark_incomplete(user, task.id)

    #Assert
    assert result.completed == False

#Invalid input, Boundary / edge, Exception handling
def test_missing_due_date_raises_error():
    #Arrange
    auth, service = make_services()
    user = auth.sign_up("sandy", "123")

    #Act / Assert
    with pytest.raises(InvalidTaskInputError):
        service.create_task(user, "Task", "", Priority.HIGH, None, "School")

#Invalid input, Boundary / edge, Exception handling
def test_empty_category_raises_error():
    #Arrange
    auth, service = make_services()
    user = auth.sign_up("sandy", "123")

    #Act/Assert
    with pytest.raises(InvalidTaskInputError):
        service.create_task(user, "Task", "", Priority.HIGH, date(2026, 4, 24), "")

#Invalid input, Boundary / edge, Exception handling
def test_create_task_with_none_user_raises_error():
    #Arrange
    _, service = make_services()

    # Act / Assert
    with pytest.raises(InvalidTaskInputError):
        service.create_task(None, "Task", "", Priority.HIGH, date(2026, 4, 24), "School")

#Happy path, Business logic
def test_update_task_changes_all_optional_fields():
    #Arrange
    auth, service = make_services()
    user = auth.sign_up("sandy", "123")
    task = service.create_task(user, "Old", "old", Priority.LOW, date(2026, 4, 24), "School")

    #Act
    updated = service.update_task(
        user,
        task.id,
        title="New",
        description="new",
        priority=Priority.HIGH,
        due_date=date(2026, 5, 1),
        category="Personal"
    )

    #Assert
    assert updated.title == "New"
    assert updated.description == "new"
    assert updated.priority == Priority.HIGH
    assert updated.due_date == date(2026, 5, 1)
    assert updated.category == "Personal"

#Boundary / edge, Business logic
def test_update_task_with_no_optional_fields_keeps_task_unchanged():
    #Arrange
    auth, service = make_services()
    user = auth.sign_up("sandy", "123")
    task = service.create_task(user, "Original", "old", Priority.LOW, date(2026, 4, 24), "School")

    #Act
    updated = service.update_task(user, task.id)

    #Assert
    assert updated.title == "Original"
    assert updated.description == "old"
    assert updated.priority == Priority.LOW
    assert updated.due_date == date(2026, 4, 24)
    assert updated.category == "School"
