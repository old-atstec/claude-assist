"""Anthropic client factory for the Claude subscription (OAuth) provider."""

from __future__ import annotations

import anthropic
import httpx

from homeassistant.core import HomeAssistant
from homeassistant.util.ssl import SSL_ALPN_HTTP11, client_context

from .claude_code_mimicry import ClaudeCodeIdentity, ClaudeCodeTransport
from .const import CONF_CLAUDE_ACCOUNT_UUID, CONF_CLAUDE_TOOL_OBFUSCATION, LOGGER

_DEFAULT_TIMEOUT = httpx.Timeout(600.0, connect=10.0)


def create_claude_code_client(
    hass: HomeAssistant,
    access_token: str,
    *,
    entry_id: str,
    account_uuid: str | None = None,
    obfuscate_tool_names: bool = False,
) -> anthropic.AsyncAnthropic:
    """Create an Anthropic client whose traffic is shaped like Claude Code CLI.

    The client owns a dedicated httpx client (``await client.close()`` releases
    it); the shared Home Assistant httpx client cannot be used because the
    mimicry lives in a custom transport.
    """
    identity = ClaudeCodeIdentity.for_entry(entry_id, account_uuid)
    transport = ClaudeCodeTransport(
        # Same ALPN bucket as HA's own httpx helper: httpcore mutates the context.
        httpx.AsyncHTTPTransport(verify=client_context(alpn_protocols=SSL_ALPN_HTTP11)),
        identity,
        obfuscate_tool_names=obfuscate_tool_names,
    )
    http_client = httpx.AsyncClient(transport=transport, timeout=_DEFAULT_TIMEOUT)
    LOGGER.debug(
        "Claude Code mimicry client created (session %s, tool obfuscation %s)",
        identity.session_id,
        obfuscate_tool_names,
    )
    return anthropic.AsyncAnthropic(
        api_key=None,
        auth_token=access_token,
        http_client=http_client,
        max_retries=2,
    )


def create_claude_code_client_for_entry(hass: HomeAssistant, entry, access_token: str) -> anthropic.AsyncAnthropic:
    """Create the client from a config entry's data/options."""
    return create_claude_code_client(
        hass,
        access_token,
        entry_id=entry.entry_id,
        account_uuid=entry.data.get(CONF_CLAUDE_ACCOUNT_UUID),
        obfuscate_tool_names=bool(entry.options.get(CONF_CLAUDE_TOOL_OBFUSCATION, False)),
    )
