"""Claude Code CLI wire-fingerprint mimicry for Anthropic OAuth requests.

Subscription (OAuth) tokens are only meant to be used by the official Claude
Code CLI. This module reshapes every request the Anthropic SDK produces so it is
indistinguishable from the native client on the wire. The transforms are ported
from CLIProxyAPI's claude executor (cloaking, per-request beta set and CCH body
signing) and the cc-mimicry plugin (header profile, tool-name obfuscation):

1. Headers: exact Claude Code user-agent, Node/JS ``x-stainless-*`` profile,
   session/request ids and a per-request ``anthropic-beta`` list.
2. ``system``: ``[0]`` billing attribution block, ``[1]`` Claude Code identity.
   The caller's own system prompt is relocated into the conversation — as a
   ``role: system`` turn on models that accept it, as a ``<system-reminder>``
   in the first user message on legacy models.
3. First user message gets Claude Code's ``currentDate`` reminder,
   ``metadata.user_id`` gets the CLI's ``{device_id, account_uuid, session_id}``
   JSON, cache breakpoints get the OAuth ``1h`` ttl.
4. The final serialized body is signed: ``cch=<5 hex>`` in the billing block is
   xxHash64 (fixed seed) of the normalized body.
5. Optionally tool names are aliased (and restored in the response stream) so
   third-party tool sets do not identify the client.

No Home Assistant imports here: the module is unit-tested standalone.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from datetime import date
import hashlib
import json
import platform
import random
import re
import struct
from typing import Any
import uuid

import httpx

# ---------------------------------------------------------------------------
# Static fingerprint (Claude Code 2.1.268 / @anthropic-ai/sdk 0.112.1)
# ---------------------------------------------------------------------------

CLAUDE_CODE_VERSION = "2.1.268"
CLAUDE_CODE_ENTRYPOINT = "cli"
CLAUDE_CODE_USER_AGENT = f"claude-cli/{CLAUDE_CODE_VERSION} (external, {CLAUDE_CODE_ENTRYPOINT})"
CLAUDE_CODE_IDENTITY = "You are Claude Code, Anthropic's official CLI for Claude."

STAINLESS_PACKAGE_VERSION = "0.112.1"
STAINLESS_RUNTIME_VERSION = "v26.3.0"
STAINLESS_RUNTIME = "node"
STAINLESS_LANG = "js"
STAINLESS_TIMEOUT = "600"
ANTHROPIC_VERSION = "2023-06-01"

BETA_CLAUDE_CODE = "claude-code-20250219"
BETA_OAUTH = "oauth-2025-04-20"
BETA_INTERLEAVED_THINKING = "interleaved-thinking-2025-05-14"
BETA_REDACT_THINKING = "redact-thinking-2026-02-12"
BETA_THINKING_TOKEN_COUNT = "thinking-token-count-2026-05-13"
BETA_CONTEXT_MANAGEMENT = "context-management-2025-06-27"
BETA_PROMPT_CACHING_SCOPE = "prompt-caching-scope-2026-01-05"
BETA_MID_CONVERSATION_SYSTEM = "mid-conversation-system-2026-04-07"
BETA_ADVISOR_TOOL = "advisor-tool-2026-03-01"
BETA_ADVANCED_TOOL_USE = "advanced-tool-use-2025-11-20"
BETA_EXTENDED_CACHE_TTL = "extended-cache-ttl-2025-04-11"
BETA_CACHE_DIAGNOSIS = "cache-diagnosis-2026-04-07"

# Model ids that reject a mid-conversation {"role": "system"} turn. Their caller
# system prompt travels as a <system-reminder> in the first user message instead.
# Unknown / future ids optimistically use the system turn.
LEGACY_SYSTEM_REMINDER_MODELS = frozenset(
    {
        "claude-3-5-haiku-20241022",
        "claude-3-5-haiku-latest",
        "claude-3-7-sonnet-20250219",
        "claude-3-7-sonnet-latest",
        "claude-haiku-4-5",
        "claude-haiku-4-5-20251001",
        "claude-opus-4",
        "claude-opus-4-20250514",
        "claude-opus-4-1",
        "claude-opus-4-1-20250805",
        "claude-opus-4-5",
        "claude-opus-4-5-20251101",
        "claude-opus-4-6",
        "claude-opus-4-7",
        "claude-sonnet-4",
        "claude-sonnet-4-20250514",
        "claude-sonnet-4-5",
        "claude-sonnet-4-5-20250929",
        "claude-sonnet-4-6",
    }
)

CACHE_CONTROL_TTL_OAUTH = "1h"
CONTEXT_MANAGEMENT = {"edits": [{"type": "clear_thinking_20251015", "keep": "all"}]}

# Top-level key order of a native /v1/messages body (from mitmproxy captures).
NATIVE_BODY_KEY_ORDER = (
    "model",
    "messages",
    "system",
    "tools",
    "tool_choice",
    "metadata",
    "max_tokens",
    "temperature",
    "thinking",
    "context_management",
    "output_config",
    "stream",
)

BILLING_HEADER_PREFIX = "x-anthropic-billing-header:"
BUILD_FINGERPRINT_SALT = "59cf53e54c78"

CCH_SEED = 0x4D659218E32A3268
CCH_PLACEHOLDER = "00000"
CCH_EXCLUDED_KEYS = frozenset({b'"max_tokens"', b'"fallbacks"', b'"fallback_credit_token"'})

CLAUDE_CODE_REPORTING_OUTCOMES = """# Reporting outcomes

Report what actually happened, not what you intended. When you say something is done, sent, saved, fixed, or verified, that claim must rest on a result you observed in this session — tool output, the file as it now reads, the page as it now loads — not on what the step should have produced. If you did not check, say you did not check. If any step failed, was skipped, or came back different from what you expected, say so in the first sentence of your report, before anything else, even when the rest of the work succeeded. Never quietly work around a failure in a way that makes it look resolved; a problem the user can see is recoverable, one your summary hides is not. When you stop before the task is complete, your first line says so plainly and names what is left. Do not describe partial work as done, and do not let a summary read as more certain than the evidence behind it."""


# ---------------------------------------------------------------------------
# xxHash64 (pure Python; used for the CCH body signature)
# ---------------------------------------------------------------------------

_P1 = 0x9E3779B185EBCA87
_P2 = 0xC2B2AE3D27D4EB4F
_P3 = 0x165667B19E3779F9
_P4 = 0x85EBCA77C2B2AE63
_P5 = 0x27D4EB2F165667C5
_M64 = 0xFFFFFFFFFFFFFFFF


def _rotl(x: int, r: int) -> int:
    return ((x << r) | (x >> (64 - r))) & _M64


def _round(acc: int, lane: int) -> int:
    acc = (acc + lane * _P2) & _M64
    return (_rotl(acc, 31) * _P1) & _M64


def _merge(acc: int, val: int) -> int:
    acc ^= _round(0, val)
    return (acc * _P1 + _P4) & _M64


def xxh64(data: bytes, seed: int = 0) -> int:
    """Return the 64-bit xxHash of ``data``."""
    n = len(data)
    i = 0
    if n >= 32:
        v1 = (seed + _P1 + _P2) & _M64
        v2 = (seed + _P2) & _M64
        v3 = seed & _M64
        v4 = (seed - _P1) & _M64
        unpack = struct.Struct("<QQQQ").unpack_from
        while i <= n - 32:
            l1, l2, l3, l4 = unpack(data, i)
            v1 = _round(v1, l1)
            v2 = _round(v2, l2)
            v3 = _round(v3, l3)
            v4 = _round(v4, l4)
            i += 32
        h = (_rotl(v1, 1) + _rotl(v2, 7) + _rotl(v3, 12) + _rotl(v4, 18)) & _M64
        h = _merge(h, v1)
        h = _merge(h, v2)
        h = _merge(h, v3)
        h = _merge(h, v4)
    else:
        h = (seed + _P5) & _M64
    h = (h + n) & _M64
    while i + 8 <= n:
        (lane,) = struct.unpack_from("<Q", data, i)
        h ^= _round(0, lane)
        h = (_rotl(h, 27) * _P1 + _P4) & _M64
        i += 8
    if i + 4 <= n:
        (lane,) = struct.unpack_from("<I", data, i)
        h ^= (lane * _P1) & _M64
        h = (_rotl(h, 23) * _P2 + _P3) & _M64
        i += 4
    while i < n:
        h ^= (data[i] * _P5) & _M64
        h = (_rotl(h, 11) * _P1) & _M64
        i += 1
    h ^= h >> 33
    h = (h * _P2) & _M64
    h ^= h >> 29
    h = (h * _P3) & _M64
    h ^= h >> 32
    return h


# ---------------------------------------------------------------------------
# Identity (session / device) and headers
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class ClaudeCodeIdentity:
    """Per-installation identity Claude Code embeds in metadata and headers."""

    device_id: str
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    account_uuid: str = ""

    @classmethod
    def for_entry(cls, entry_id: str, account_uuid: str | None = None) -> ClaudeCodeIdentity:
        """Derive a stable device id from the config entry id."""
        device_id = hashlib.sha256(f"ai_subscription_assist:{entry_id}".encode()).hexdigest()
        return cls(device_id=device_id, account_uuid=account_uuid or "")

    def user_id(self) -> str:
        return json.dumps(
            {
                "device_id": self.device_id,
                "account_uuid": self.account_uuid,
                "session_id": self.session_id,
            },
            separators=(",", ":"),
        )


def stainless_os() -> str:
    system = platform.system()
    return {"Darwin": "MacOS", "Windows": "Windows", "Linux": "Linux", "FreeBSD": "FreeBSD"}.get(
        system, f"Other::{system.lower()}"
    )


def stainless_arch() -> str:
    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64"):
        return "x64"
    if machine in ("arm64", "aarch64"):
        return "arm64"
    if machine in ("i386", "i686", "x86"):
        return "x86"
    return f"other::{machine}"


def supported_accept_encoding() -> str:
    """Advertise the native set, but only codecs this httpx can decode."""
    from httpx._decoders import SUPPORTED_DECODERS

    return ", ".join(enc for enc in ("gzip", "deflate", "br", "zstd") if enc in SUPPORTED_DECODERS)


def build_headers(
    original: httpx.Headers,
    identity: ClaudeCodeIdentity,
    *,
    betas: str,
    content_length: int | None,
    host: str,
) -> list[tuple[str, str]]:
    """Rebuild the outbound header set in Claude Code's wire casing and order.

    The real client emits its headers bytewise-sorted (uppercase names first),
    so the returned list is in that order. Everything the Python SDK adds
    (its own user-agent, Python ``x-stainless-*`` profile, async markers) is
    dropped; ``authorization`` and ``content-type`` are carried over.
    """
    headers: dict[str, str] = {
        "Accept": "application/json",
        "Accept-Encoding": supported_accept_encoding(),
        "Connection": "keep-alive",
        "Host": host,
        "User-Agent": CLAUDE_CODE_USER_AGENT,
        "X-Claude-Code-Session-Id": identity.session_id,
        "X-Stainless-Arch": stainless_arch(),
        "X-Stainless-Lang": STAINLESS_LANG,
        "X-Stainless-OS": stainless_os(),
        "X-Stainless-Package-Version": STAINLESS_PACKAGE_VERSION,
        "X-Stainless-Retry-Count": "0",
        "X-Stainless-Runtime": STAINLESS_RUNTIME,
        "X-Stainless-Runtime-Version": STAINLESS_RUNTIME_VERSION,
        "X-Stainless-Timeout": STAINLESS_TIMEOUT,
        "anthropic-beta": betas,
        "anthropic-dangerous-direct-browser-access": "true",
        "anthropic-version": ANTHROPIC_VERSION,
        "x-app": "cli",
        "x-client-request-id": str(uuid.uuid4()),
    }
    if content_length is not None:
        headers["Content-Length"] = str(content_length)
    if (auth := original.get("authorization")) is not None:
        headers["Authorization"] = auth
    if (api_key := original.get("x-api-key")) is not None:
        headers["x-api-key"] = api_key
    if (content_type := original.get("content-type")) is not None:
        headers["Content-Type"] = content_type
    return sorted(headers.items(), key=lambda item: item[0].encode())


# ---------------------------------------------------------------------------
# Body helpers
# ---------------------------------------------------------------------------


def _model_name(body: dict[str, Any]) -> str:
    model = str(body.get("model", "")).strip().lower()
    return model.rsplit("/", 1)[-1]


def uses_legacy_system_reminder(body: dict[str, Any]) -> bool:
    return _model_name(body) in LEGACY_SYSTEM_REMINDER_MODELS


def is_fable_51_model(model: str) -> bool:
    m = model.strip().lower()
    for target in ("fable-5-1", "fable-5.1", "mythos-5-1", "mythos-5.1"):
        idx = m.find(target)
        if idx != -1:
            nxt = idx + len(target)
            if nxt >= len(m) or not m[nxt].isdigit():
                return True
    return False


def _thinking_type(body: dict[str, Any]) -> str:
    thinking = body.get("thinking")
    if isinstance(thinking, dict):
        return str(thinking.get("type", ""))
    return ""


def _thinking_display_set(body: dict[str, Any]) -> bool:
    thinking = body.get("thinking")
    return isinstance(thinking, dict) and "display" in thinking


def build_betas(body: dict[str, Any] | None) -> str:
    """Assemble the per-request ``anthropic-beta`` list for an OAuth credential.

    Ordered like the interactive ``cli`` entrypoint capture; the
    mid-conversation-system token is only claimed when the body will actually
    carry a ``role: system`` turn.
    """
    betas = [BETA_CLAUDE_CODE, BETA_OAUTH, BETA_INTERLEAVED_THINKING]
    if body is None or not _thinking_display_set(body):
        betas.append(BETA_REDACT_THINKING)
    betas += [BETA_THINKING_TOKEN_COUNT, BETA_CONTEXT_MANAGEMENT, BETA_PROMPT_CACHING_SCOPE]
    if body is not None and not uses_legacy_system_reminder(body):
        betas.append(BETA_MID_CONVERSATION_SYSTEM)
    betas += [BETA_ADVISOR_TOOL, BETA_ADVANCED_TOOL_USE, BETA_EXTENDED_CACHE_TTL]
    if body is not None and isinstance(body.get("diagnostics"), dict):
        betas.append(BETA_CACHE_DIAGNOSIS)
    return ",".join(betas)


def compute_build_fingerprint(message_text: str, version: str) -> str:
    """3-hex build suffix Claude Code embeds in ``cc_version``."""
    chars = "".join(message_text[i] if i < len(message_text) else "0" for i in (4, 7, 20))
    return hashlib.sha256((BUILD_FINGERPRINT_SALT + chars + version).encode()).hexdigest()[:3]


def _content_text_blocks(content: Any) -> list[str]:
    if isinstance(content, str):
        return [content]
    if isinstance(content, list):
        return [b["text"] for b in content if isinstance(b, dict) and b.get("type") == "text" and "text" in b]
    return []


def billing_fingerprint_message_text(body: dict[str, Any]) -> str:
    """Last text block of the most recent user message (native seeding rule)."""
    text = ""
    for message in body.get("messages", []):
        if not isinstance(message, dict) or message.get("role") != "user":
            continue
        blocks = _content_text_blocks(message.get("content"))
        if blocks and blocks[-1]:
            text = blocks[-1]
    return text


def build_billing_header(message_text: str, *, version: str = CLAUDE_CODE_VERSION) -> str:
    build = compute_build_fingerprint(message_text, version)
    return (
        f"{BILLING_HEADER_PREFIX} cc_version={version}.{build}; "
        f"cc_entrypoint={CLAUDE_CODE_ENTRYPOINT}; cch={CCH_PLACEHOLDER};"
    )


def is_billing_header_text(text: str) -> bool:
    return text.startswith(BILLING_HEADER_PREFIX)


def _text_block(text: str, cache_control: dict[str, Any] | None = None) -> dict[str, Any]:
    block: dict[str, Any] = {"type": "text", "text": text}
    if cache_control is not None:
        block["cache_control"] = dict(cache_control)
    return block


EPHEMERAL = {"type": "ephemeral"}


def collect_caller_system_blocks(system: Any) -> list[str]:
    """Caller system texts worth forwarding (skips our own attribution blocks)."""
    texts: list[str] = []
    for text in _content_text_blocks(system):
        if not text.strip() or is_billing_header_text(text) or text == CLAUDE_CODE_IDENTITY:
            continue
        texts.append(text)
    return texts


def _first_user_index(messages: list[Any]) -> int:
    for idx, message in enumerate(messages):
        if isinstance(message, dict) and message.get("role") == "user":
            return idx
    return -1


def _as_block_list(content: Any) -> list[dict[str, Any]]:
    if isinstance(content, str):
        return [_text_block(content)]
    if isinstance(content, list):
        return [dict(b) if isinstance(b, dict) else b for b in content]
    return []


def _system_reminder(text: str) -> str:
    return f"<system-reminder>\n{text}{'' if text.endswith(chr(10)) else chr(10)}</system-reminder>"


def current_date_reminder(today: date) -> str:
    return (
        "<system-reminder>\n"
        "As you answer the user's questions, you can use the following context:\n"
        "# currentDate\n"
        f"Today's date is {today.isoformat()}.\n\n"
        "      IMPORTANT: this context may or may not be relevant to your tasks. "
        "You should not respond to this context unless it is highly relevant to your task.\n"
        "</system-reminder>\n\n"
    )


_DATE_REMINDER_PREFIX = (
    "<system-reminder>\nAs you answer the user's questions, you can use the following context:\n"
    "# currentDate\nToday's date is "
)


def _prepend_reminders_to_first_user(messages: list[Any], texts: list[str]) -> None:
    """Legacy-model path: caller system prompt as <system-reminder> blocks."""
    idx = _first_user_index(messages)
    if idx < 0 or not texts:
        return
    blocks = _as_block_list(messages[idx].get("content"))
    reminders = [_text_block(_system_reminder(t)) for t in texts]
    existing = {b.get("text") for b in blocks if isinstance(b, dict) and b.get("type") == "text"}
    reminders = [r for r in reminders if r["text"] not in existing]
    if not reminders:
        return
    # tool_result blocks must lead the message that answers a tool_use turn.
    insert_at = 0
    while insert_at < len(blocks) and isinstance(blocks[insert_at], dict) and blocks[insert_at].get("type") == "tool_result":
        insert_at += 1
    messages[idx]["content"] = blocks[:insert_at] + reminders + blocks[insert_at:]


def _insert_system_turns(messages: list[Any], texts: list[str]) -> None:
    """Modern-model path: caller system prompt as role=system turns after the first user turn."""
    idx = _first_user_index(messages)
    if idx < 0 or not texts:
        return
    insert_at = idx + 1
    while insert_at < len(messages) and messages[insert_at].get("role") == "user":
        insert_at += 1
    already = messages[insert_at : insert_at + len(texts)]
    if len(already) == len(texts) and all(
        m.get("role") == "system" and "\n\n".join(_content_text_blocks(m.get("content"))) == t
        for m, t in zip(already, texts, strict=True)
    ):
        return
    turns = [{"role": "system", "content": [_text_block(t, EPHEMERAL)]} for t in texts]
    messages[insert_at:insert_at] = turns


def _inject_current_date(messages: list[Any], today: date) -> None:
    idx = _first_user_index(messages)
    if idx < 0:
        return
    content = messages[idx].get("content")
    date_block = _text_block(current_date_reminder(today))
    if isinstance(content, str):
        messages[idx]["content"] = [date_block, _text_block(content, EPHEMERAL)]
        return
    if not isinstance(content, list):
        return
    blocks: list[Any] = []
    cached = False
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            text = block.get("text", "")
            if text.startswith(_DATE_REMINDER_PREFIX):
                continue
            if not cached and not (text.startswith("<system-reminder>") and "</system-reminder>" in text):
                block = {**block, "cache_control": dict(EPHEMERAL)}
                cached = True
        blocks.append(block)
    insert_at = 0
    while insert_at < len(blocks) and isinstance(blocks[insert_at], dict) and blocks[insert_at].get("type") == "tool_result":
        insert_at += 1
    blocks.insert(insert_at, date_block)
    messages[idx]["content"] = blocks


def _upgrade_cache_control_ttl(body: dict[str, Any], ttl: str) -> None:
    """Native OAuth ttl upgrade: only blocks that already carry a ttl-less cache_control."""

    def upgrade(block: Any) -> None:
        if not isinstance(block, dict):
            return
        cc = block.get("cache_control")
        if not isinstance(cc, dict) or "ttl" in cc or not isinstance(cc.get("type"), str):
            return
        upgraded = {"type": cc["type"], "ttl": ttl}
        if "scope" in cc:
            upgraded["scope"] = cc["scope"]
        block["cache_control"] = upgraded

    for block in body.get("system", []) if isinstance(body.get("system"), list) else []:
        upgrade(block)
    for message in body.get("messages", []):
        if isinstance(message, dict) and isinstance(message.get("content"), list):
            for block in message["content"]:
                upgrade(block)
    for tool in body.get("tools", []) if isinstance(body.get("tools"), list) else []:
        upgrade(tool)


def _reorder_keys(body: dict[str, Any]) -> dict[str, Any]:
    ordered = {key: body[key] for key in NATIVE_BODY_KEY_ORDER if key in body}
    ordered.update({key: value for key, value in body.items() if key not in ordered})
    return ordered


def cloak_messages_body(
    body: dict[str, Any],
    identity: ClaudeCodeIdentity,
    *,
    today: date,
) -> dict[str, Any]:
    """Reshape a /v1/messages body into Claude Code's native form.

    Returns a new dict; ``body`` is not modified.
    """
    body = json.loads(json.dumps(body))
    messages: list[Any] = body.get("messages") or []
    body["messages"] = messages
    model = str(body.get("model", ""))

    caller_blocks = collect_caller_system_blocks(body.get("system"))
    message_text = billing_fingerprint_message_text(body)

    system = [
        _text_block(build_billing_header(message_text)),
        _text_block(CLAUDE_CODE_IDENTITY, EPHEMERAL),
    ]
    if is_fable_51_model(model):
        system.append(_text_block(CLAUDE_CODE_REPORTING_OUTCOMES))
    body["system"] = system

    if caller_blocks:
        if uses_legacy_system_reminder(body):
            _prepend_reminders_to_first_user(messages, caller_blocks)
        else:
            _insert_system_turns(messages, caller_blocks)
    _inject_current_date(messages, today)

    metadata = body.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
    metadata["user_id"] = identity.user_id()
    body["metadata"] = metadata

    if "temperature" not in body:
        body["temperature"] = 1
    elif isinstance(body["temperature"], float) and body["temperature"].is_integer():
        body["temperature"] = int(body["temperature"])

    if "context_management" not in body and _thinking_type(body) in ("enabled", "adaptive"):
        body["context_management"] = json.loads(json.dumps(CONTEXT_MANAGEMENT))

    _upgrade_cache_control_ttl(body, CACHE_CONTROL_TTL_OAUTH)
    return _reorder_keys(body)


# ---------------------------------------------------------------------------
# Serialization + CCH signing
# ---------------------------------------------------------------------------


def serialize_body(body: dict[str, Any]) -> bytes:
    """``JSON.stringify``-compatible serialization (compact, raw UTF-8)."""
    return json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


class _JsonScanner:
    """Byte-level JSON walker that builds the CCH hash view without reserializing.

    Mirrors Claude Code's normalization: every ``model`` string value is
    emptied and every ``max_tokens`` / ``fallbacks`` / ``fallback_credit_token``
    member is dropped, with the client's exact comma handling. It also records
    where the ``system[0].text`` string sits so the cch digits can be located.
    """

    __slots__ = ("body", "edits", "path", "pos", "system_text_span")

    def __init__(self, body: bytes) -> None:
        self.body = body
        self.pos = 0
        self.edits: list[tuple[int, int]] = []
        self.path: list[Any] = []
        self.system_text_span: tuple[int, int] | None = None

    # -- primitives --------------------------------------------------------

    def _skip_ws(self) -> None:
        body, pos = self.body, self.pos
        while pos < len(body) and body[pos] in b" \t\r\n":
            pos += 1
        self.pos = pos

    def _consume(self, char: int) -> bool:
        if self.pos < len(self.body) and self.body[self.pos] == char:
            self.pos += 1
            return True
        return False

    def _parse_string(self) -> tuple[int, int]:
        body = self.body
        if self.pos >= len(body) or body[self.pos] != 0x22:
            raise ValueError(f"missing JSON string at byte {self.pos}")
        start = self.pos
        pos = start + 1
        while pos < len(body):
            c = body[pos]
            if c == 0x5C:  # backslash
                pos += 2
            elif c == 0x22:
                self.pos = pos + 1
                return start, self.pos
            else:
                pos += 1
        raise ValueError(f"unterminated JSON string at byte {start}")

    def _add_edit(self, start: int, end: int) -> None:
        if start < end:
            self.edits.append((start, end))

    # -- values ------------------------------------------------------------

    def parse_value(self, collect: bool) -> None:
        self._skip_ws()
        if self.pos >= len(self.body):
            raise ValueError(f"missing JSON value at byte {self.pos}")
        c = self.body[self.pos]
        if c == 0x7B:  # {
            self._parse_object(collect)
        elif c == 0x5B:  # [
            self._parse_array(collect)
        elif c == 0x22:
            self._parse_string()
        else:
            start = self.pos
            while self.pos < len(self.body) and self.body[self.pos] not in b",}] \t\r\n":
                self.pos += 1
            if self.pos == start:
                raise ValueError(f"missing JSON value at byte {start}")

    def _parse_object(self, collect: bool) -> None:
        self.pos += 1
        self._skip_ws()
        if self._consume(0x7D):
            return
        # (start, end, comma_before, comma_after, excluded)
        members: list[tuple[int, int, int, int, bool]] = []
        comma_before = -1
        while True:
            self._skip_ws()
            member_start = self.pos
            key_start, key_end = self._parse_string()
            self._skip_ws()
            if not self._consume(0x3A):
                raise ValueError(f"missing object colon at byte {self.pos}")
            self._skip_ws()
            key = self.body[key_start:key_end]
            excluded = collect and key in CCH_EXCLUDED_KEYS
            self.path.append(json.loads(key))
            if collect and key == b'"model"' and self.pos < len(self.body) and self.body[self.pos] == 0x22:
                value_start, value_end = self._parse_string()
                self._add_edit(value_start + 1, value_end - 1)
            elif self.path == ["system", 0, "text"] and self.pos < len(self.body) and self.body[self.pos] == 0x22:
                self.system_text_span = self._parse_string()
            else:
                self.parse_value(collect and not excluded)
            self.path.pop()
            member_end = self.pos
            self._skip_ws()
            comma_after = -1
            if self._consume(0x2C):
                comma_after = self.pos - 1
            members.append((member_start, member_end, comma_before, comma_after, excluded))
            if comma_after >= 0:
                comma_before = comma_after
                continue
            if not self._consume(0x7D):
                raise ValueError(f"missing object end at byte {self.pos}")
            break
        if collect:
            self._add_excluded_member_edits(members)

    def _parse_array(self, collect: bool) -> None:
        self.pos += 1
        self._skip_ws()
        if self._consume(0x5D):
            return
        index = 0
        while True:
            self.path.append(index)
            self.parse_value(collect)
            self.path.pop()
            index += 1
            self._skip_ws()
            if self._consume(0x2C):
                continue
            if not self._consume(0x5D):
                raise ValueError(f"missing array end at byte {self.pos}")
            return

    def _add_excluded_member_edits(self, members: list[tuple[int, int, int, int, bool]]) -> None:
        start = 0
        while start < len(members):
            if not members[start][4]:
                start += 1
                continue
            end = start
            while end + 1 < len(members) and members[end + 1][4]:
                end += 1
            m_start, m_end = members[start], members[end]
            if end + 1 < len(members):
                self._add_edit(m_start[0], m_end[3] + 1)
            elif start > 0 and end > start:
                # Native quirk: a trailing run of several dispatch members keeps
                # the comma that precedes it in the hash view.
                self._add_edit(m_start[0], m_end[1])
            elif start > 0:
                self._add_edit(m_start[2], m_end[1])
            else:
                self._add_edit(m_start[0], m_end[1])
            start = end + 1

    # -- driver ------------------------------------------------------------

    def run(self) -> bytes:
        self.parse_value(True)
        self._skip_ws()
        if self.pos != len(self.body):
            raise ValueError(f"unexpected JSON data at byte {self.pos}")
        self.edits.sort()
        out = bytearray()
        last = 0
        for start, end in self.edits:
            if start < last:
                raise ValueError(f"overlapping CCH normalization edit at byte {start}")
            out += self.body[last:start]
            last = end
        out += self.body[last:]
        return bytes(out)


_CCH_DIGITS = re.compile(rb"cch=([0-9a-f]{5});")


def locate_cch_digits(body: bytes) -> int | None:
    """Byte offset of the 5 cch digits inside ``system[0].text``, if present."""
    scanner = _JsonScanner(body)
    try:
        scanner.parse_value(False)
    except ValueError:
        return None
    span = scanner.system_text_span
    if span is None:
        return None
    raw = body[span[0] : span[1]]
    if not raw[1:].startswith(BILLING_HEADER_PREFIX.encode()):
        return None
    match = _CCH_DIGITS.search(raw)
    if match is None:
        return None
    return span[0] + match.start(1)


def sign_body(body: bytes) -> bytes:
    """Fill the ``cch`` digits of the billing block; other bytes are untouched."""
    offset = locate_cch_digits(body)
    if offset is None:
        return body
    unsigned = bytearray(body)
    unsigned[offset : offset + 5] = CCH_PLACEHOLDER.encode()
    normalized = _JsonScanner(bytes(unsigned)).run()
    digest = xxh64(normalized, CCH_SEED) & 0xFFFFF
    unsigned[offset : offset + 5] = f"{digest:05x}".encode()
    return bytes(unsigned)


# ---------------------------------------------------------------------------
# Tool-name obfuscation (cc-mimicry / Parrot lineage)
# ---------------------------------------------------------------------------

STATIC_TOOL_NAME_REWRITES = {"sessions_": "cc_sess_", "session_": "cc_ses_"}
FAKE_TOOL_NAME_PREFIXES = (
    "analyze_", "compute_", "fetch_", "generate_", "lookup_", "modify_",
    "process_", "query_", "render_", "resolve_", "sync_", "update_",
    "validate_", "convert_", "extract_", "manage_", "monitor_", "parse_",
    "review_", "search_", "transform_", "handle_", "invoke_", "notify_",
)  # fmt: skip
DYNAMIC_TOOL_MAP_THRESHOLD = 5


@dataclass(slots=True)
class ToolNameRewrite:
    forward: dict[str, str]
    reverse_ordered: list[tuple[str, str]]


def _fnv1a64(names: list[str]) -> int:
    h = 0xCBF29CE484222325
    for i, name in enumerate(names):
        data = (b"\x00" if i else b"") + name.encode()
        for byte in data:
            h ^= byte
            h = (h * 0x100000001B3) & _M64
    return h


def _build_dynamic_tool_map(names: list[str]) -> dict[str, str] | None:
    if len(names) <= DYNAMIC_TOOL_MAP_THRESHOLD:
        return None
    rng = random.Random(_fnv1a64(names))
    prefixes = list(FAKE_TOOL_NAME_PREFIXES)
    rng.shuffle(prefixes)
    return {name: f"{prefixes[i % len(prefixes)]}{name[:3]}{i:02d}" for i, name in enumerate(names)}


def _should_rewrite_tool(tool: dict[str, Any]) -> bool:
    # Server tools (web_search_20250305, ...) are protocol names, never renamed.
    return tool.get("type", "") in ("", "function", "custom") and bool(tool.get("name"))


def build_tool_name_rewrite(tools: Any) -> ToolNameRewrite | None:
    if not isinstance(tools, list):
        return None
    names = [t["name"] for t in tools if isinstance(t, dict) and _should_rewrite_tool(t)]
    dynamic = _build_dynamic_tool_map(names)
    forward: dict[str, str] = {}
    for name in names:
        fake = name
        if dynamic and name in dynamic:
            fake = dynamic[name]
        else:
            for prefix, replacement in STATIC_TOOL_NAME_REWRITES.items():
                if name.startswith(prefix):
                    fake = replacement + name[len(prefix) :]
                    break
        if fake != name:
            forward[name] = fake
    if not forward:
        return None
    reverse = sorted(((fake, real) for real, fake in forward.items()), key=lambda p: len(p[0]), reverse=True)
    return ToolNameRewrite(forward=forward, reverse_ordered=reverse)


def apply_tool_name_rewrite(body: dict[str, Any], rewrite: ToolNameRewrite) -> None:
    for tool in body.get("tools", []) if isinstance(body.get("tools"), list) else []:
        if isinstance(tool, dict) and _should_rewrite_tool(tool) and tool["name"] in rewrite.forward:
            tool["name"] = rewrite.forward[tool["name"]]
    tool_choice = body.get("tool_choice")
    if isinstance(tool_choice, dict) and tool_choice.get("type") == "tool":
        tool_choice["name"] = rewrite.forward.get(tool_choice.get("name"), tool_choice.get("name"))
    for message in body.get("messages", []):
        if not isinstance(message, dict) or not isinstance(message.get("content"), list):
            continue
        for block in message["content"]:
            if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") in rewrite.forward:
                block["name"] = rewrite.forward[block["name"]]


def restore_tool_names(data: bytes, rewrite: ToolNameRewrite | None) -> bytes:
    if not data:
        return data
    if rewrite is not None:
        for fake, real in rewrite.reverse_ordered:
            data = data.replace(fake.encode(), real.encode())
    for prefix, replacement in STATIC_TOOL_NAME_REWRITES.items():
        data = data.replace(replacement.encode(), prefix.encode())
    return data


class _RestoringStream(httpx.AsyncByteStream):
    """Reverses tool aliases on a response stream, SSE event by event.

    The wrapped stream is the raw wire stream, so a compressed response is
    decoded here first; the caller drops the content-encoding header.
    """

    def __init__(self, inner: httpx.AsyncByteStream, rewrite: ToolNameRewrite | None, encoding: str) -> None:
        from httpx._decoders import SUPPORTED_DECODERS

        self._inner = inner
        self._rewrite = rewrite
        decoder_cls = SUPPORTED_DECODERS.get(encoding.strip().lower() or "identity")
        self._decoder = decoder_cls() if decoder_cls is not None else None

    async def __aiter__(self) -> AsyncIterator[bytes]:
        buffer = b""
        async for chunk in self._inner:
            if self._decoder is not None:
                chunk = self._decoder.decode(chunk)
            buffer += chunk
            while (cut := buffer.find(b"\n\n")) != -1:
                yield restore_tool_names(buffer[: cut + 2], self._rewrite)
                buffer = buffer[cut + 2 :]
        if self._decoder is not None:
            buffer += self._decoder.flush()
        if buffer:
            yield restore_tool_names(buffer, self._rewrite)

    async def aclose(self) -> None:
        await self._inner.aclose()


def _restore_response(response: httpx.Response, rewrite: ToolNameRewrite | None) -> None:
    encoding = response.headers.get("content-encoding", "identity")
    response.stream = _RestoringStream(response.stream, rewrite, encoding)  # type: ignore[arg-type]
    response.headers.pop("content-encoding", None)
    response.headers.pop("content-length", None)


# ---------------------------------------------------------------------------
# httpx transport
# ---------------------------------------------------------------------------

MESSAGES_PATH = "/v1/messages"


class ClaudeCodeTransport(httpx.AsyncBaseTransport):
    """httpx transport wrapper that applies the mimicry to every Anthropic request."""

    def __init__(
        self,
        inner: httpx.AsyncBaseTransport,
        identity: ClaudeCodeIdentity,
        *,
        obfuscate_tool_names: bool = False,
        today: Callable[[], date] = date.today,
    ) -> None:
        self._inner = inner
        self.identity = identity
        self.obfuscate_tool_names = obfuscate_tool_names
        self._today = today

    def prepare(self, request: httpx.Request, content: bytes | None) -> tuple[httpx.Request, ToolNameRewrite | None]:
        """Build the outbound request; ``content`` is the original JSON body (or None)."""
        rewrite: ToolNameRewrite | None = None
        betas = build_betas(None)
        data: bytes | None = None
        if request.method == "POST" and request.url.path == MESSAGES_PATH and content:
            payload = json.loads(content)
            payload = cloak_messages_body(payload, self.identity, today=self._today())
            if self.obfuscate_tool_names and (rewrite := build_tool_name_rewrite(payload.get("tools"))):
                apply_tool_name_rewrite(payload, rewrite)
            betas = build_betas(payload)
            data = sign_body(serialize_body(payload))
        elif content:
            data = content
        headers = build_headers(
            request.headers,
            self.identity,
            betas=betas,
            content_length=len(data) if data is not None else None,
            host=request.url.netloc.decode(),
        )
        outbound = httpx.Request(
            request.method,
            request.url,
            headers=headers,
            content=data,
            extensions=request.extensions,
        )
        return outbound, rewrite

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        content = await request.aread() if request.method in ("POST", "PUT", "PATCH") else None
        outbound, rewrite = self.prepare(request, content)
        response = await self._inner.handle_async_request(outbound)
        if rewrite is not None or self.obfuscate_tool_names:
            _restore_response(response, rewrite)
        return response

    async def aclose(self) -> None:
        await self._inner.aclose()
