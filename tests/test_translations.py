"""Sanity checks for integration translation files."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

COMPONENT_DIR = Path(__file__).resolve().parents[1] / "custom_components" / "ai_subscription_assist"
STRINGS_PATH = COMPONENT_DIR / "strings.json"
TRANSLATION_PATHS = sorted((COMPONENT_DIR / "translations").glob("*.json"))

# The HA frontend renders strings with ICU MessageFormat, where an unescaped
# `<name>` is parsed as a tag and breaks the whole string ("INVALID_TAG").
UNESCAPED_TAG = re.compile(r"(?<!')<[A-Za-zА-Яа-я]")


def _flatten(data: dict, prefix: str = "") -> dict[str, str]:
    flat: dict[str, str] = {}
    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            flat.update(_flatten(value, path))
        else:
            flat[path] = value
    return flat


def _load(path: Path) -> dict[str, str]:
    return _flatten(json.loads(path.read_text(encoding="utf-8")))


@pytest.mark.parametrize("path", TRANSLATION_PATHS, ids=lambda p: p.name)
def test_translation_keys_match_strings(path: Path) -> None:
    """Every language file has exactly the keys declared in strings.json."""
    expected = set(_load(STRINGS_PATH))
    actual = set(_load(path))
    assert actual == expected, {
        "missing": sorted(expected - actual),
        "extra": sorted(actual - expected),
    }


@pytest.mark.parametrize("path", [STRINGS_PATH, *TRANSLATION_PATHS], ids=lambda p: p.name)
def test_no_unescaped_angle_brackets(path: Path) -> None:
    """Placeholders like <text> must be written as '<'text> for ICU MessageFormat."""
    offenders = {key: value for key, value in _load(path).items() if UNESCAPED_TAG.search(value)}
    assert not offenders, offenders
