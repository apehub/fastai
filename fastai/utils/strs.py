"""String and lightweight coercion helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def extract_json_object(text: str) -> dict[str, Any] | None:
    """Extract the first JSON object from text that may include prose or fences."""

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    try:
        parsed = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None

    return parsed if isinstance(parsed, dict) else None


def as_str(value: Any) -> str:
    return value if isinstance(value, str) else ""


def as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    return [item for item in value if isinstance(item, str)]


def as_path_list(value: Any) -> list[Path]:
    if not isinstance(value, list):
        return []

    return [Path(item) for item in value if isinstance(item, str)]
