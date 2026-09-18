"""Tests for memory owner resolution."""

from __future__ import annotations

from types import SimpleNamespace

from custom_components.ai_subscription_assist.memory_service import (
    AUTOMATION_OWNER_ID,
    _owner_user_id,
)


def test_owner_is_ha_user_when_present() -> None:
    user_input = SimpleNamespace(context=SimpleNamespace(user_id="user-1"))
    assert _owner_user_id(user_input) == "user-1"


def test_owner_falls_back_to_automation_without_user() -> None:
    """conversation.process from automations/webhooks has no user context."""
    assert _owner_user_id(SimpleNamespace(context=SimpleNamespace(user_id=None))) == AUTOMATION_OWNER_ID
    assert _owner_user_id(SimpleNamespace(context=None)) == AUTOMATION_OWNER_ID
