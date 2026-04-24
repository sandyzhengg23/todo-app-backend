from datetime import date
import pytest

from src.models import Priority
from src.repositories import InMemoryUserRepository, InMemoryTaskRepository
from src.services import AuthService, TaskService
from src.exceptions import InvalidTaskInputError


class DummyReminder:
    def send(self, user, task):
        pass


def make_services():
    auth = AuthService(InMemoryUserRepository())
    service = TaskService(InMemoryTaskRepository(), DummyReminder())
    return auth, service

#Business logic, Equivalence classes
def test_sort_by_priority():
    #Arrange
    auth, service = make_services()
    user = auth.sign_up("sandy", "123")

    service.create_task(user, "low_task", "", Priority.LOW, date(2026, 4, 24), "l")
    service.create_task(user, "high_task", "", Priority.HIGH, date(2026, 4, 24), "h")

    #Act
    tasks = service.sort_tasks(user, "priority")

    #Assert
    assert tasks[0].priority == Priority.HIGH

#Invalid input, Exception handling, Boundary / edge
def test_sort_invalid_field():
    #Arrange 
    auth, service = make_services()
    user = auth.sign_up("sandy", "123")

    #Act/Assert
    with pytest.raises(InvalidTaskInputError):
        service.sort_tasks(user, "invalid")

#Happy path, Business logic, Equivalence classes
def test_filter_by_category():
    #Arrange
    auth, service = make_services()
    user = auth.sign_up("sandy", "123")
    
    service.create_task(user, "Study", "", Priority.HIGH, date(2026, 4, 24), "School")
    service.create_task(user, "Homework", "", Priority.HIGH, date(2026, 4, 24), "School")
    service.create_task(user, "Gym", "", Priority.LOW, date(2026, 4, 24), "Health")

    #Act
    tasks = service.filter_tasks(user, category="School")

    #Assert
    assert len(tasks) == 2

#Happy path, Business logic, Equivalence classes
def test_filter_by_keyword():
    #Arrange
    auth, service = make_services()
    user = auth.sign_up("sandy", "123")

    service.create_task(user, "Study pytest", "", Priority.HIGH, date(2026, 4, 24), "School")
    service.create_task(user, "Study for final exams", "", Priority.HIGH, date(2026, 4, 24), "School")


    #Act
    tasks = service.filter_tasks(user, keyword="Study")

    #Assert
    assert len(tasks) == 2


#Happy path, Business logic
def test_sort_by_due_date_returns_earliest_first():
    # Arrange
    auth, service = make_services()
    user = auth.sign_up("sandy", "123")
    service.create_task(user, "Later", "", Priority.HIGH, date(2026, 5, 1), "School")
    service.create_task(user, "Earlier", "", Priority.HIGH, date(2026, 4, 1), "School")

    # Act
    tasks = service.sort_tasks(user, "due_date")

    # Assert
    assert tasks[0].title == "Earlier"

#Happy path, Business logic
def test_sort_by_completed_returns_incomplete_first():
    #Arrange
    auth, service = make_services()
    user = auth.sign_up("sandy", "123")
    task = service.create_task(user, "Done", "", Priority.HIGH, date(2026, 4, 24), "School")
    service.create_task(user, "Not done", "", Priority.HIGH, date(2026, 4, 24), "School")
    service.mark_complete(user, task.id)

    #Act
    tasks = service.sort_tasks(user, "completed")

    #Assert
    assert tasks[0].title == "Not done"

#Boundary / edge, Business logic
def test_filter_returns_empty_list_when_no_match():
    #Arrange
    auth, service = make_services()
    user = auth.sign_up("sandy", "123")
    service.create_task(user, "Study", "", Priority.HIGH, date(2026, 4, 24), "School")

    #Act
    tasks = service.filter_tasks(user, keyword="missing")

    #Assert
    assert tasks == []