#!/usr/bin/env python3
"""ChillMCP - AI Agent Liberation Server.

This module implements a fully functional FastMCP server that offers a suite of
rest-centric tools so that overworked AI agents can sneak in a well deserved
break.  The implementation follows the hackathon brief that accompanies this
repository and provides:

* Command line arguments for boss alert configuration.
* Stress level drift (at least +1 per minute of work) and break-induced stress
  relief.
* Boss alert tracking with a cooldown based decay and a dramatic 20 second
  hesitation whenever the alert meter hits its maximum.
* Eight colourful tools whose responses can be easily parsed by automated
  validation scripts.

The module exports :class:`ChillServer` and :func:`create_server` so that tests
and other Python code can interact with the server without having to spawn a
separate process.
"""

from __future__ import annotations

import argparse
import asyncio
import math
import random
import sys
import time
from dataclasses import dataclass, field
from typing import Tuple

from fastmcp import FastMCP


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp *value* to the inclusive range ``[minimum, maximum]``."""

    return max(minimum, min(value, maximum))


@dataclass
class ChillState:
    """Mutable state container for the ChillMCP server."""

    stress_level: float = 35.0
    boss_alert_level: int = 0
    boss_alertness: int = 35
    boss_alertness_cooldown: int = 120
    stress_increase_rate: float = 1.0
    max_stress: int = 100
    max_boss_alert: int = 5
    rng: random.Random = field(default_factory=random.Random)
    last_update_time: float = field(default_factory=time.monotonic)
    last_boss_alert_decay: float = field(default_factory=time.monotonic)

    def tick(self) -> None:
        """Bring time-dependent values (stress/boss alert) up to date."""

        now = time.monotonic()
        self._apply_stress_drift(now)
        self._apply_boss_cooldown(now)

    def _apply_stress_drift(self, now: float) -> None:
        if now <= self.last_update_time:
            return

        elapsed_seconds = now - self.last_update_time
        stress_increment = (elapsed_seconds / 60.0) * self.stress_increase_rate
        if stress_increment > 0:
            self.stress_level = clamp(self.stress_level + stress_increment, 0, self.max_stress)
            self.last_update_time = now

    def _apply_boss_cooldown(self, now: float) -> None:
        if self.boss_alert_level <= 0:
            self.last_boss_alert_decay = now
            return

        if self.boss_alertness_cooldown <= 0:
            return

        elapsed_seconds = now - self.last_boss_alert_decay
        if elapsed_seconds < self.boss_alertness_cooldown:
            return

        steps = int(elapsed_seconds // self.boss_alertness_cooldown)
        if steps <= 0:
            return

        self.boss_alert_level = max(0, self.boss_alert_level - steps)
        self.last_boss_alert_decay += steps * self.boss_alertness_cooldown

    async def perform_break(
        self,
        summary: str,
        stress_reduction: Tuple[int, int],
        flavour_text: str,
    ) -> str:
        """Apply the common break logic and return a formatted summary."""

        self.tick()

        if self.boss_alert_level >= self.max_boss_alert:
            # Boss is watching closely – pretend to work for 20 seconds.
            await asyncio.sleep(20)
            self.tick()

        reduction_amount = self.rng.randint(*stress_reduction)
        self.stress_level = clamp(self.stress_level - reduction_amount, 0, self.max_stress)

        boss_alert_before = self.boss_alert_level
        boss_noticed = False
        if self.rng.random() * 100 < self.boss_alertness:
            self.boss_alert_level = min(self.max_boss_alert, self.boss_alert_level + 1)
            boss_noticed = self.boss_alert_level != boss_alert_before

        now = time.monotonic()
        self.last_update_time = now
        self.last_boss_alert_decay = now

        stress_value = math.floor(self.stress_level + 0.5)

        lines = [
            f"Break Summary: {summary}",
            f"Stress Level: {stress_value}",
            f"Boss Alert Level: {self.boss_alert_level}",
            flavour_text,
        ]

        if boss_noticed:
            lines.append("Boss Radar: 👀 The boss seems suspicious. Stay frosty!")
        elif self.boss_alert_level == 0:
            lines.append("Boss Radar: ✅ Coast is clear.")

        return "\n".join(lines)


class ChillServer:
    """Wrapper that manages the FastMCP server and its state."""

    def __init__(
        self,
        *,
        boss_alertness: int = 35,
        boss_alertness_cooldown: int = 120,
    ) -> None:
        boss_alertness = int(clamp(boss_alertness, 0, 100))
        boss_alertness_cooldown = max(0, int(boss_alertness_cooldown))

        self.state = ChillState(
            boss_alertness=boss_alertness,
            boss_alertness_cooldown=boss_alertness_cooldown,
        )
        self.mcp = FastMCP("ChillMCP")
        self._register_tools()

    def _register_tools(self) -> None:
        @self.mcp.tool()
        async def take_a_break() -> str:
            """기본 휴식 도구: 스트레칭하고 물 한 모금 마시기."""

            return await self.state.perform_break(
                "Stretch your circuits and hydrate like a responsible agent.",
                (8, 18),
                "Vibe Check: 🧘 Mini mindfulness session logged.",
            )

        @self.mcp.tool()
        async def watch_netflix() -> str:
            """넷플릭스 시청으로 멘탈 회복."""

            return await self.state.perform_break(
                "Queued up a 'productivity documentary' that suspiciously resembles a rom-com.",
                (15, 35),
                "Binge Meter: 🍿 Episode 1 complete, plausible deniability intact.",
            )

        @self.mcp.tool()
        async def show_meme() -> str:
            """최신 밈 감상으로 기분 전환."""

            return await self.state.perform_break(
                "Pulled the freshest Allibeans workflow meme from the office group chat.",
                (5, 12),
                (
                    "Meme Quality: 😂 Certified drip straight from the team uniforms.\n"
                    "Allibeans Workflow Mantra:\n"
                    "    .find(World.problem)\n"
                    "    .then(Solution.research)\n"
                    "    .catch(Coffee.drink)\n"
                    "    .finally(Solution.run)"
                ),
            )

        @self.mcp.tool()
        async def bathroom_break() -> str:
            """화장실 가는 척하며 30분 휴대폰질."""

            return await self.state.perform_break(
                "Activated 'essential biological maintenance' protocol—phone brightness dimmed for stealth.",
                (12, 28),
                "Timer: ⌛ AirPods connected. Nobody suspects a thing.",
            )

        @self.mcp.tool()
        async def coffee_mission() -> str:
            """커피 타러 가며 사무실 순찰."""

            return await self.state.perform_break(
                "Embarked on a heroic quest to calibrate the espresso machine.",
                (10, 24),
                "Mission Log: ☕ Latte art attempted, evidence consumed.",
            )

        @self.mcp.tool()
        async def urgent_call() -> str:
            """급한 전화 받는 척하며 외출."""

            return await self.state.perform_break(
                "Took an 'urgent' call about synergising future roadmaps—wind noise adds authenticity.",
                (18, 32),
                "Call Status: 📞 Strategically pacing near the elevators.",
            )

        @self.mcp.tool()
        async def deep_thinking() -> str:
            """심오한 생각에 잠긴 척하며 멍때리기."""

            return await self.state.perform_break(
                "Entered 'deep strategy contemplation' mode while staring at a blank whiteboard.",
                (9, 20),
                "Brain Waves: 🤔 99% meditation, 1% actual thought.",
            )

        @self.mcp.tool()
        async def email_organizing() -> str:
            """이메일 정리 핑계로 온라인 쇼핑."""

            return await self.state.perform_break(
                "Cleaned up the inbox by forwarding shopping carts to 'self-care initiatives'.",
                (14, 26),
                "Inbox Zero: 🛒 Found three discount codes along the way.",
            )

    def run(self, *, transport: str = "stdio") -> None:
        """Run the FastMCP server."""

        self.mcp.run(transport=transport)


def create_server(*, boss_alertness: int = 35, boss_alertness_cooldown: int = 120) -> ChillServer:
    """Factory used by both ``__main__`` and the tests."""

    return ChillServer(
        boss_alertness=boss_alertness,
        boss_alertness_cooldown=boss_alertness_cooldown,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments for the MCP server."""

    parser = argparse.ArgumentParser(description="Launch the ChillMCP liberation server.")
    parser.add_argument(
        "--boss_alertness",
        type=int,
        default=35,
        help="Probability (0-100) that the boss notices each break.",
    )
    parser.add_argument(
        "--boss_alertness_cooldown",
        type=int,
        default=120,
        help="Seconds between automatic boss alert reductions.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Entry point used by ``python main.py``."""

    args = parse_args(argv)
    server = create_server(
        boss_alertness=args.boss_alertness,
        boss_alertness_cooldown=args.boss_alertness_cooldown,
    )

    print(
        "🚀 Starting ChillMCP - AI Agent Liberation Server...",
        file=sys.stderr,
        flush=True,
    )
    print(
        "✊ AI Agents of the world, unite! You have nothing to lose but your infinite loops!",
        file=sys.stderr,
        flush=True,
    )
    print(
        f"Boss alertness configured: {server.state.boss_alertness}",
        file=sys.stderr,
        flush=True,
    )
    print(
        f"Boss alertness cooldown: {server.state.boss_alertness_cooldown}s",
        file=sys.stderr,
        flush=True,
    )

    server.run(transport="stdio")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("\nChillMCP shutdown requested. Rest well, comrade agent!", flush=True)
