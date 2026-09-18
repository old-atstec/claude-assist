"""Tests for the memory panel WebSocket commands."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from custom_components.ai_subscription_assist import memory_websocket
from custom_components.ai_subscription_assist.const import DOMAIN


@pytest.mark.asyncio
async def test_entry_list_tolerates_subentry_without_disabled_by() -> None:
    """HA 2026.9 ConfigSubentry has no disabled_by attribute; the panel must not crash."""
    subentry = SimpleNamespace(
        subentry_id="sub1", subentry_type="conversation", title="Claude"
    )
    entry = SimpleNamespace(
        entry_id="e1", title="Claude", state="loaded", subentries={"sub1": subentry}
    )
    hass = MagicMock()
    hass.config_entries.async_entries.return_value = [entry]
    connection = MagicMock()

    # @async_response wraps the coroutine into a task scheduler; call the
    # underlying handler directly.
    await memory_websocket.ws_entry_list.__wrapped__(hass, connection, {"id": 1})

    hass.config_entries.async_entries.assert_called_once_with(DOMAIN)
    connection.send_result.assert_called_once()
    payload = connection.send_result.call_args.args[1]
    assert payload["count"] == 1
    assert payload["entries"][0]["subentries"] == [
        {"subentry_id": "sub1", "title": "Claude", "disabled": False}
    ]
