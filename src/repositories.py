from src.models import User, Task
from src.exceptions import TaskNotFoundError


class InMemoryUserRepository:
    def __init__(self):
        self._users_by_id = {}
        self._next_id = 1

    def add(self, username, password):
        user = User(
            id=self._next_id,
            username=username,
            password=password
        )

        self._users_by_id[user.id] = user
        self._next_id += 1

        return user

    def find_by_username(self, username):
        for user in self._users_by_id.values():
            if user.username == username:
                return user

        return None

    def get_by_id(self, user_id):
        return self._users_by_id.get(user_id)


class InMemoryTaskRepository:
    def __init__(self):
        self._tasks_by_id = {}
        self._next_id = 1

    def add(self, user_id, title, description, priority, due_date, category):
        task = Task(
            id=self._next_id,
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            category=category,
            completed=False
        )

        self._tasks_by_id[task.id] = task
        self._next_id += 1

        return task

    def get(self, task_id):
        task = self._tasks_by_id.get(task_id)

        if task is None:
            raise TaskNotFoundError(f"Task with id {task_id} was not found.")

        return task

    def list_by_user(self, user_id):
        return [
            task
            for task in self._tasks_by_id.values()
            if task.user_id == user_id
        ]

    def update(self, task):
        if task.id not in self._tasks_by_id:
            raise TaskNotFoundError(f"Task with id {task.id} was not found.")

        self._tasks_by_id[task.id] = task

        return task

    def delete(self, task_id):
        if task_id not in self._tasks_by_id:
            raise TaskNotFoundError(f"Task with id {task_id} was not found.")

        del self._tasks_by_id[task_id]