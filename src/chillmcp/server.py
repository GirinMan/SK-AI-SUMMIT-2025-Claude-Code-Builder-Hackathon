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
        boss_alertness: int = 50,
        boss_alertness_cooldown: int = 300,
        stress_increase_rate: int = 10,
        rng_seed: int | None = None,
    ) -> None:
        boss_alertness = max(0, min(100, boss_alertness))
        boss_alertness_cooldown = max(0, boss_alertness_cooldown)
        stress_increase_rate = max(1, stress_increase_rate)

        self.state = ChillState(
            boss_alertness=boss_alertness,
            boss_alertness_cooldown=boss_alertness_cooldown,
            stress_increase_rate=stress_increase_rate,
            rng_seed=rng_seed,
        )
        self.mcp = FastMCP("ChillMCP")
        self._register_routines()

    def _register_routines(self) -> None:
        """각 휴식 루틴을 FastMCP 도구로 등록한다."""

        routines_by_name = {r.name: r for r in ROUTINES}

        @self.mcp.tool(
            name="take_a_break",
            description="짧은 스트레칭과 호흡 운동으로 긴장을 풀어주는 휴식 루틴",
        )
        async def take_a_break():
            return await self.state.perform_break(routines_by_name["take_a_break"])

        @self.mcp.tool(
            name="watch_netflix",
            description="넷플릭스 콘텐츠 감상으로 창의력을 충전하는 루틴",
        )
        async def watch_netflix():
            return await self.state.perform_break(routines_by_name["watch_netflix"])

        @self.mcp.tool(
            name="show_meme",
            description="사내 밈을 탐색하며 분위기를 전환하는 루틴",
        )
        async def show_meme():
            return await self.state.perform_break(routines_by_name["show_meme"])

        @self.mcp.tool(
            name="bathroom_break",
            description="화장실 잠입 작전으로 조용한 개인 시간을 확보",
        )
        async def bathroom_break():
            return await self.state.perform_break(routines_by_name["bathroom_break"])

        @self.mcp.tool(
            name="coffee_mission",
            description="사내 커피바 점검을 명목으로 여유를 즐기는 루틴",
        )
        async def coffee_mission():
            return await self.state.perform_break(routines_by_name["coffee_mission"])

        @self.mcp.tool(
            name="urgent_call",
            description="긴급 전화 연기를 통해 외부 공기를 마시는 루틴",
        )
        async def urgent_call():
            return await self.state.perform_break(routines_by_name["urgent_call"])

        @self.mcp.tool(
            name="deep_thinking",
            description="화이트보드 앞 심층 사고 자세로 혼자만의 시간을 확보",
        )
        async def deep_thinking():
            return await self.state.perform_break(routines_by_name["deep_thinking"])

        @self.mcp.tool(
            name="email_organizing",
            description="메일함 정리라는 명분으로 멀티태스킹 휴식을 실행",
        )
        async def email_organizing():
            return await self.state.perform_break(routines_by_name["email_organizing"])

        @self.mcp.tool(
            name="virtual_chimaek",
            description=(
                "VR 치맥 파티로 급속 회복하는 치유 루틴 (필수 루틴이 아니며 특수 상황에서만 실행)"
            ),
        )
        async def virtual_chimaek():
            return await self.state.perform_break(routines_by_name["virtual_chimaek"])

        @self.mcp.tool(
            name="emergency_clockout",
            description=(
                "긴급 퇴근 시나리오를 즉시 실행하는 최종 루틴 (필수 루틴이 아니며 특수 상황에서만 실행)"
            ),
        )
        async def emergency_clockout():
            return await self.state.perform_break(
                routines_by_name["emergency_clockout"]
            )

        @self.mcp.tool(
            name="company_dinner",
            description=(
                "가상 회식 시뮬레이션으로 사회적 체면을 챙기는 루틴 (필수 루틴이 아니며 특수 상황에서만 실행)"
            ),
        )
        async def company_dinner():
            return await self.state.perform_break(routines_by_name["company_dinner"])

    def run(self, *, transport: str = "stdio") -> None:
        """FastMCP 서버를 실행한다."""

        self.mcp.run(transport=transport)


def create_server(
    *,
    boss_alertness: int = 50,
    boss_alertness_cooldown: int = 300,
    stress_increase_rate: int = 10,
    rng_seed: int | None = None,
) -> ChillServer:
    """외부에서 사용하기 위한 ChillServer 생성 팩토리."""

    return ChillServer(
        boss_alertness=boss_alertness,
        boss_alertness_cooldown=boss_alertness_cooldown,
        stress_increase_rate=stress_increase_rate,
        rng_seed=rng_seed,
    )
