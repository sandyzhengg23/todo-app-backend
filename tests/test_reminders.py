from datetime import date
from unittest.mock import Mock
import pytest

from src.models import Priority, User, Task
from src.repositories import InMemoryUserRepository, InMemoryTaskRepository
from src.services import AuthService, TaskService
from src.exceptions import UnauthorizedTaskAccessError
from src.reminder import ReminderSender, ConsoleReminderSender


class SpyReminder:
    def __init__(self):
        self.calls = []

    def send(self, user, task):
        self.calls.append(task.title)


def make_services(reminder):
    auth = AuthService(InMemoryUserRepository())
    service = TaskService(InMemoryTaskRepository(), reminder)
    return auth, service


#Happy path, Business logic
def test_reminder_is_sent():
    #Arrange
    spy = SpyReminder()
    auth, service = make_services(spy)
    user = auth.sign_up("sandy", "123")
    task = service.create_task(user, "Study", "", Priority.HIGH, date(2026, 4, 24), "School")

    #Act
    service.set_reminder(user, task.id)

    #Assert
    assert spy.calls == ["Study"]

#Invalid input, Exception handling, Business logic
def test_reminder_wrong_user_raises():
    #Arrange
    spy = SpyReminder()
    auth, service = make_services(spy)
    user1 = auth.sign_up("sandy", "123")
    user2 = auth.sign_up("alex", "456")
    task = service.create_task(user1, "Private", "", Priority.HIGH, date(2026, 4, 24), "School")

    #Act/Assert
    with pytest.raises(UnauthorizedTaskAccessError):
        service.set_reminder(user2, task.id)

#Business logic
def test_reminder_calls_mock():
    #Arrange
    mock = Mock()
    auth, service = make_services(mock)
    user = auth.sign_up("sandy", "123")
    task = service.create_task(user, "Study", "", Priority.HIGH, date(2026, 4, 24), "School")

    #Act
    service.set_reminder(user, task.id)

    #Assert
    mock.send.assert_called_once()

#Exception handling
def test_base_reminder_sender_raises_not_implemented():
    #Arrange
    sender = ReminderSender()
    user = User(1, "sandy", "123")
    task = Task(1, 1, "Study", "", Priority.HIGH, date(2026, 4, 24), "School")

    #Act/Assert
    with pytest.raises(NotImplementedError):
        sender.send(user, task)

#Happy Path
def test_console_reminder_sender_prints_message(capsys):
    #Arrange
    sender = ConsoleReminderSender()
    user = User(1, "sandy", "123")
    task = Task(1, 1, "Study", "", Priority.HIGH, date(2026, 4, 24), "School")

    #Act
    sender.send(user, task)

    #Assert
    captured = capsys.readouterr()
    assert captured.out == "Reminder sent to sandy: Study\n"