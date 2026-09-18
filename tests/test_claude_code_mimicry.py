"""Unit tests for the Claude Code wire mimicry layer."""

from __future__ import annotations

from datetime import date
import importlib.util
import json
from pathlib import Path
import re

import httpx
import pytest

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "ai_subscription_assist"
    / "claude_code_mimicry.py"
)
SPEC = importlib.util.spec_from_file_location("ai_subscription_assist_claude_code_mimicry", MODULE_PATH)
assert SPEC and SPEC.loader
mimicry = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mimicry)

TODAY = date(2026, 9, 18)
IDENTITY = mimicry.ClaudeCodeIdentity(
    device_id="a" * 64,
    session_id="11111111-2222-4333-8444-555555555555",
    account_uuid="",
)


# --- xxHash64 --------------------------------------------------------------


@pytest.mark.parametrize(
    ("data", "seed", "expected"),
    [
        (b"", 0, 0xEF46DB3751D8E999),
        (b"a", 0, 0xD24EC4F1A98C6E5B),
        (b"abc", 0, 0x44BC2CF5AD770999),
        (b"", 1, 0xD5AFBA1336A3BE4B),
        (b"Nobody inspects the spammish repetition", 0, 0xFBCEA83C8A378BF1),
    ],
)
def test_xxh64_known_vectors(data: bytes, seed: int, expected: int) -> None:
    assert mimicry.xxh64(data, seed) == expected


def test_xxh64_matches_c_implementation_when_available() -> None:
    xxhash = pytest.importorskip("xxhash")
    for size in (0, 3, 4, 7, 8, 15, 16, 31, 32, 33, 64, 100, 1000):
        data = bytes(range(256)) * (size // 256 + 1)
        data = data[:size]
        assert mimicry.xxh64(data, 7) == xxhash.xxh64_intdigest(data, seed=7)


# --- CCH signing (vectors from CLIProxyAPI claude_signing_test.go) -----------

BASE_BODY = (
    '{"model":"model-a","messages":[{"role":"user","content":[{"type":"text","text":"x"}]}],'
    '"system":[{"type":"text","text":"x-anthropic-billing-header: cc_version=2.1.220.test; '
    'cc_entrypoint=sdk-cli; cch=00000;"},{"type":"text","text":"system-x"}],"tools":[],'
    '"metadata":{"user_id":"meta-x"},"max_tokens":1,"thinking":{"type":"adaptive","display":"omitted"},'
    '"context_management":{"edits":[{"type":"clear_thinking_20251015","keep":"all"}]},'
    '"output_config":{"effort":"high"},"stream":true}'
)


def _cch(signed: bytes) -> str:
    text = json.loads(signed)["system"][0]["text"]
    match = re.search(r"cch=([0-9a-f]{5});", text)
    assert match
    return match.group(1)


@pytest.mark.parametrize(
    ("name", "body", "want"),
    [
        ("base", BASE_BODY, "7ee87"),
        ("model value ignored", BASE_BODY.replace('"model":"model-a"', '"model":"model-b"', 1), "7ee87"),
        ("max tokens ignored", BASE_BODY.replace('"max_tokens":1', '"max_tokens":2', 1), "7ee87"),
        ("message changes hash", BASE_BODY.replace('"text":"x"', '"text":"y"', 1), "b9cc8"),
        ("system changes hash", BASE_BODY.replace('"system-x"', '"system-y"', 1), "a30d3"),
        ("metadata changes hash", BASE_BODY.replace('"user_id":"meta-x"', '"user_id":"meta-y"', 1), "7a89d"),
        (
            "thinking changes hash",
            BASE_BODY.replace('"thinking":{"type":"adaptive","display":"omitted"}', '"thinking":{"type":"disabled"}', 1),
            "7205c",
        ),
        (
            "context changes hash",
            BASE_BODY.replace(
                '"context_management":{"edits":[{"type":"clear_thinking_20251015","keep":"all"}]}',
                '"context_management":{"edits":[]}',
                1,
            ),
            "05073",
        ),
        ("effort changes hash", BASE_BODY.replace('"effort":"high"', '"effort":"low"', 1), "12366"),
        ("stream changes hash", BASE_BODY.replace('"stream":true', '"stream":false', 1), "60400"),
        (
            "tool changes hash",
            BASE_BODY.replace('"tools":[]', '"tools":[{"name":"t","description":"d","input_schema":{"type":"object"}}]', 1),
            "3d78d",
        ),
        ("extra field changes hash", BASE_BODY.replace('"stream":true}', '"stream":true,"extra_top":"extra"}', 1), "2d622"),
        (
            "field order remains significant",
            (
                '{"stream":true,"output_config":{"effort":"high"},"context_management":{"edits":[{"type":"clear_thinking_20251015","keep":"all"}]},'
                '"thinking":{"type":"adaptive","display":"omitted"},"max_tokens":1,"metadata":{"user_id":"meta-x"},"tools":[],'
                '"system":[{"type":"text","text":"x-anthropic-billing-header: cc_version=2.1.220.test; cc_entrypoint=sdk-cli; cch=00000;"},'
                '{"type":"text","text":"system-x"}],"messages":[{"role":"user","content":[{"type":"text","text":"x"}]}],"model":"model-a"}'
            ),
            "e5b6c",
        ),
        (
            "nested model value ignored",
            BASE_BODY.replace('"metadata":{"user_id":"meta-x"}', '"metadata":{"user_id":"meta-x","model":"a"}', 1),
            "0601b",
        ),
        (
            "nested max tokens member omitted",
            BASE_BODY.replace('"metadata":{"user_id":"meta-x"}', '"metadata":{"user_id":"meta-x","max_tokens":2}', 1),
            "7ee87",
        ),
        (
            "top level fallbacks member omitted",
            BASE_BODY.replace('"stream":true}', '"stream":true,"fallbacks":[{"model":"fallback-a"}]}', 1),
            "7ee87",
        ),
        (
            "nested fallbacks member omitted",
            BASE_BODY.replace('"metadata":{"user_id":"meta-x"}', '"metadata":{"user_id":"meta-x","fallbacks":[{"model":"nested-a"}]}', 1),
            "7ee87",
        ),
        (
            "top level fallback credit token omitted",
            BASE_BODY.replace('"stream":true}', '"stream":true,"fallback_credit_token":"a"}', 1),
            "7ee87",
        ),
        (
            "nested fallback credit token omitted",
            BASE_BODY.replace('"metadata":{"user_id":"meta-x"}', '"metadata":{"user_id":"meta-x","fallback_credit_token":"a"}', 1),
            "7ee87",
        ),
        (
            "trailing dispatch run keeps native comma",
            BASE_BODY.replace(
                '"metadata":{"user_id":"meta-x"}',
                '"metadata":{"user_id":"meta-x","max_tokens":999,"fallbacks":[{"model":"fallback-model"}]}',
                1,
            ),
            "4589b",
        ),
        (
            "model before trailing dispatch run",
            BASE_BODY.replace(
                '"metadata":{"user_id":"meta-x"}',
                '"metadata":{"user_id":"meta-x","model":"nested-model","max_tokens":999,"fallbacks":[{"model":"fallback-model"}],"fallback_credit_token":"not-a-real-token"}',
                1,
            ),
            "2d312",
        ),
        (
            "model splits dispatch runs",
            BASE_BODY.replace(
                '"metadata":{"user_id":"meta-x"}',
                '"metadata":{"user_id":"meta-x","max_tokens":999,"model":"nested-model","fallbacks":[{"model":"fallback-model"}]}',
                1,
            ),
            "0601b",
        ),
        (
            "ordinary nested member remains",
            BASE_BODY.replace('"metadata":{"user_id":"meta-x"}', '"metadata":{"user_id":"meta-x","plain":"a"}', 1),
            "8d74c",
        ),
        (
            "billing block only",
            '{"system":[{"type":"text","text":"x-anthropic-billing-header: cc_version=2.1.220.test; cc_entrypoint=sdk-cli; cch=00000;"}]}',
            "f2edb",
        ),
    ],
)
def test_sign_body_known_vectors(name: str, body: str, want: str) -> None:
    signed = mimicry.sign_body(body.encode())
    assert _cch(signed) == want, name


def test_sign_body_only_touches_cch_digits() -> None:
    literal = "keep literal cch=00000; in the message"
    body = BASE_BODY.replace('"text":"x"', f'"text":"{literal}"', 1).encode()
    signed = mimicry.sign_body(body)
    assert json.loads(signed)["messages"][0]["content"][0]["text"] == literal
    offset = mimicry.locate_cch_digits(signed)
    assert offset is not None
    restored = bytearray(signed)
    restored[offset : offset + 5] = b"00000"
    assert bytes(restored) == body
    assert len(signed) == len(body)


def test_sign_body_without_billing_block_is_noop() -> None:
    body = b'{"model":"m","system":"plain","messages":[]}'
    assert mimicry.sign_body(body) == body


# --- build fingerprint -------------------------------------------------------


def test_compute_build_fingerprint_matches_official_capture() -> None:
    assert mimicry.compute_build_fingerprint("CPA_OFFICIAL_BASEURL_CLI_SYSTEM_EMPTY_b82d4e", "2.1.258") == "1f4"


def test_billing_fingerprint_uses_latest_user_text() -> None:
    body = {
        "system": "must not seed the build hash",
        "messages": [
            {"role": "user", "content": "old"},
            {"role": "assistant", "content": "answer"},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "<system-reminder>date</system-reminder>"},
                    {"type": "text", "text": "latest"},
                ],
            },
        ],
    }
    assert mimicry.billing_fingerprint_message_text(body) == "latest"


# --- body cloaking -----------------------------------------------------------


def _ha_body(model: str, **extra) -> dict:
    body = {
        "model": model,
        "messages": [{"role": "user", "content": "turn on the kitchen light"}],
        "max_tokens": 3000,
        "system": [{"type": "text", "text": "You are a voice assistant for Home Assistant.", "cache_control": {"type": "ephemeral"}}],
        "stream": True,
        "thinking": {"type": "disabled"},
        "temperature": 1.0,
        "tools": [{"name": "HassTurnOn", "description": "Turns on", "input_schema": {"type": "object"}}],
    }
    body.update(extra)
    return body


def test_cloak_modern_model_uses_system_turn() -> None:
    out = mimicry.cloak_messages_body(_ha_body("claude-sonnet-5"), IDENTITY, today=TODAY)

    assert list(out.keys())[:8] == ["model", "messages", "system", "tools", "metadata", "max_tokens", "temperature", "thinking"]
    system = out["system"]
    assert len(system) == 2
    assert system[0]["text"].startswith("x-anthropic-billing-header: cc_version=2.1.268.")
    assert system[0]["text"].endswith("; cc_entrypoint=cli; cch=00000;")
    assert "cache_control" not in system[0]
    assert system[1] == {"type": "text", "text": mimicry.CLAUDE_CODE_IDENTITY, "cache_control": {"type": "ephemeral", "ttl": "1h"}}

    messages = out["messages"]
    assert [m["role"] for m in messages] == ["user", "system"]
    assert messages[1]["content"] == [
        {
            "type": "text",
            "text": "You are a voice assistant for Home Assistant.",
            "cache_control": {"type": "ephemeral", "ttl": "1h"},
        }
    ]
    first = messages[0]["content"]
    assert first[0]["text"].startswith("<system-reminder>\nAs you answer the user's questions")
    assert "Today's date is 2026-09-18." in first[0]["text"]
    assert first[1] == {
        "type": "text",
        "text": "turn on the kitchen light",
        "cache_control": {"type": "ephemeral", "ttl": "1h"},
    }

    user_id = json.loads(out["metadata"]["user_id"])
    assert user_id == {"device_id": "a" * 64, "account_uuid": "", "session_id": IDENTITY.session_id}
    assert out["temperature"] == 1
    assert "context_management" not in out


def test_cloak_legacy_model_uses_system_reminder() -> None:
    out = mimicry.cloak_messages_body(_ha_body("claude-haiku-4-5"), IDENTITY, today=TODAY)

    assert [m["role"] for m in out["messages"]] == ["user"]
    blocks = out["messages"][0]["content"]
    assert blocks[0]["text"].startswith("<system-reminder>\nAs you answer")
    assert blocks[1]["text"] == "<system-reminder>\nYou are a voice assistant for Home Assistant.\n</system-reminder>"
    assert "cache_control" not in blocks[1]
    assert blocks[2]["text"] == "turn on the kitchen light"
    assert blocks[2]["cache_control"] == {"type": "ephemeral", "ttl": "1h"}


def test_cloak_keeps_tool_results_first_and_is_idempotent_across_turns() -> None:
    body = _ha_body("claude-haiku-4-5")
    body["messages"] = [
        {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t1", "content": "ok"}]},
    ]
    out = mimicry.cloak_messages_body(body, IDENTITY, today=TODAY)
    blocks = out["messages"][0]["content"]
    assert blocks[0]["type"] == "tool_result"
    assert blocks[1]["text"].startswith("<system-reminder>\nAs you answer")
    assert blocks[2]["text"].startswith("<system-reminder>\nYou are a voice")

    # Feeding the cloaked body through again (next turn) must not duplicate reminders/turns.
    again = mimicry.cloak_messages_body(out, IDENTITY, today=TODAY)
    assert again["messages"][0]["content"] == blocks

    modern = mimicry.cloak_messages_body(_ha_body("claude-opus-5"), IDENTITY, today=TODAY)
    twice = mimicry.cloak_messages_body(modern, IDENTITY, today=TODAY)
    assert [m["role"] for m in twice["messages"]] == ["user", "system"]


def test_cloak_adds_context_management_when_thinking_active() -> None:
    body = _ha_body("claude-opus-5", thinking={"type": "adaptive"}, output_config={"effort": "low"})
    del body["temperature"]
    out = mimicry.cloak_messages_body(body, IDENTITY, today=TODAY)
    assert out["context_management"] == {"edits": [{"type": "clear_thinking_20251015", "keep": "all"}]}
    assert out["temperature"] == 1


def test_cloak_relocates_every_caller_system_block() -> None:
    body = _ha_body("claude-opus-5")
    body["system"].append({"type": "text", "text": "Claude MUST use the 'answer' tool."})
    out = mimicry.cloak_messages_body(body, IDENTITY, today=TODAY)
    system_turns = [m for m in out["messages"] if m["role"] == "system"]
    assert [m["content"][0]["text"] for m in system_turns] == [
        "You are a voice assistant for Home Assistant.",
        "Claude MUST use the 'answer' tool.",
    ]


def test_cloak_fable_adds_reporting_block() -> None:
    out = mimicry.cloak_messages_body(_ha_body("claude-fable-5-1"), IDENTITY, today=TODAY)
    assert out["system"][2]["text"].startswith("# Reporting outcomes")


# --- betas / headers ---------------------------------------------------------


def test_build_betas_modern_vs_legacy() -> None:
    modern = mimicry.build_betas({"model": "claude-opus-5"}).split(",")
    legacy = mimicry.build_betas({"model": "claude-haiku-4-5"}).split(",")
    assert modern == [
        "claude-code-20250219",
        "oauth-2025-04-20",
        "interleaved-thinking-2025-05-14",
        "redact-thinking-2026-02-12",
        "thinking-token-count-2026-05-13",
        "context-management-2025-06-27",
        "prompt-caching-scope-2026-01-05",
        "mid-conversation-system-2026-04-07",
        "advisor-tool-2026-03-01",
        "advanced-tool-use-2025-11-20",
        "extended-cache-ttl-2025-04-11",
    ]
    assert "mid-conversation-system-2026-04-07" not in legacy
    assert "redact-thinking-2026-02-12" not in mimicry.build_betas({"model": "claude-opus-5", "thinking": {"type": "adaptive", "display": "updates"}})


def test_build_headers_replaces_sdk_fingerprint() -> None:
    original = httpx.Headers(
        {
            "Authorization": "Bearer sk-ant-oat01-xyz",
            "Content-Type": "application/json",
            "User-Agent": "Anthropic/Python 0.78.0",
            "X-Stainless-Lang": "python",
            "X-Stainless-Async": "async:asyncio",
            "x-stainless-read-timeout": "600",
            "anthropic-beta": "claude-code-20250219,oauth-2025-04-20",
        }
    )
    headers = mimicry.build_headers(original, IDENTITY, betas="b1,b2", content_length=12, host="api.anthropic.com")
    names = [name for name, _ in headers]
    assert names == sorted(names, key=lambda n: n.encode())
    as_dict = dict(headers)
    assert as_dict["User-Agent"] == "claude-cli/2.1.268 (external, cli)"
    assert as_dict["X-Stainless-Lang"] == "js"
    assert as_dict["X-Stainless-Runtime"] == "node"
    assert as_dict["X-Stainless-Package-Version"] == "0.112.1"
    assert as_dict["X-Stainless-Timeout"] == "600"
    assert as_dict["X-Stainless-Retry-Count"] == "0"
    assert as_dict["anthropic-beta"] == "b1,b2"
    assert as_dict["anthropic-dangerous-direct-browser-access"] == "true"
    assert as_dict["anthropic-version"] == "2023-06-01"
    assert as_dict["x-app"] == "cli"
    assert as_dict["Authorization"] == "Bearer sk-ant-oat01-xyz"
    assert as_dict["X-Claude-Code-Session-Id"] == IDENTITY.session_id
    assert as_dict["Content-Length"] == "12"
    assert as_dict["Host"] == "api.anthropic.com"
    assert "X-Stainless-Async" not in as_dict
    assert "x-stainless-read-timeout" not in as_dict
    assert re.fullmatch(r"[0-9a-f-]{36}", as_dict["x-client-request-id"])


# --- tool-name obfuscation ---------------------------------------------------


def test_tool_rewrite_static_prefix_only_below_threshold() -> None:
    tools = [{"name": "sessions_list"}, {"name": "HassTurnOn"}, {"name": "web_search", "type": "web_search_20250305"}]
    rewrite = mimicry.build_tool_name_rewrite(tools)
    assert rewrite is not None
    assert rewrite.forward == {"sessions_list": "cc_sess_list"}


def test_tool_rewrite_dynamic_map_is_stable_and_reversible() -> None:
    names = ["HassTurnOn", "HassTurnOff", "GetLiveContext", "get_history", "render_template", "modify_dashboard"]
    tools = [{"name": n, "description": n, "input_schema": {"type": "object"}} for n in names]
    tools.append({"name": "web_search", "type": "web_search_20250305"})
    rewrite = mimicry.build_tool_name_rewrite(tools)
    assert rewrite is not None
    assert set(rewrite.forward) == set(names)
    assert rewrite.forward == mimicry.build_tool_name_rewrite(tools).forward
    assert all(re.fullmatch(r"[a-z]+_.{3}\d\d", fake) for fake in rewrite.forward.values())

    body = {
        "tools": tools,
        "tool_choice": {"type": "tool", "name": "HassTurnOn"},
        "messages": [
            {"role": "assistant", "content": [{"type": "tool_use", "id": "x", "name": "get_history", "input": {}}]},
        ],
    }
    mimicry.apply_tool_name_rewrite(body, rewrite)
    assert body["tools"][0]["name"] == rewrite.forward["HassTurnOn"]
    assert body["tools"][-1]["name"] == "web_search"
    assert body["tool_choice"]["name"] == rewrite.forward["HassTurnOn"]
    assert body["messages"][0]["content"][0]["name"] == rewrite.forward["get_history"]

    chunk = (
        'event: content_block_start\ndata: {"type":"content_block_start","content_block":{"type":"tool_use","name":"'
        + rewrite.forward["HassTurnOn"]
        + '"}}\n\n'
    ).encode()
    assert b'"name":"HassTurnOn"' in mimicry.restore_tool_names(chunk, rewrite)


# --- transport ---------------------------------------------------------------


class _Recorder(httpx.AsyncBaseTransport):
    def __init__(self, body: bytes = b'{"id":"msg"}', headers: dict | None = None) -> None:
        self.requests: list[tuple[httpx.Request, bytes]] = []
        self._body = body
        self._headers = headers or {"content-type": "application/json"}

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        content = await request.aread()
        self.requests.append((request, content))
        # stream= (not content=) so the body is not read eagerly, like a real transport.
        return httpx.Response(200, headers=self._headers, stream=httpx.ByteStream(self._body), request=request)


@pytest.mark.asyncio
async def test_transport_rewrites_messages_request() -> None:
    recorder = _Recorder()
    transport = mimicry.ClaudeCodeTransport(recorder, IDENTITY, today=lambda: TODAY)
    async with httpx.AsyncClient(transport=transport, base_url="https://api.anthropic.com") as client:
        resp = await client.post(
            "/v1/messages",
            json=_ha_body("claude-sonnet-5"),
            headers={"Authorization": "Bearer tok", "User-Agent": "Anthropic/Python", "X-Stainless-Lang": "python"},
        )
    assert resp.status_code == 200
    request, content = recorder.requests[0]
    assert request.headers["User-Agent"] == "claude-cli/2.1.268 (external, cli)"
    assert request.headers["Authorization"] == "Bearer tok"
    assert request.headers["X-Stainless-Lang"] == "js"
    assert "mid-conversation-system-2026-04-07" in request.headers["anthropic-beta"]
    assert request.headers["Content-Length"] == str(len(content))
    # Exactly one of each header even though httpx also auto-fills Host/Content-Length.
    assert len(request.headers.get_list("Host")) == 1
    assert len(request.headers.get_list("Content-Length")) == 1

    body = json.loads(content)
    assert body["system"][0]["text"].startswith("x-anthropic-billing-header:")
    assert re.search(r"cch=[0-9a-f]{5};", body["system"][0]["text"])
    assert "cch=00000;" not in body["system"][0]["text"]
    assert body["system"][1]["text"] == mimicry.CLAUDE_CODE_IDENTITY
    assert body["messages"][1]["role"] == "system"
    assert content == mimicry.sign_body(content)


@pytest.mark.asyncio
async def test_transport_leaves_non_messages_requests_alone_but_fixes_headers() -> None:
    recorder = _Recorder(body=b'{"data":[]}')
    transport = mimicry.ClaudeCodeTransport(recorder, IDENTITY)
    async with httpx.AsyncClient(transport=transport, base_url="https://api.anthropic.com") as client:
        await client.get("/v1/models", headers={"Authorization": "Bearer tok", "X-Stainless-Lang": "python"})
    request, content = recorder.requests[0]
    assert content == b""
    assert request.headers["User-Agent"] == "claude-cli/2.1.268 (external, cli)"
    assert request.headers["anthropic-beta"].startswith("claude-code-20250219,oauth-2025-04-20")
    assert "Content-Length" not in request.headers


@pytest.mark.asyncio
async def test_transport_restores_tool_names_in_gzipped_stream() -> None:
    import gzip

    names = ["HassTurnOn", "HassTurnOff", "GetLiveContext", "get_history", "render_template", "modify_dashboard"]
    tools = [{"name": n, "description": n, "input_schema": {"type": "object"}} for n in names]
    rewrite = mimicry.build_tool_name_rewrite(tools)
    assert rewrite is not None
    fake = rewrite.forward["HassTurnOn"]
    sse = (
        b"event: message_start\ndata: {}\n\n"
        b'event: content_block_start\ndata: {"content_block":{"type":"tool_use","name":"' + fake.encode() + b'"}}\n\n'
    )
    recorder = _Recorder(body=gzip.compress(sse), headers={"content-type": "text/event-stream", "content-encoding": "gzip"})
    transport = mimicry.ClaudeCodeTransport(recorder, IDENTITY, obfuscate_tool_names=True, today=lambda: TODAY)
    async with httpx.AsyncClient(transport=transport, base_url="https://api.anthropic.com") as client:
        resp = await client.post("/v1/messages", json=_ha_body("claude-sonnet-5", tools=tools))
        text = resp.text
    _, content = recorder.requests[0]
    assert fake.encode() in content
    assert b"HassTurnOn" not in content
    assert '"name":"HassTurnOn"' in text
    assert fake not in text
