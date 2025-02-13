import json

import pytest

from datetime import datetime
from ktodo import (
    SUCCESS,
    DIR_ERROR,
    FILE_ERROR,
    DB_READ_ERROR,
    DB_WRITE_ERROR,
    JSON_ERROR,
    ID_ERROR,
    __app_name__,
    __version__,
    cli,
    ktodo,
)

test_data = [[{
    "description": "Test1",
    "todo": {
        "Description": "Test1.",
        "Priority": "2",
        "Status": "todo",
        "CreatedAt": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
        "UpdatedAt": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    },
}, SUCCESS],
    [{
        "description": "Test2",
        "status": "done",
        "todo": {
            "Description": "Test2.",
            "Priority": "2",
            "Status": "done",
            "CreatedAt": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
            "UpdatedAt": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        },
    }, SUCCESS],
    [{
        "description": "Test3",
        "priority": "1",
        "todo": {
            "Description": "Test3.",
            "Priority": "1",
            "Status": "todo",
            "CreatedAt": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
            "UpdatedAt": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        },
    }, SUCCESS],
    [{
        "description": "Test4",
        "priority": "3",
        "todo": {
            "Description": "Test4.",
            "Priority": "3",
            "Status": "todo",
            "CreatedAt": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
            "UpdatedAt": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        },
    }, SUCCESS],
    [{
        "description": "Test5",
        "priority": "1",
        "status": "in-progress",
        "todo": {
            "Description": "Test5.",
            "Priority": "1",
            "Status": "in-progress",
            "CreatedAt": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
            "UpdatedAt": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        },
    }, SUCCESS],
    [{
        "description": "Test6",
        "priority": "2",
        "status": "todo",
        "todo": {
            "Description": "Test6.",
            "Priority": "2",
            "Status": "todo",
            "CreatedAt": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
            "UpdatedAt": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        },
    }, SUCCESS
]]
print(test_data)


@pytest.fixture
def mock_json_file(tmp_path):
    todo = [
        {
            "Description": "task9 with date.",
            "Priority": "2",
            "Status": "todo",
            "createdAt": "2025-02-01 22:49:59",
            "updatedAt": "2025-02-01 22:49:59"
        },
        {
            "Description": "task10 with date.",
            "Priority": "2",
            "Status": "in-progress",
            "createdAt": "2025-02-01 22:52:26",
            "updatedAt": "2025-02-01 22:53:16"
        }
    ]
    db_file = tmp_path / "todos.json"
    with db_file.open("w") as db:
        json.dump(todo, db, indent=4)
    return db_file


def test_add(mock_json_file):
    todoer = ktodo.Todoer(mock_json_file)
    for data in test_data:
        status = False
        priority = False
        if data[0].get("status"):
            status = True
        if data[0].get("priority"):
            priority = True

        if status and priority:
            assert todoer.add(
                data[0]["description"], status=data[0]["status"], priority=data[0]["priority"]) == (data[0]["todo"], data[1])

        if status and not priority:
            assert todoer.add(
                data[0]["description"], status=data[0]["status"]) == (data[0]["todo"], data[1])

        if not status and priority:
            assert todoer.add(
                data[0]["description"], priority=data[0]["priority"]) == (data[0]["todo"], data[1])

        if not status and not priority:
            assert todoer.add(
                data[0]["description"]) == (data[0]["todo"], data[1])

    read = todoer._db_handler.read_todos()
    assert len(read.todo_list) == 8, read.todo_list


def test_remove(mock_json_file):
    todoer = ktodo.Todoer(mock_json_file)
    read = todoer._db_handler.read_todos()

    assert todoer.remove(0) == ({}, ID_ERROR)
    assert todoer.remove(-10) == ({}, ID_ERROR)
    assert todoer.remove(110) == ({}, ID_ERROR)

    assert todoer.remove(1) == (read.todo_list[0], SUCCESS)

    read = todoer._db_handler.read_todos()
    assert len(read.todo_list) == 1
