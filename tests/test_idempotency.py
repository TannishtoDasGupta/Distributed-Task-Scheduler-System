from app.routes.task_routes import request_fingerprint


def test_request_fingerprint_is_stable_across_dictionary_order():
    first = request_fingerprint("echo", {"a": 1, "b": {"x": 2, "y": 3}})
    second = request_fingerprint("echo", {"b": {"y": 3, "x": 2}, "a": 1})
    assert first == second


def test_request_fingerprint_changes_when_task_input_changes():
    first = request_fingerprint("sum", {"values": [1, 2]})
    changed_payload = request_fingerprint("sum", {"values": [1, 3]})
    changed_type = request_fingerprint("echo", {"values": [1, 2]})
    assert first != changed_payload
    assert first != changed_type
