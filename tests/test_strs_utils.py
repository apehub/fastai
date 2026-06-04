from __future__ import annotations

from pathlib import Path

from fastai.utils.strs import as_path_list, as_str, as_str_list, extract_json_object


def test_extract_json_object_tolerates_prose_and_code_fences() -> None:
    text = 'Here is JSON:\n```json\n{"name": "fastai", "count": 2}\n```'

    assert extract_json_object(text) == {"name": "fastai", "count": 2}


def test_extract_json_object_rejects_missing_or_invalid_objects() -> None:
    assert extract_json_object("not json") is None
    assert extract_json_object("[1, 2, 3]") is None
    assert extract_json_object("{invalid") is None


def test_as_str_returns_only_string_values() -> None:
    assert as_str("fastai") == "fastai"
    assert as_str(42) == ""


def test_as_str_list_keeps_only_string_items() -> None:
    assert as_str_list(["src", 42, "tests", None]) == ["src", "tests"]
    assert as_str_list("src") == []


def test_as_path_list_keeps_only_string_items_as_paths() -> None:
    assert as_path_list(["src", 42, "tests", None]) == [Path("src"), Path("tests")]
    assert as_path_list("src") == []
