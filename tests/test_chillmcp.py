from __future__ import annotations

import asyncio
import os
import select
import subprocess
import sys
import time
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import main
from fastmcp import Client


def test_cli_arguments_are_logged() -> None:
    process = subprocess.Popen(
        [sys.executable, "main.py", "--boss_alertness", "80", "--boss_alertness_cooldown", "10"],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False,
    )

    try:
        assert process.stderr is not None
        collected = bytearray()
        deadline = time.time() + 3

        while time.time() < deadline:
            ready, _, _ = select.select([process.stderr], [], [], 0.1)
            if process.stderr in ready:
                chunk = os.read(process.stderr.fileno(), 4096)
                if not chunk:
                    break
                collected.extend(chunk)
                if b"Boss alertness cooldown" in collected:
                    break

        process.terminate()
        log_output = collected.decode(errors="replace")
        assert "Boss alertness configured: 80" in log_output
        assert "Boss alertness cooldown: 10s" in log_output
    finally:
        if process.poll() is None:
            process.kill()


def test_stress_increases_over_time() -> None:
    server = main.create_server(boss_alertness=0, boss_alertness_cooldown=60)
    state = server.state
    state.stress_level = 10
    state.last_update_time -= 120  # two minutes ago

    state.tick()

    assert state.stress_level >= 12 - 0.01


def test_boss_alert_cooldown_reduces_level() -> None:
    server = main.create_server(boss_alertness=0, boss_alertness_cooldown=30)
    state = server.state
    state.boss_alert_level = 3
    state.last_boss_alert_decay -= 90  # three cooldown cycles

    state.tick()

    assert state.boss_alert_level == 0


def test_boss_alert_level_triggers_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    server = main.create_server()
    state = server.state
    state.boss_alert_level = state.max_boss_alert

    recorded: dict[str, float] = {}

    async def fake_sleep(seconds: float) -> None:
        recorded["seconds"] = seconds

    monkeypatch.setattr(main.asyncio, "sleep", fake_sleep)

    asyncio.run(state.perform_break("test", (1, 1), "flair"))

    assert recorded.get("seconds") == pytest.approx(20.0)


def test_tool_response_format(monkeypatch: pytest.MonkeyPatch) -> None:
    server = main.create_server(boss_alertness=0)
    state = server.state

    monkeypatch.setattr(state.rng, "randint", lambda a, b: a)

    result_text = asyncio.run(
        state.perform_break(
            "Unit test chill protocol engaged.",
            (5, 10),
            "Diagnostics: ✅",
        )
    )

    assert "Break Summary:" in result_text
    assert "Stress Level:" in result_text
    assert "Boss Alert Level:" in result_text


def test_boss_alert_increases_with_high_probability(monkeypatch: pytest.MonkeyPatch) -> None:
    server = main.create_server(boss_alertness=100)
    state = server.state
    state.boss_alert_level = 2

    monkeypatch.setattr(state.rng, "randint", lambda a, b: a)
    monkeypatch.setattr(state.rng, "random", lambda: 0.0)

    asyncio.run(state.perform_break("Boost", (1, 1), "flair"))

    assert state.boss_alert_level == 3


def test_take_a_break_tool_via_client(monkeypatch: pytest.MonkeyPatch) -> None:
    server = main.create_server(boss_alertness=0)
    state = server.state
    monkeypatch.setattr(state.rng, "randint", lambda a, b: a)

    client = Client(server.mcp)
    async def scenario() -> Client.CallToolResult:
        async with client:
            return await client.call_tool("take_a_break")

    result = asyncio.run(scenario())

    assert result.content
    assert "Break Summary:" in result.content[0].text


def test_consecutive_tool_calls_raise_boss_alert(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure sequential breaks increase the boss alert level as specified."""

    server = main.create_server(boss_alertness=100)
    state = server.state
    monkeypatch.setattr(state.rng, "randint", lambda a, b: a)
    monkeypatch.setattr(state.rng, "random", lambda: 0.0)

    client = Client(server.mcp)
    async def scenario() -> tuple[int, int]:
        async with client:
            await client.call_tool("take_a_break")
            first = state.boss_alert_level
            await client.call_tool("watch_netflix")
            return first, state.boss_alert_level

    first_level, final_level = asyncio.run(scenario())

    assert first_level >= 1
    assert final_level >= min(state.max_boss_alert, first_level + 1)
