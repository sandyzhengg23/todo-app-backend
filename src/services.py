from src.models import Priority
from src.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InvalidTaskInputError,
    UnauthorizedTaskAccessError,
)


class AuthService:
    def __init__(self, user_repository):
        self._user_repository = user_repository

    def sign_up(self, username, password):
        self._validate_username(username)
        self._validate_password(password)

        existing_user = self._user_repository.find_by_username(username)

        if existing_user is not None:
            raise UserAlreadyExistsError(f"Username '{username}' already exists.")

        return self._user_repository.add(username, password)

    def login(self, username, password):
        user = self._user_repository.find_by_username(username)

        if user is None:
            raise InvalidCredentialsError("Invalid username or password.")

        if user.password != password:
            raise InvalidCredentialsError("Invalid username or password.")

        return user

    def _validate_username(self, username):
        if username is None or username.strip() == "":
            raise InvalidCredentialsError("Username cannot be empty.")

    def _validate_password(self, password):
        if password is None or password.strip() == "":
            raise InvalidCredentialsError("Password cannot be empty.")


class TaskService:
    def __init__(self, task_repository, reminder_sender):
        self._task_repository = task_repository
        self._reminder_sender = reminder_sender

    def create_task(
        self,
        user,
        title,
        description,
        priority,
        due_date,
        category
    ):
        self._validate_user(user)
        self._validate_task_input(title, priority, due_date, category)

        return self._task_repository.add(
            user_id=user.id,
            title=title.strip(),
            description=description or "",
            priority=priority,
            due_date=due_date,
            category=category.strip()
        )

    def get_task(self, user, task_id):
        self._validate_user(user)

        task = self._task_repository.get(task_id)
        self._authorize(user, task)

        return task

    def list_tasks(self, user):
        self._validate_user(user)

        return self._task_repository.list_by_user(user.id)

    def update_task(
        self,
        user,
        task_id,
        title=None,
        description=None,
        priority=None,
        due_date=None,
        category=None
    ):
        task = self.get_task(user, task_id)

        if title is not None:
            if title.strip() == "":
                raise InvalidTaskInputError("Title cannot be empty.")
            task.title = title.strip()

        if description is not None:
            task.description = description

        if priority is not None:
            self._validate_priority(priority)
            task.priority = priority

        if due_date is not None:
            task.due_date = due_date

        if category is not None:
            if category.strip() == "":
                raise InvalidTaskInputError("Category cannot be empty.")
            task.category = category.strip()

        return self._task_repository.update(task)

    def delete_task(self, user, task_id):
        task = self.get_task(user, task_id)

        self._task_repository.delete(task.id)

    def mark_complete(self, user, task_id):
        task = self.get_task(user, task_id)

        task.completed = True

        return self._task_repository.update(task)

    def mark_incomplete(self, user, task_id):
        task = self.get_task(user, task_id)

        task.completed = False

        return self._task_repository.update(task)

    def sort_tasks(self, user, sort_by):
        tasks = self.list_tasks(user)

        if sort_by == "priority":
            return sorted(tasks, key=lambda task: task.priority.value, reverse=True)

        if sort_by == "due_date":
            return sorted(tasks, key=lambda task: task.due_date)

        if sort_by == "completed":
            return sorted(tasks, key=lambda task: task.completed)

        raise InvalidTaskInputError(f"Unsupported sort field: {sort_by}")

    def filter_tasks(self, user, category=None, keyword=None):
        tasks = self.list_tasks(user)

        if category is not None:
            tasks = [
                task
                for task in tasks
                if task.category.lower() == category.lower()
            ]

        if keyword is not None:
            keyword_lower = keyword.lower()

            tasks = [
                task
                for task in tasks
                if keyword_lower in task.title.lower()
                or keyword_lower in task.description.lower()
            ]

        return tasks

    def set_reminder(self, user, task_id):
        task = self.get_task(user, task_id)

        self._reminder_sender.send(user, task)

        return task

    def _authorize(self, user, task):
        if task.user_id != user.id:
            raise UnauthorizedTaskAccessError(
                "User is not allowed to access this task."
            )

    def _validate_user(self, user):
        if user is None:
            raise InvalidTaskInputError("User is required.")

    def _validate_task_input(self, title, priority, due_date, category):
        if title is None or title.strip() == "":
            raise InvalidTaskInputError("Title cannot be empty.")

        self._validate_priority(priority)

        if due_date is None:
            raise InvalidTaskInputError("Due date is required.")

        if category is None or category.strip() == "":
            raise InvalidTaskInputError("Category cannot be empty.")

    def _validate_priority(self, priority):
        if not isinstance(priority, Priority):
            raise InvalidTaskInputError("Priority must be LOW, MEDIUM, or HIGH.")