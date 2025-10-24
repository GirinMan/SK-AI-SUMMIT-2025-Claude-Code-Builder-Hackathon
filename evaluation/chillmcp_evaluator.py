"""ChillMCP 기능을 자동으로 점검하는 평가 스크립트."""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from main import create_server, parse_args
from src.chillmcp.routines import ROUTINES
from src.chillmcp.state import BreakRoutine, ChillState


ROUTINE_MAP: Dict[str, BreakRoutine] = {routine.name: routine for routine in ROUTINES}


@dataclass
class EvaluationResult:
    """단일 테스트 항목의 결과."""

    name: str
    passed: bool
    detail: str
    bonus: bool = False


class ManualClock:
    """시간 진행을 수동으로 제어하기 위한 도우미."""

    def __init__(self, start: float = 0.0) -> None:
        self.current = start

    def advance(self, seconds: float) -> float:
        self.current += seconds
        return self.current

    def __call__(self) -> float:
        return self.current


class SleepProbe:
    """`asyncio.sleep` 대체용 더미로, 호출 시간을 기록한다."""

    def __init__(self) -> None:
        self.calls: List[float] = []

    async def __call__(self, seconds: float) -> None:
        self.calls.append(seconds)


async def _run_break(state: ChillState, routine_name: str) -> str:
    """지정한 휴식 루틴을 실행한다."""

    routine = ROUTINE_MAP[routine_name]
    return await state.perform_break(routine)


async def evaluate() -> List[EvaluationResult]:
    """모든 핵심 및 가산 항목을 검사한다."""

    results: List[EvaluationResult] = []

    # 1. 커맨드라인 파라미터 테스트
    args = parse_args(["--boss_alertness", "77", "--boss_alertness_cooldown", "33", "--rng_seed", "9"])
    results.append(
        EvaluationResult(
            name="커맨드라인 파라미터 인식",
            passed=(args.boss_alertness == 77 and args.boss_alertness_cooldown == 33 and args.rng_seed == 9),
            detail=f"boss_alertness={args.boss_alertness}, cooldown={args.boss_alertness_cooldown}, rng_seed={args.rng_seed}",
        )
    )

    # 2. 연속 휴식 테스트 - 상사 경보 상승
    server = create_server(boss_alertness=100, boss_alertness_cooldown=9999, rng_seed=2024)
    boss_state = server.state
    await _run_break(boss_state, "take_a_break")
    await _run_break(boss_state, "watch_netflix")
    await _run_break(boss_state, "show_meme")
    results.append(
        EvaluationResult(
            name="연속 휴식 경보 상승",
            passed=boss_state.boss_alert_level >= 3,
            detail=f"boss_alert_level={boss_state.boss_alert_level}",
        )
    )

    # 3. 스트레스 누적 테스트 - 시간 경과 반영
    clock = ManualClock()
    drift_state = ChillState(time_fn=clock, rng_seed=1)
    initial = drift_state.stress_level
    clock.advance(120)
    drift_state.tick()
    results.append(
        EvaluationResult(
            name="스트레스 자연 증가",
            passed=drift_state.stress_level >= initial + 2,
            detail=f"start={initial:.2f}, after={drift_state.stress_level:.2f}",
        )
    )

    # 4. 지연 테스트 - 최고 경보 시 20초 대기
    sleep_probe = SleepProbe()
    delay_clock = ManualClock()
    delay_state = ChillState(boss_alert_level=5, time_fn=delay_clock, sleep_fn=sleep_probe, rng_seed=2)
    await _run_break(delay_state, "take_a_break")
    results.append(
        EvaluationResult(
            name="Boss Alert 최대 지연",
            passed=(sleep_probe.calls == [20]),
            detail=f"sleep_calls={sleep_probe.calls}",
        )
    )

    # 5. 파싱 테스트 - 텍스트에서 수치 추출
    parsing_state = ChillState(rng_seed=3)
    response = await _run_break(parsing_state, "coffee_mission")
    stress_match = re.search(r"^Stress Level: (?P<value>\d+)$", response, flags=re.MULTILINE)
    boss_match = re.search(r"^Boss Alert Level: (?P<value>\d+)$", response, flags=re.MULTILINE)
    results.append(
        EvaluationResult(
            name="응답 파싱 가능성",
            passed=bool(stress_match and boss_match),
            detail=f"stress={stress_match.group('value') if stress_match else 'NA'}, boss={boss_match.group('value') if boss_match else 'NA'}",
        )
    )

    # 6. 쿨다운 테스트 - 시간 경과에 따른 경보 감소
    cooldown_clock = ManualClock()
    cooldown_state = ChillState(
        boss_alert_level=3,
        boss_alertness_cooldown=10,
        time_fn=cooldown_clock,
        rng_seed=4,
    )
    cooldown_clock.advance(21)
    cooldown_state.tick()
    results.append(
        EvaluationResult(
            name="Boss Alert 쿨다운",
            passed=cooldown_state.boss_alert_level == 1,
            detail=f"boss_alert_level={cooldown_state.boss_alert_level}",
        )
    )

    # === 가산점 항목 ===
    chimaek_state = ChillState(rng_seed=5)
    chimaek_response = await _run_break(chimaek_state, "virtual_chimaek")
    results.append(
        EvaluationResult(
            name="치맥 프로토콜",
            passed="치킨" in chimaek_response and "🍻" in chimaek_response,
            detail="치맥 호출 완료",
            bonus=True,
        )
    )

    exit_state = ChillState(stress_level=88, boss_alert_level=4, rng_seed=6)
    await _run_break(exit_state, "emergency_clockout")
    results.append(
        EvaluationResult(
            name="즉시 퇴근 모드",
            passed=(exit_state.stress_level == 0 and exit_state.boss_alert_level == 0),
            detail=f"stress={exit_state.stress_level}, boss={exit_state.boss_alert_level}",
            bonus=True,
        )
    )

    dinner_state = ChillState(rng_seed=7)
    dinner_response = await _run_break(dinner_state, "company_dinner")
    results.append(
        EvaluationResult(
            name="랜덤 회식 이벤트",
            passed="Event Log:" in dinner_response and "Lucky Draw:" in dinner_response,
            detail="회식 시나리오 생성",
            bonus=True,
        )
    )

    return results


def summarise(results: Iterable[EvaluationResult]) -> str:
    """평가 결과를 요약해 재치 있는 리포트를 만든다."""

    lines = ["🌴 ChillMCP 휴식 감시 리포트"]
    mandatory = [res for res in results if not res.bonus]
    bonuses = [res for res in results if res.bonus]

    lines.append("\n[필수 미션 결과]")
    for res in mandatory:
        status = "✅" if res.passed else "❌"
        lines.append(f"{status} {res.name} - {res.detail}")

    lines.append("\n[보너스 미션 결과]")
    for res in bonuses:
        status = "🌟" if res.passed else "💤"
        lines.append(f"{status} {res.name} - {res.detail}")

    if all(res.passed for res in mandatory):
        lines.append("\n총평: ☕ 커피머신도 박수칠 완벽한 농땡이 운영!")
    else:
        lines.append("\n총평: 🔧 아직 상사 레이더에 잡히는 구간이 남았습니다.")

    return "\n".join(lines)


def main() -> None:
    """스크립트를 직접 실행할 때 평가를 수행한다."""

    results = asyncio.run(evaluate())
    report = summarise(results)
    print(report)


if __name__ == "__main__":
    main()
