"""This module provides the Kiamov To-Do CLI."""

from argparse import ArgumentParser
from typing import List, Callable, Literal
from ktodo import (
    ERRORS, __app_name__, __version__, __description__, config, database, ktodo
)
from pathlib import Path
import sys


def main() -> None:
    supported_queries: dict[str, dict] = get_supported_queries()

    querie, args = get_querie(supported_queries)

    try:
        querie(**args)
    except KeyError:
        sys.exit("No task found with the provided ID")


def init(
    db_path: str
) -> None:
    """Initialize the to-do database."""
    app_init_error = config.init_app(db_path)
    if app_init_error:
        print(f'Creating config file failed with "{ERRORS[app_init_error]}"')
        return
    db_init_error = database.init_database(Path(db_path))
    if db_init_error:
        print(f'Creating database failed with "{ERRORS[db_init_error]}"')
        return
    else:
        print(f"The to-do database is {db_path}")


def get_todoer() -> ktodo.Todoer:
    if config.CONFIG_FILE_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH)
    else:
        print('Config file not found. Please, run "ktodo init"')
        return
    if db_path.exists():
        return ktodo.Todoer(db_path)
    else:
        print('Database not found. Please, run "ktodo init"')
        return


def get_supported_queries() -> dict[str, dict]:
    return {
        "init": {
            "target": init,
            "help": "Initialize the to-do database.",
            "args": [
                {
                    "name_or_flags": ["--db-path", "-db"],
                    "default": database.DEFAULT_DB_FILE_PATH,
                    "help": "to-do database location?"
                }
            ],
        },
        "add": {
            "target": add,
            "help": "Add a new to-do with a DESCRIPTION.",
            "args": [
                {
                    "name_or_flags": ["description"],
                    "help": "Description of the task"
                },
                {
                    "name_or_flags": ["--priority", "-p"],
                    "help": "Priority of the task (default is '2')",
                    "default": "2",
                    "choices": ["1", "2", "3"],
                },
                {
                    "name_or_flags": ["--status", "-s"],
                    "help": "Status of the task (default is 'todo')",
                    "default": "todo",
                    "choices": ["todo", "in-progress", "done"],
                },
            ],
        },
        "update": {
            "target": update,
            "help": "Update a to-do using its ID.",
            "args": [
                {
                    "name_or_flags": ["id"],
                    "type": int,
                    "help": "ID of the task you want to update"
                },
                {
                    "name_or_flags": ["new_description"],
                    "help": "New description for the task"
                }
            ],
        },
        "remove": {
            "target": remove,
            "help": "Remove a to-do using its ID.",
            "args": [
                {
                    "name_or_flags": ["id"],
                    "type": int,
                    "help": "ID of the task you want to delete",
                },
                {
                    "name_or_flags": ["--force", "-f"],
                    "action": "store_true",
                    "help": "Force deletion without confirmat",
                }
            ],
        },
        "remove-all": {
            "target": remove_all,
            "help": "Remove all to-dos.",
            "args": [
                {
                    "name_or_flags": ["--force", "-f"],
                    "action": "store_true",
                    "help": "Force deletion without confirmat",
                }
            ],
        },
        "list": {
            "target": list_all,
            "help": "List all to-dos.",
            "args": [
                {
                    "name_or_flags": ["--status", "-s"],
                    "help": "Filter tasks by status (default is 'all')",
                    "choices": ["all", "done", "todo", "in-progress"],
                    "type": str.lower,
                    "default": "all",
                }
            ],
        },
        "set-status": {
            "target": set_status,
            "help": "Сhanges status using its ID.",
            "args": [
                {
                    "name_or_flags": ["id"],
                    "type": int,
                    "help": "ID of the task you want to change"
                },
                {
                    "name_or_flags": ["status"],
                    "help": "New status for the selected task",
                    "choices": ["done", "todo", "in-progress"],
                    "type": str.lower,
                }
            ],
        },
    }


def add(description: str, status: str = "todo", priority: str = "2") -> None:
    """Add a new to-do with a DESCRIPTION."""
    todoer = get_todoer()
    if todoer == None:
        return
    todo, error = todoer.add(description, status, priority)
    if error:
        print(f'Adding to-do failed with "{ERRORS[error]}"')
        return
    else:
        todo_list = todoer.get_todo_list()
        print(
            f"""to-do: "{todo['Description']}" was added """
            f"""with priority: {priority} (ID: {len(todo_list)})"""
        )


def update(id: int, new_description: str) -> None:
    """Update a to-do using its ID."""
    todoer = get_todoer()
    if todoer == None:
        return
    todo, error = todoer.update(id, new_description)
    if error:
        print(f'Updating to-do # "{id}" failed with "{ERRORS[error]}"')
        return
    else:
        print(f"""to-do # {id} "{todo['Description']}" updated!""")


def list_all(status: Literal["all", "done", "todo", "in-progress"] = "all",) -> None:
    """List to-dos."""
    todoer = get_todoer()
    if todoer == None:
        return
    todo_list = todoer.get_todo_list(status=status)
    if len(todo_list) == 0:
        print("There are no tasks in the to-do list yet")
        return
    print("\nto-do list:\n")
    columns = (
        "ID.  ",
        "| Priority ",
        "| Status      ",
        "| CreatedAt            ",
        "| UpdatedAt            ",
        "| Description   ",
    )
    headers = "".join(columns)
    print(headers)
    print("-" * len(headers))
    for id, todo in enumerate(todo_list, 1):
        desc, priority, status, createdAt, updatedAt = todo.values()
        print(
            f"{id}{(len(columns[0]) - len(str(id))) * ' '}"
            f"| {priority}{(len(columns[1]) - len(str(priority)) - 2) * ' '}"
            f"| {status}{(len(columns[2]) - len(str(status)) - 2) * ' '}"
            f"| {createdAt}{(len(columns[3]) - len(str(createdAt)) - 2) * ' '}"
            f"| {updatedAt}{(len(columns[4]) - len(str(updatedAt)) - 2) * ' '}"
            f"| {desc}"
        )
    print("-" * len(headers) + "\n")


def set_status(id: int, status: Literal["done", "todo", "in-progress"] = "todo") -> None:
    """Сhanges status using its ID."""
    todoer = get_todoer()
    if todoer == None:
        return
    todo, error = todoer.set_status(id, status)
    if error:
        print(f'Change to-do # "{id}" failed with "{ERRORS[error]}"')
        return
    else:
        print(f"""to-do # {id} "{todo['Description']}" changed!""")


def remove(
    id: int,
    force: bool
) -> None:
    """Remove a to-do using its ID."""
    todoer = get_todoer()
    if todoer == None:
        return

    def _remove():
        todo, error = todoer.remove(id)
        if error:
            print(f'Removing to-do # {id} failed with "{ERRORS[error]}"')
            return
        else:
            print(f"to-do # {id}: '{todo["Description"]}' was removed")

    if force:
        _remove()
    else:
        todo_list = todoer.get_todo_list()
        try:
            todo = todo_list[id - 1]
        except IndexError:
            print("Invalid TODO_ID")
            return

        delete = input(
            f"Delete to-do # {id}: {todo['Description']}? [Y/N]? ").lower()

        if delete == "y":
            _remove()
        else:
            print("Operation canceled")


def remove_all(
    force: bool
) -> None:
    """Remove all to-dos."""
    todoer = get_todoer()
    if todoer == None:
        return
    if force:
        error = todoer.remove_all().error
        if error:
            print(f'Removing to-dos failed with "{ERRORS[error]}"')
            return
        else:
            print("All to-dos were removed")
    else:
        print("Operation canceled")


def get_querie(supported_queries: dict[str, dict]) -> tuple[Callable, dict]:
    parser: ArgumentParser = ArgumentParser(
        description=__description__
    )

    parser.add_argument("-v", "--version", action="version", version=f"{__app_name__} v{__version__}",
                        help="displays the current version of the application")

    sub_parsers = parser.add_subparsers(
        title="commands", dest="command", required=True)

    for name, properties in supported_queries.items():
        p = sub_parsers.add_parser(name, help=properties["help"])
        for arg in properties["args"]:
            p.add_argument(*arg.pop("name_or_flags"), **arg)

    args: dict = parser.parse_args().__dict__
    querie: Callable = supported_queries[args.pop("command")]["target"]

    return querie, args


if __name__ == "__main__":
    main()
