"""This module provides the Kiamov To-Do model-controller."""

from typing import Any, Dict, NamedTuple, List, Literal
from pathlib import Path
from ktodo.database import DatabaseHandler
from datetime import datetime
from ktodo import DB_READ_ERROR, ID_ERROR


class CurrentTodo(NamedTuple):
    todo: Dict[str, Any]
    error: int


class Todoer:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)

    def remove_all(self) -> CurrentTodo:
        """Remove all to-dos from the database."""
        write = self._db_handler.write_todos([])
        return CurrentTodo({}, write.error)

    def remove(self, todo_id: int) -> CurrentTodo:
        """Remove a to-do from the database using its id or index."""
        read = self._db_handler.read_todos()
        if todo_id <= 0:
            return CurrentTodo({}, ID_ERROR)
        if read.error:
            return CurrentTodo({}, read.error)
        try:
            todo = read.todo_list.pop(todo_id - 1)
        except IndexError:
            return CurrentTodo({}, ID_ERROR)
        write = self._db_handler.write_todos(read.todo_list)
        return CurrentTodo(todo, write.error)

    def set_status(self, todo_id: int, status: Literal["done", "todo", "in-progress"] = "todo") -> CurrentTodo:
        """Set a to-do status."""
        read = self._db_handler.read_todos()
        if read.error:
            return CurrentTodo({}, read.error)
        try:
            todo = read.todo_list[todo_id - 1]
        except IndexError:
            return CurrentTodo({}, ID_ERROR)
        todo["Status"] = status
        todo["updatedAt"] = (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        write = self._db_handler.write_todos(read.todo_list)
        return CurrentTodo(todo, write.error)

    def update(self, todo_id: int, new_description: str) -> CurrentTodo:
        """Set a new description."""
        if not new_description.endswith("."):
            new_description += "."
        read = self._db_handler.read_todos()

        if read.error:
            return CurrentTodo({}, read.error)
        try:
            todo = read.todo_list[todo_id - 1]
        except IndexError:
            return CurrentTodo({}, ID_ERROR)
        todo["Description"] = new_description
        todo["updatedAt"] = (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        write = self._db_handler.write_todos(read.todo_list)
        return CurrentTodo(todo, write.error)

    def get_todo_list(self, status: Literal["done", "todo", "in-progress", "all"] = "all") -> List[Dict[str, Any]]:
        """Return the current to-do list."""
        read = self._db_handler.read_todos()

        new_list_todos = []
        for item in read.todo_list:
            match status:
                case "done":
                    if item["Status"] == "done":
                        new_list_todos.append(item)
                case "in-progress":
                    if item["Status"] == "in-progress":
                        new_list_todos.append(item)
                case "todo":
                    if item["Status"] == "todo":
                        new_list_todos.append(item)
                case "all":
                    new_list_todos.append(item)
        return new_list_todos

    def add(self, description: str, status: Literal["done", "todo", "in-progress"] = "todo", priority: Literal["1", "2", "3"] = "2") -> CurrentTodo:
        """Add a new to-do to the database."""
        if not description.endswith("."):
            description += "."

        todo = {
            "Description": description,
            "Priority": priority,
            "Status": status,
            "CreatedAt": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
            "UpdatedAt": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        }

        read = self._db_handler.read_todos()
        if read.error == DB_READ_ERROR:
            return CurrentTodo(todo, read.error)

        read.todo_list.append(todo)
        write = self._db_handler.write_todos(read.todo_list)
        return CurrentTodo(todo, write.error)
