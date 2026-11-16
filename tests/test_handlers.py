import pytest

from app.workers.handlers import execute_task


def test_echo_returns_payload():
    payload = {"message": "hello"}
    assert execute_task("echo", payload) == {"echo": payload}


def test_sum_returns_total():
    assert execute_task("sum", {"values": [10, 20, 30]}) == {"sum": 60}


def test_sum_accepts_floats():
    assert execute_task("sum", {"values": [1.5, 2.5]}) == {"sum": 4.0}


def test_sum_rejects_empty_values():
    with pytest.raises(ValueError, match="non-empty"):
        execute_task("sum", {"values": []})


def test_sum_rejects_non_numeric_values():
    with pytest.raises(ValueError, match="numbers"):
        execute_task("sum", {"values": [1, "two"]})


def test_sum_rejects_boolean_values():
    with pytest.raises(ValueError, match="numbers"):
        execute_task("sum", {"values": [True, 2]})


def test_concat_returns_joined_string():
    assert execute_task("concat", {"values": ["open", "source"]}) == {
        "result": "opensource"
    }


def test_concat_rejects_non_string_values():
    with pytest.raises(ValueError, match="list of strings"):
        execute_task("concat", {"values": ["ok", 1]})


def test_unknown_task_type_is_rejected():
    with pytest.raises(ValueError, match="Unsupported task type"):
        execute_task("not_registered", {})


def test_payload_must_be_object():
    with pytest.raises(ValueError, match="JSON object"):
        execute_task("echo", [])
