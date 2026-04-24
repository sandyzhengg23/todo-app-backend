from dataclasses import dataclass
from datetime import date
from enum import Enum


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass(frozen=True)
class User:
    id: int
    username: str
    password: str


@dataclass
class Task:
    id: int
    user_id: int
    title: str
    description: str
    priority: Priority
    due_date: date
    category: str
    completed: bool = False