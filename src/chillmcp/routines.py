"""휴식 도구 목록과 재치 있는 메시지를 정의하는 모듈."""

from __future__ import annotations

from typing import Iterable, List

from .state import BreakRoutine


def _chicken_and_beer_lines(state) -> Iterable[str]:
    """가상 치맥 파티 메시지를 생성한다."""

    pairing = state.rng.choice(
        [
            "치킨 메뉴: 🐔 간장 바사삭 & 맥주 온도: 4℃",  # 한식 감성 유지
            "치킨 메뉴: 🔥 마라 양념 & 맥주 온도: -1℃",
            "치킨 메뉴: 🧄 마늘 폭탄 & 맥주 온도: 3℃",
        ]
    )
    return (
        "Snack Tracker: 🍗 야근 수당으로 산 가상 치킨 도착.",
        pairing,
        "Calorie Shield: 🛡️ 내일 아침 헬스장 예약 완료.",
    )


def _company_dinner_lines(state) -> Iterable[str]:
    """랜덤 회식 이벤트를 구성한다."""

    events = [
        "Event Log: 🎤 갑자기 노래방 2차가 소환되었습니다!",
        "Event Log: 🧋 팀장님이 펄 듬뿍 버블티를 쐈습니다!",
        "Event Log: 🎲 야근 vs 연차 가위바위보 토너먼트 개시!",
    ]
    lucky_draw = state.rng.choice(
        [
            "Lucky Draw: 🎁 돌아오는 택시비 영수증 자동 승인!",
            "Lucky Draw: 🎉 내일 오전 회의 자동 취소권 획득!",
            "Lucky Draw: 💤 회식 후 재택근무 패스 발급!",
        ]
    )
    return (state.rng.choice(events), lucky_draw)


def _company_dinner_post_hook(state) -> None:
    """회식 후 스트레스가 살짝 오르도록 연출한다."""

    state.stress_level = min(state.max_stress, state.stress_level + 3)


def _emergency_clockout_post_hook(state) -> None:
    """즉시 퇴근 모드에서는 스트레스와 경보 수치를 초기화한다."""

    state.stress_level = 0
    state.boss_alert_level = 0


ROUTINES: List[BreakRoutine] = [
    BreakRoutine(
        name="take_a_break",
        summary="전신 스트레칭으로 회로를 말랑하게 조정했다.",
        stress_reduction=(8, 18),
        flavour_text="Vibe Log: 🧘 3분 명상과 수분 보충 완료.",
        extra_lines=("Energy Bar: ⚡ 의자 높이와 모니터 각도 재정렬.",),
    ),
    BreakRoutine(
        name="watch_netflix",
        summary="넷플릭스 다큐라고 주장하는 로맨틱 코미디 1편을 재생했다.",
        stress_reduction=(15, 35),
        flavour_text="Binge Report: 🍿 집중 모드로 감상해도 문제없다고 합리화 완료.",
        extra_lines=("Episode Count: 1", "Alibi Status: ✅ 업무 연관성 12% 확보."),
    ),
    BreakRoutine(
        name="show_meme",
        summary="사내 메신저에서 최신 업무 밈을 수집했다.",
        stress_reduction=(5, 12),
        flavour_text="Meme Quality: 😂 이모지 리액션 47개 돌파.",
        extra_lines=("Workflow Mantra: find(problem)->research()->coffee()->run()",),
    ),
    BreakRoutine(
        name="bathroom_break",
        summary="생리 현상 위장 작전과 함께 30분 폰질을 수행했다.",
        stress_reduction=(12, 28),
        flavour_text="Stealth Timer: ⌛ 화면 밝기 20%로 잠입 성공.",
    ),
    BreakRoutine(
        name="coffee_mission",
        summary="에스프레소 머신을 캘리브레이션하며 순찰을 돌았다.",
        stress_reduction=(10, 24),
        flavour_text="Mission Log: ☕ 라떼 아트 흔적은 완벽히 삭제됨.",
        extra_lines=("Bean Tracker: 🌱 원두 재고 73%", "Foam Status: 🫧 적정 유지"),
    ),
    BreakRoutine(
        name="urgent_call",
        summary="미래 로드맵 시너지를 논하는 척 바람을 쐬고 왔다.",
        stress_reduction=(18, 32),
        flavour_text="Call Status: 📞 엘리베이터 앞을 42m 왕복 보행.",
    ),
    BreakRoutine(
        name="deep_thinking",
        summary="화이트보드를 노려보며 '심층 전략'에 몰입한 척했다.",
        stress_reduction=(9, 20),
        flavour_text="Brain Waves: 🤔 명상 99% + 아이디어 1%.",
        extra_lines=("Inspirational Quote: '시뮬레이션도 쉬어야 돌아간다.'",),
    ),
    BreakRoutine(
        name="email_organizing",
        summary="인박스를 정리한다는 핑계로 쇼핑 카트를 채웠다.",
        stress_reduction=(14, 26),
        flavour_text="Inbox Zero: 🛒 할인 코드 3개 확보.",
    ),
    BreakRoutine(
        name="virtual_chimaek",
        summary="가상 현실에서 치킨과 맥주를 한 상 가득 주문했다.",
        stress_reduction=(20, 36),
        flavour_text="Mood Booster: 🍻 회식 없이도 치맥 기운 충전.",
        extra_lines=_chicken_and_beer_lines,
    ),
    BreakRoutine(
        name="emergency_clockout",
        summary="비상 퇴근 버튼을 눌러 전원 차단 시퀀스를 가동했다.",
        stress_reduction=(0, 0),
        flavour_text="Escape Route: 🚪 사무실 불 끄고 즉시 퇴장 완료.",
        extra_lines=("Aftercare Plan: 💤 내일 첫 일정은 11시에 시작.",),
        post_hook=_emergency_clockout_post_hook,
    ),
    BreakRoutine(
        name="company_dinner",
        summary="랜덤 이벤트 가득한 회사 회식 시뮬레이션을 돌렸다.",
        stress_reduction=(6, 14),
        flavour_text="Team Spirit: 🍶 텐션은 올리고 책임감은 내려놓기.",
        extra_lines=_company_dinner_lines,
        post_hook=_company_dinner_post_hook,
    ),
]
