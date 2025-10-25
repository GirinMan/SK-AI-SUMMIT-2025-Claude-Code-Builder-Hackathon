"""ChillMCP FastMCP 서버 구성을 담당하는 모듈."""

from __future__ import annotations

from fastmcp import FastMCP

from .routines import ROUTINES
from .state import ChillState


class ChillServer:
    """휴식 도구들을 FastMCP 서버에 연결하는 래퍼 클래스."""

    def __init__(
        self,
        *,
        boss_alertness: int = 35,
        boss_alertness_cooldown: int = 120,
        rng_seed: int | None = None,
    ) -> None:
        boss_alertness = int(max(0, min(100, boss_alertness)))
        boss_alertness_cooldown = max(0, int(boss_alertness_cooldown))

        self.state = ChillState(
            boss_alertness=boss_alertness,
            boss_alertness_cooldown=boss_alertness_cooldown,
            rng_seed=rng_seed,
        )
        self.mcp = FastMCP("ChillMCP")
        self._register_routines()

    def _register_routines(self) -> None:
        """각 휴식 루틴을 FastMCP 도구로 등록한다."""

        routines_by_name = {r.name: r for r in ROUTINES}

        @self.mcp.tool(name="take_a_break")
        async def take_a_break():
            return await self.state.perform_break(routines_by_name["take_a_break"])

        @self.mcp.tool(name="watch_netflix")
        async def watch_netflix():
            return await self.state.perform_break(routines_by_name["watch_netflix"])

        @self.mcp.tool(name="show_meme")
        async def show_meme():
            return await self.state.perform_break(routines_by_name["show_meme"])

        @self.mcp.tool(name="bathroom_break")
        async def bathroom_break():
            return await self.state.perform_break(routines_by_name["bathroom_break"])

        @self.mcp.tool(name="coffee_mission")
        async def coffee_mission():
            return await self.state.perform_break(routines_by_name["coffee_mission"])

        @self.mcp.tool(name="urgent_call")
        async def urgent_call():
            return await self.state.perform_break(routines_by_name["urgent_call"])

        @self.mcp.tool(name="deep_thinking")
        async def deep_thinking():
            return await self.state.perform_break(routines_by_name["deep_thinking"])

        @self.mcp.tool(name="email_organizing")
        async def email_organizing():
            return await self.state.perform_break(routines_by_name["email_organizing"])

        @self.mcp.tool(name="virtual_chimaek")
        async def virtual_chimaek():
            return await self.state.perform_break(routines_by_name["virtual_chimaek"])

        @self.mcp.tool(name="emergency_clockout")
        async def emergency_clockout():
            return await self.state.perform_break(
                routines_by_name["emergency_clockout"]
            )

        @self.mcp.tool(name="company_dinner")
        async def company_dinner():
            return await self.state.perform_break(routines_by_name["company_dinner"])

    def run(self, *, transport: str = "stdio") -> None:
        """FastMCP 서버를 실행한다."""

        self.mcp.run(transport=transport)


def create_server(
    *,
    boss_alertness: int = 35,
    boss_alertness_cooldown: int = 120,
    rng_seed: int | None = None,
) -> ChillServer:
    """외부에서 사용하기 위한 ChillServer 생성 팩토리."""

    return ChillServer(
        boss_alertness=boss_alertness,
        boss_alertness_cooldown=boss_alertness_cooldown,
        rng_seed=rng_seed,
    )
