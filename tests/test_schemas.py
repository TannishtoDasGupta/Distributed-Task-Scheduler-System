import pytest
from pydantic import ValidationError

from app.schemas import TaskCreate


def test_task_payload_defaults_to_empty_object():
    task = TaskCreate(type="echo")
    assert task.payload == {}


def test_task_payload_preserves_empty_object():
    task = TaskCreate(type="echo", payload={})
    assert task.payload == {}


def test_task_type_is_trimmed():
    task = TaskCreate(type="  echo  ")
    assert task.type == "echo"


@pytest.mark.parametrize("task_type", ["", "   ", "x" * 51])
def test_task_type_rejects_invalid_length(task_type):
    with pytest.raises(ValidationError):
        TaskCreate(type=task_type)


def test_task_payload_must_be_an_object():
    with pytest.raises(ValidationError):
        TaskCreate(type="echo", payload=["not", "an", "object"])
