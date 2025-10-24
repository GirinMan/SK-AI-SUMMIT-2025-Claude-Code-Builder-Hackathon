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

        for routine in ROUTINES:
            @self.mcp.tool(name=routine.name)
            async def _tool(routine=routine):
                return await self.state.perform_break(routine)

    def run(self, *, transport: str = "stdio") -> None:
        """FastMCP 서버를 실행한다."""

        self.mcp.run(transport=transport)


def create_server(
    *, boss_alertness: int = 35, boss_alertness_cooldown: int = 120, rng_seed: int | None = None
) -> ChillServer:
    """외부에서 사용하기 위한 ChillServer 생성 팩토리."""

    return ChillServer(
        boss_alertness=boss_alertness,
        boss_alertness_cooldown=boss_alertness_cooldown,
        rng_seed=rng_seed,
    )
