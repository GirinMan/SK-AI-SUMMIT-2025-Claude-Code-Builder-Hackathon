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


def clamp(value: float, minimum: float, maximum: float) -> float:
    """값을 주어진 구간 ``[minimum, maximum]`` 안으로 고정한다."""

    return max(minimum, min(value, maximum))


@dataclass(frozen=True)
class BreakRoutine:
    """휴식 도구에 필요한 정보를 한곳에 모은 데이터 클래스."""

    name: str
    summary: str
    stress_reduction: Tuple[int, int]
    flavour_text: str
    extra_lines: ExtraLineFactory | Sequence[str] | None = None
    post_hook: PostHook | None = None

    def render_extra_lines(self, state: "ChillState") -> Sequence[str]:
        """추가 안내 문장을 생성한다."""

        if self.extra_lines is None:
            return ()
        if callable(self.extra_lines):
            return tuple(self.extra_lines(state))
        return tuple(self.extra_lines)


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

    async def perform_break(
        self,
        routine: BreakRoutine | str,
        stress_reduction: Tuple[int, int] | None = None,
        flavour_text: str | None = None,
        *,
        extra_lines: ExtraLineFactory | Sequence[str] | None = None,
        post_hook: PostHook | None = None,
    ) -> str:
        """휴식 루틴을 실행하고 결과 문자열을 반환한다."""

        if isinstance(routine, BreakRoutine):
            selected_routine = routine
        else:
            if stress_reduction is None or flavour_text is None:
                raise TypeError(
                    "요약, 스트레스 감소 범위, 분위기 문구를 모두 지정해야 합니다."
                )
            selected_routine = BreakRoutine(
                name="custom",
                summary=routine,
                stress_reduction=stress_reduction,
                flavour_text=flavour_text,
                extra_lines=extra_lines,
                post_hook=post_hook,
            )

        self.tick()

        if self.boss_alert_level >= self.max_boss_alert:
            # 상사가 바로 뒤에 있는 것 같으니, 20초 동안 일하는 척한다.
            sleep_fn = self.sleep_fn or asyncio.sleep
            await sleep_fn(20)
            self.tick()

        reduction_amount = self.rng.randint(*selected_routine.stress_reduction)
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

        lines = [
            f"Break Summary: {selected_routine.summary}",
            f"Stress Level: {stress_value}",
            f"Boss Alert Level: {self.boss_alert_level}",
            selected_routine.flavour_text,
        ]

        lines.extend(selected_routine.render_extra_lines(self))

        if boss_noticed:
            lines.append("Boss Radar: 👀 상사가 뭔가 감지했습니다. 연막탄 준비!")
        elif self.boss_alert_level == 0:
            lines.append("Boss Radar: ✅ 안전 지대 확보 완료.")

        return "\n".join(lines)
