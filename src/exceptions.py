class TodoError(Exception):
    """Base exception for the to-do app."""


class UserAlreadyExistsError(TodoError):
    """Raised when a username is already taken."""


class InvalidCredentialsError(TodoError):
    """Raised when login credentials are invalid."""


class InvalidTaskInputError(TodoError):
    """Raised when task input is invalid."""


class TaskNotFoundError(TodoError):
    """Raised when a task does not exist."""


class UnauthorizedTaskAccessError(TodoError):
    """Raised when a user tries to access another user's task."""