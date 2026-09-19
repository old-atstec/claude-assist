"""Tests for expiry-driven Claude OAuth token refresh."""

from __future__ import annotations

import asyncio
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import anthropic

import custom_components.ai_subscription_assist as integration
from custom_components.ai_subscription_assist.const import (
    CONF_EXPIRES_AT,
    DOMAIN,
    TOKEN_EXPIRY_BUFFER,
)


def _entry(expires_in: float, client: object | None = None) -> SimpleNamespace:
    entry = SimpleNamespace(
        entry_id="entry-1",
        data={CONF_EXPIRES_AT: time.time() + expires_in},
    )
    if client is not None:
        entry.runtime_data = client
    return entry


def _hass() -> SimpleNamespace:
    return SimpleNamespace(data={})


def _client() -> anthropic.AsyncClient:
    return anthropic.AsyncAnthropic(api_key=None, auth_token="old-token")


def test_token_expiring_uses_buffer() -> None:
    assert not integration._claude_token_expiring(_entry(TOKEN_EXPIRY_BUFFER + 60))
    assert integration._claude_token_expiring(_entry(TOKEN_EXPIRY_BUFFER - 60))
    assert integration._claude_token_expiring(_entry(-1))
    assert integration._claude_token_expiring(SimpleNamespace(entry_id="x", data={}))


def test_fresh_token_is_not_refreshed() -> None:
    entry = _entry(3600, _client())
    with patch.object(integration, "_async_refresh_token", AsyncMock()) as refresh:
        assert asyncio.run(integration.async_ensure_claude_access_token(_hass(), entry))
    refresh.assert_not_called()
    assert entry.runtime_data.auth_token == "old-token"


def test_expiring_token_is_refreshed_and_swapped_on_client() -> None:
    entry = _entry(60, _client())
    with patch.object(
        integration, "_async_refresh_token", AsyncMock(return_value="new-token")
    ) as refresh:
        assert asyncio.run(integration.async_ensure_claude_access_token(_hass(), entry))
    refresh.assert_awaited_once()
    assert entry.runtime_data.auth_token == "new-token"


def test_force_refreshes_even_when_fresh() -> None:
    entry = _entry(3600, _client())
    with patch.object(
        integration, "_async_refresh_token", AsyncMock(return_value="new-token")
    ):
        assert asyncio.run(
            integration.async_ensure_claude_access_token(_hass(), entry, force=True)
        )
    assert entry.runtime_data.auth_token == "new-token"


def test_failed_refresh_reports_false_and_keeps_client() -> None:
    entry = _entry(-1, _client())
    with patch.object(integration, "_async_refresh_token", AsyncMock(return_value=None)):
        assert not asyncio.run(integration.async_ensure_claude_access_token(_hass(), entry))
    assert entry.runtime_data.auth_token == "old-token"


def test_refresh_without_runtime_data_during_setup() -> None:
    entry = _entry(-1)
    with patch.object(
        integration, "_async_refresh_token", AsyncMock(return_value="new-token")
    ):
        assert asyncio.run(integration.async_ensure_claude_access_token(_hass(), entry))


def test_concurrent_refreshes_are_serialised() -> None:
    """A periodic check racing a chat turn must not spend the refresh token twice."""
    entry = _entry(-1, _client())
    hass = _hass()

    async def fake_refresh(_hass, _entry):
        await asyncio.sleep(0)
        _entry.data = {**_entry.data, CONF_EXPIRES_AT: time.time() + 8 * 3600}
        return "new-token"

    async def run():
        with patch.object(integration, "_async_refresh_token", AsyncMock(side_effect=fake_refresh)) as refresh:
            results = await asyncio.gather(
                integration.async_ensure_claude_access_token(hass, entry),
                integration.async_ensure_claude_access_token(hass, entry),
                integration.async_ensure_claude_access_token(hass, entry),
            )
        return results, refresh.await_count

    results, count = asyncio.run(run())
    assert results == [True, True, True]
    assert count == 1
    assert "entry-1" in hass.data[DOMAIN]["claude_refresh_locks"]
