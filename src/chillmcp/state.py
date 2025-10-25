"""ChillMCP 서버의 상태와 휴식 루틴 모델을 정의하는 모듈."""

from __future__ import annotations

import asyncio
import math
import random
import time
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Sequence, Tuple

# 타입 힌트용 별칭 정의
ExtraLineFactory = Callable[["ChillState"], Sequence[str]]
PostHook = Callable[["ChillState"], None]
AsyncSleepFn = Callable[[float], Awaitable[None]]


@dataclass(frozen=True)
class RoutineScenario:
    """각 휴식 루틴에서 선택될 수 있는 개별 시나리오."""

    headline: str
    stress_reduction: Tuple[int, int]
    detail_lines: ExtraLineFactory | Sequence[str] | None = None

    def render_details(self, state: "ChillState") -> Sequence[str]:
        """시나리오에 연결된 세부 문장을 생성한다."""

        if self.detail_lines is None:
            return ()
        if callable(self.detail_lines):
            return tuple(self.detail_lines(state))
        return tuple(self.detail_lines)


def clamp(value: float, minimum: float, maximum: float) -> float:
    """값을 주어진 구간 ``[minimum, maximum]`` 안으로 고정한다."""

    return max(minimum, min(value, maximum))


def _merge_detail_sources(
    sources: Sequence[str | ExtraLineFactory | Sequence[str]],
) -> Sequence[str] | ExtraLineFactory:
    """여러 디테일 소스를 하나의 팩토리로 통합한다."""

    flattened: list[str] = []
    factories: list[ExtraLineFactory] = []

    for source in sources:
        if callable(source):
            factories.append(source)
        elif isinstance(source, str):
            flattened.append(source)
        else:
            flattened.extend(source)

    if not factories:
        return tuple(flattened)

    def factory(state: "ChillState") -> Sequence[str]:
        lines: list[str] = []
        lines.extend(flattened)
        for item in factories:
            lines.extend(item(state))
        return tuple(lines)

    return factory


@dataclass(frozen=True)
class BreakRoutine:
    """휴식 도구에 필요한 정보를 한곳에 모은 데이터 클래스."""

    name: str
    scenarios: Sequence[RoutineScenario]
    post_hook: PostHook | None = None

    def select_scenario(self, state: "ChillState") -> RoutineScenario:
        """상태 기반 랜덤 시나리오를 선택한다."""

        if not self.scenarios:
            raise ValueError(f"Routine '{self.name}'에 등록된 시나리오가 없습니다.")
        return state.rng.choice(self.scenarios)


@dataclass
class ChillState:
    """ChillMCP 서버가 관리하는 실시간 상태를 보관한다."""

    stress_level: float = 35.0
    boss_alert_level: int = 0
    boss_alertness: int = 35
    boss_alertness_cooldown: int = 120
    stress_increase_rate: float = 1.0
    max_stress: int = 100
    max_boss_alert: int = 5
    rng_seed: int | None = None
    time_fn: Callable[[], float] = time.monotonic
    sleep_fn: AsyncSleepFn | None = None
    rng: random.Random = field(default_factory=random.Random, init=False)
    last_update_time: float = field(default_factory=time.monotonic, init=False)
    last_boss_alert_decay: float = field(default_factory=time.monotonic, init=False)

    def __post_init__(self) -> None:
        """랜덤 시드를 초기화하고 타임스탬프를 맞춘다."""

        object.__setattr__(self, "rng", random.Random(self.rng_seed))
        now = self.time_fn()
        self.last_update_time = now
        self.last_boss_alert_decay = now

    def tick(self) -> None:
        """시간 경과에 따라 스트레스와 경보 수치를 최신 상태로 만든다."""

        now = self.time_fn()
        self._apply_stress_drift(now)
        self._apply_boss_cooldown(now)

    def _apply_stress_drift(self, now: float) -> None:
        """시간이 지남에 따라 스트레스가 자연 증가하도록 처리한다."""

        if now <= self.last_update_time:
            return

        elapsed_seconds = now - self.last_update_time
        stress_increment = (elapsed_seconds / 60.0) * self.stress_increase_rate
        if stress_increment > 0:
            self.stress_level = clamp(
                self.stress_level + stress_increment, 0, self.max_stress
            )
            self.last_update_time = now

    def _apply_boss_cooldown(self, now: float) -> None:
        """지정된 쿨다운 시간마다 보스 경보 수치를 감소시킨다."""

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

    def _snapshot_state(self) -> dict[str, float | int]:
        """스트레스와 보스 경보 상태를 간결한 딕셔너리로 반환한다."""

        return {
            "stress_level": round(self.stress_level, 2),
            "boss_alert_level": self.boss_alert_level,
        }

    def _format_state(self, snapshot: dict[str, float | int]) -> str:
        """스냅샷을 사람 친화적인 로깅 문자열로 변환한다."""

        return (
            f"stress={snapshot['stress_level']}, "
            f"boss_alert={snapshot['boss_alert_level']}"
        )

    async def perform_break(
        self,
        routine: BreakRoutine | str,
        stress_reduction: Tuple[int, int] | None = None,
        flavour_text: str | None = None,
        *,
        extra_lines: ExtraLineFactory | Sequence[str] | None = None,
        post_hook: PostHook | None = None,
    ) -> dict[str, object]:
        """휴식 루틴을 실행하고 결과 메시지를 반환한다."""

        if isinstance(routine, BreakRoutine):
            selected_routine = routine
            scenario = selected_routine.select_scenario(self)
            tool_label = selected_routine.name
        else:
            if stress_reduction is None:
                raise TypeError("스트레스 감소 범위를 지정해야 합니다.")
            details: list[str | ExtraLineFactory | Sequence[str]] = []
            if flavour_text:
                details.append(flavour_text)
            if extra_lines is not None:
                details.append(extra_lines)

            scenario = RoutineScenario(
                headline=routine,
                stress_reduction=stress_reduction,
                detail_lines=_merge_detail_sources(details),
            )
            selected_routine = BreakRoutine(
                name="custom",
                scenarios=(scenario,),
                post_hook=post_hook,
            )
            tool_label = scenario.headline

        state_before = self._snapshot_state()
        print(
            "[ChillMCP][tool="
            f"{tool_label}] before state: "
            f"{self._format_state(state_before)}"
        )

        self.tick()

        if self.boss_alert_level >= self.max_boss_alert:
            # 상사가 바로 뒤에 있는 것 같으니, 20초 동안 일하는 척한다.
            sleep_fn = self.sleep_fn or asyncio.sleep
            await sleep_fn(20)
            self.tick()

        reduction_amount = self.rng.randint(*scenario.stress_reduction)
        self.stress_level = clamp(
            self.stress_level - reduction_amount, 0, self.max_stress
        )

        boss_alert_before = self.boss_alert_level
        boss_noticed = False
        if self.rng.random() * 100 < self.boss_alertness:
            self.boss_alert_level = min(self.max_boss_alert, self.boss_alert_level + 1)
            boss_noticed = self.boss_alert_level != boss_alert_before

        now = self.time_fn()
        self.last_update_time = now
        self.last_boss_alert_decay = now

        if selected_routine.post_hook is not None:
            selected_routine.post_hook(self)

        stress_value = math.floor(self.stress_level + 0.5)
        summary_parts = [scenario.headline]
        summary_parts.extend(scenario.render_details(self))
        if boss_noticed:
            summary_parts.append(
                "Boss Alert 상승 ⚠️ 상사가 휴식을 눈치채 경보가 한 단계 올랐습니다"
            )
        elif self.boss_alert_level == 0:
            summary_parts.append("Boss Alert 안정 ✅ 현재 경보는 0단계입니다")
        else:
            summary_parts.append(
                f"Boss Alert 주의 🟡 경보 {self.boss_alert_level}단계에서 유지 중입니다"
            )

        sanitized_parts = [part.replace(":", " -") for part in summary_parts if part]
        summary_text = " | ".join(sanitized_parts)

        payload_text = (
            f"Break Summary: {summary_text}\n"
            f"Stress Level: {stress_value}\n"
            f"Boss Alert Level: {self.boss_alert_level}"
        )

        state_after = self._snapshot_state()
        print(
            "[ChillMCP][tool="
            f"{tool_label}] after state: "
            f"{self._format_state(state_after)}"
        )

        return {"content": [{"type": "text", "text": payload_text}]}
