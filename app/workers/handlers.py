"""Pure task handlers used by the Celery worker.

Handlers deliberately avoid database and broker access so they can be tested
independently and extended without coupling business logic to Celery.
"""
from typing import Any


def execute_task(task_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Execute a supported task type and return a JSON-serialisable result."""
    if not isinstance(payload, dict):
        raise ValueError("Task payload must be a JSON object")

    if task_type == "echo":
        return {"echo": payload}

    if task_type == "sum":
        values = payload.get("values")
        if not isinstance(values, list) or not values:
            raise ValueError("'sum' tasks require a non-empty 'values' list")
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in values):
            raise ValueError("'sum' values must all be numbers")
        return {"sum": sum(values)}

    if task_type == "concat":
        values = payload.get("values")
        if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
            raise ValueError("'concat' tasks require a list of strings")
        return {"result": "".join(values)}

    raise ValueError(
        f"Unsupported task type: {task_type!r}. "
        "Supported types are: echo, sum, concat."
    )
