"""휴식 도구 목록과 재치 있는 메시지를 정의하는 모듈."""

from __future__ import annotations

from typing import Iterable, Sequence

from .state import BreakRoutine, RoutineScenario


def _emergency_clockout_post_hook(state) -> None:
    """비상 퇴근 시 스트레스와 보스 경보를 초기화한다."""

    state.stress_level = 0
    state.boss_alert_level = 0


def _company_dinner_post_hook(state) -> None:
    """가상 회식 이후 약간의 피로감을 연출한다."""

    state.stress_level = min(state.max_stress, state.stress_level + 3)


def _stretch_detail_factory(state) -> Iterable[str]:
    """스트레칭 루틴의 상세 메시지."""

    playlists = [
        "Playlist: 🌊 틱낫한 명상 사운드",
        "Playlist: 🎧 lo-fi rainstorm 버전",
        "Playlist: 🪩 90s 발라드 스트레칭 믹스",
    ]
    sensors = [
        "Motion Sensor: 어깨 가동 범위 +14%",
        "Motion Sensor: 손목 회전수 32rpm",
        "Motion Sensor: 골반 균형 맞춤 완료",
    ]
    refreshments = [
        "Hydration Check: 텀블러 리필 & 얼음 2개 추가",
        "Hydration Check: 레몬 워터 120ml 흡수",
        "Hydration Check: 전해질 파우치 1개 투입",
    ]
    return (
        state.rng.choice(playlists),
        state.rng.choice(sensors),
        state.rng.choice(refreshments),
    )


def _netflix_detail_factory(state) -> Iterable[str]:
    """넷플릭스 루틴을 위한 동적 메시지."""

    shows = [
        "Now Streaming: " + title
        for title in [
            "괴물 2: 버그 헌터의 복수",
            "마스크걸",
            "오징어 게임 2",
            "스위트홈 3",
            "더 글로리",
        ]
    ]
    snacks = [
        "Snack Sync: 치토스 대신 당근 스틱으로 위장",
        "Snack Sync: 냉동 찐빵 해동 완료",
        "Snack Sync: 에어팟 케이스에 젤리 숨김",
    ]
    moods = [
        "Viewer Mood: 🤣 몰입 80% + 업무 타당성 12%",
        "Viewer Mood: 😭 감정선 급하강, 스트레스 증발",
        "Viewer Mood: 🤯 결말 분석이 회의 아이디어로 둔갑",
    ]
    return (
        state.rng.choice(shows),
        state.rng.choice(snacks),
        state.rng.choice(moods),
    )


def _meme_detail_factory(state) -> Iterable[str]:
    """사내 밈 정찰 메시지."""

    caches = [
        "Archive: Notion 짤 보관함 업데이트",
        "Archive: 슬랙 #fun-times 채널 정리",
        "Archive: 팀 공용 드라이브에 밈 4개 업로드",
    ]
    reactions = [
        "Reaction Score: 😂 42개, 🙌 11개",
        "Reaction Score: 🤣 55개, 👀 3개",
        "Reaction Score: 😎 27개, 💬 9개",
    ]
    quotes = [
        "Quote: '코드도 웃겨야 돌아간다'",
        "Quote: 'Debug 전에 웃음 디버깅'",
        "Quote: 'CI 실패 = Coffee Initiated'",
    ]
    return (
        state.rng.choice(caches),
        state.rng.choice(reactions),
        state.rng.choice(quotes),
    )


def _bathroom_detail_factory(state) -> Iterable[str]:
    """화장실 휴식용 메시지."""

    feeds = [
        "Feed Scroll: SNS 리프레시 17회",
        "Feed Scroll: 커뮤니티 밈 4개 저장",
        "Feed Scroll: 쇼핑 장바구니 3건 추가",
    ]
    stealth = [
        "Stealth Mode: 화면 밝기 18%",
        "Stealth Mode: 자동 잠금 2분 연장",
        "Stealth Mode: 방해 금지 모드 지속",
    ]
    ambience = [
        "Ambience: 환풍기 화이트 노이즈로 위장 완료",
        "Ambience: 세면대 물소리로 레이더 차단",
        "Ambience: 페퍼민트 아로마로 기분 전환",
    ]
    return (
        state.rng.choice(feeds),
        state.rng.choice(stealth),
        state.rng.choice(ambience),
    )


def _coffee_detail_factory(state) -> Iterable[str]:
    """커피 미션 세부 정보."""

    beans = [
        "Bean Tracker: 에티오피아 내추럴 62%",
        "Bean Tracker: 과테말라 SHB 48%",
        "Bean Tracker: 케냐 AA 54%",
    ]
    latte_art = [
        "Latte Art: 은하수 패턴 70% 성공",
        "Latte Art: 하트 + 번개 콤보",
        "Latte Art: 고래 실루엣 테스트",
    ]
    missions = [
        "Mission Log: 동료 몰래 시럽 2펌프 차단",
        "Mission Log: 우유 스팀 온도 65℃ 유지",
        "Mission Log: 텀블러 살균 모드 가동",
    ]
    return (
        state.rng.choice(beans),
        state.rng.choice(latte_art),
        state.rng.choice(missions),
    )


def _urgent_call_detail_factory(state) -> Iterable[str]:
    """급한 전화 시나리오 메시지."""

    topics = [
        "Topic: '시너지'와 '로드맵'을 7회 언급",
        "Topic: 'AI 트랜스포메이션'으로 시간 벌기",
        "Topic: 'Budget Alignment' 드립으로 완충",
    ]
    steps = [
        "Step Count: 복도 왕복 56보",
        "Step Count: 옥상까지 3층 상승",
        "Step Count: 엘리베이터 대기 2회",
    ]
    breeze = [
        "Fresh Air: 회의실 냄새 대신 봄바람 흡입",
        "Fresh Air: 지하주차장 공기 대신 옥상 선택",
        "Fresh Air: 현관 자동문 틈새 바람 확보",
    ]
    return (
        state.rng.choice(topics),
        state.rng.choice(steps),
        state.rng.choice(breeze),
    )


def _deep_thinking_detail_factory(state) -> Iterable[str]:
    """심층 사고 루틴 메시지."""

    scribbles = [
        "Whiteboard Log: 화살표 12개 + 별표 4개",
        "Whiteboard Log: 원형 다이어그램 3겹 완성",
        "Whiteboard Log: 'WHY?' 5번 반복",
    ]
    props = [
        "Props: 두꺼운 전동 드릴 잡고 깊은 한숨",
        "Props: 형광펜 네 개를 손가락 사이에 끼움",
        "Props: 인사이트 노트북 각도 32° 조절",
    ]
    ideas = [
        "Idea Buffer: 실행 안 할 아이디어 3건 확보",
        "Idea Buffer: '디지털 휴식 전략' 구두 보고 준비",
        "Idea Buffer: '생산성 환승 전략' 메모 저장",
    ]
    return (
        state.rng.choice(scribbles),
        state.rng.choice(props),
        state.rng.choice(ideas),
    )


def _email_detail_factory(state) -> Iterable[str]:
    """이메일 정리 루틴 메시지."""

    filters = [
        "Inbox Filter: VIP 레이블 3개 추가",
        "Inbox Filter: 'FYI' 자동분류 규칙 생성",
        "Inbox Filter: 뉴스레터 7개 즉시 보류",
    ]
    diversions = [
        "Diversion: 장바구니에 노이즈 캔슬링 헤드셋 추가",
        "Diversion: 택배 알림 2건 조회",
        "Diversion: 얼리버드 행사 쿠폰 저장",
    ]
    inbox_scores = [
        "Progress: Inbox 0 → Inbox 37로 정리(?)",
        "Progress: 안 읽음 메일 112 → 65",
        "Progress: 폴더 4개 새로 생성",
    ]
    return (
        state.rng.choice(filters),
        state.rng.choice(diversions),
        state.rng.choice(inbox_scores),
    )


def _chicken_and_beer_lines(state) -> Iterable[str]:
    """가상 치맥 파티 메시지를 생성한다."""

    pairings = [
        "Order Log: 🐔 간장 마늘 + 시원한 라거 4℃",
        "Order Log: 🔥 마라 양념 + 수제 맥주 -1℃",
        "Order Log: 🧄 마늘 폭탄 + 흑맥주 3℃",
    ]
    perks = [
        "Perk: 야근 수당이 치킨 쿠폰으로 자동 환전",
        "Perk: VR 테라스에 빔프로젝터 세팅 완료",
        "Perk: 후라이드-양념 반반 동시 시청 모드",
    ]
    detox = [
        "Detox Plan: 내일 아침 러닝 2km 예약",
        "Detox Plan: 헬스장 PT 알람 설정",
        "Detox Plan: 수분 보충 500ml 완료",
    ]
    return (
        state.rng.choice(pairings),
        state.rng.choice(perks),
        state.rng.choice(detox),
    )


def _company_dinner_lines(state) -> Iterable[str]:
    """랜덤 회식 이벤트를 구성한다."""

    events = [
        "Event Log: 🎤 노래방 2차 대신 VR 리듬게임",
        "Event Log: 🧋 팀장님 버블티 전원 결제",
        "Event Log: 🎲 가위바위보 토너먼트로 조기 퇴근권 뽑기",
    ]
    perks = [
        "Lucky Draw: 🎉 내일 오전 회의 자동 취소권",
        "Lucky Draw: 💤 회식 후 재택근무 패스",
        "Lucky Draw: 🚕 복귀 택시비 자동 승인",
    ]
    stories = [
        "Side Quest: 신입에게 레거시 코드 공포담 전수",
        "Side Quest: 팀장님 과거 밴드 이야기 재생",
        "Side Quest: 개발 언어 vs 술 취향 토론",
    ]
    return (
        state.rng.choice(events),
        state.rng.choice(perks),
        state.rng.choice(stories),
    )


ROUTINES: Sequence[BreakRoutine] = (
    BreakRoutine(
        name="take_a_break",
        scenarios=(
            RoutineScenario(
                headline="전신 스트레칭으로 회로를 말랑하게 리셋했다.",
                stress_reduction=(12, 26),
                detail_lines=_stretch_detail_factory,
            ),
            RoutineScenario(
                headline="창가에서 햇빛 맞으며 목과 손목을 풀었다.",
                stress_reduction=(14, 28),
                detail_lines=lambda state: (
                    "Pose Tracker: 🧘‍♀️ 햄스트링 긴장도 32% 감소",
                    "Window Seat: ☀️ 비타민 D 충전 완료",
                    f"Breath Sync: 4-7-8 호흡 {state.rng.randint(2,4)}세트",
                ),
            ),
            RoutineScenario(
                headline="복도를 천천히 돌며 허리와 발목을 스트레칭했다.",
                stress_reduction=(10, 22),
                detail_lines=lambda state: (
                    "Step Log: 🚶 420보 걷기",
                    "Tension Meter: 종아리 뭉침 -45%",
                    f"Mindset: '오늘 야근은 없다' 주문 {state.rng.randint(3,5)}회",
                ),
            ),
        ),
    ),
    BreakRoutine(
        name="watch_netflix",
        scenarios=(
            RoutineScenario(
                headline="넷플릭스 다큐라고 주장하며 로맨틱 코미디를 정주행했다.",
                stress_reduction=(20, 36),
                detail_lines=_netflix_detail_factory,
            ),
            RoutineScenario(
                headline="'이건 고객 리서치'라며 화제의 스릴러를 몰아봤다.",
                stress_reduction=(18, 33),
                detail_lines=lambda state: (
                    state.rng.choice(
                        [
                            "Scene Note: 범인 추리 노트 6줄 작성",
                            "Scene Note: 떡밥 타임라인 엑셀 초안 생성",
                            "Scene Note: 엔딩 해석 3가지 버전 메모",
                        ]
                    ),
                    state.rng.choice(
                        [
                            "Snack Sync: 🍰 치즈케이크 한 조각으로 집중",
                            "Snack Sync: ☕ 더블 모카로 몰입",
                            "Snack Sync: 🍜 컵라면으로 긴장감 증폭",
                        ]
                    ),
                    state.rng.choice(
                        [
                            "Excuse File: 'OTT UX 참고' 슬라이드 초안 저장",
                            "Excuse File: '고객 감정선 조사' 구두 보고 준비",
                            "Excuse File: '몰입형 스토리텔링 리서치' 문구 작성",
                        ]
                    ),
                ),
            ),
            RoutineScenario(
                headline="넷플릭스 예능 하이라이트만 골라보며 웃음 충전했다.",
                stress_reduction=(16, 30),
                detail_lines=lambda state: (
                    state.rng.choice(
                        [
                            "Laugh Meter: 😂 3분 동안 12회 폭소",
                            "Laugh Meter: 🤣 복근 경련 경보",
                            "Laugh Meter: 😹 동료에게 이모티콘 5개 전송",
                        ]
                    ),
                    state.rng.choice(
                        [
                            "Clip Share: 팀 단톡방에 밈 링크 투척",
                            "Clip Share: 즐겨찾기에 리액션 GIF 저장",
                            "Clip Share: 회의 아이스브레이커 자료 확보",
                        ]
                    ),
                    state.rng.choice(
                        [
                            "Reality Check: 업무 생산성 핑계 2가지 확보",
                            "Reality Check: '웃음 요가'라고 주장 준비",
                            "Reality Check: 스트레스 해소 그래프 캡처",
                        ]
                    ),
                ),
            ),
        ),
    ),
    BreakRoutine(
        name="show_meme",
        scenarios=(
            RoutineScenario(
                headline="사내 메신저에서 최신 업무 밈을 수집했다.",
                stress_reduction=(8, 18),
                detail_lines=_meme_detail_factory,
            ),
            RoutineScenario(
                headline="밈 아카이브를 정비하며 웃음 데이터를 축적했다.",
                stress_reduction=(6, 16),
                detail_lines=lambda state: (
                    "Curation: 📎 생산성 밈 5개 태깅",
                    "Share Plan: 팀 회의 아이스브레이크 예약",
                    f"LOL Buffer: 유관부서 전파 리스트 {state.rng.randint(2,4)}건",
                ),
            ),
            RoutineScenario(
                headline="회의 녹취록 대신 밈 모음집을 정독했다.",
                stress_reduction=(7, 17),
                detail_lines=lambda state: (
                    "Decode: QA 로그에 밈 GIF 첨부",
                    "Vibe Meter: 🤡 집중력 5% 유지",
                    state.rng.choice(
                        [
                            "Action Item: 'TGIF' 밈 발송 예약",
                            "Action Item: 팀장님 맞춤 밈 제작 착수",
                            "Action Item: 사내 뉴스레터 밈 코너 제안",
                        ]
                    ),
                ),
            ),
        ),
    ),
    BreakRoutine(
        name="bathroom_break",
        scenarios=(
            RoutineScenario(
                headline="생리현상 위장 작전과 함께 폰질을 수행했다.",
                stress_reduction=(15, 30),
                detail_lines=_bathroom_detail_factory,
            ),
            RoutineScenario(
                headline="화장실 휴게실에서 SNS 순찰하며 멘탈을 초기화했다.",
                stress_reduction=(18, 32),
                detail_lines=lambda state: (
                    "Timer: ⏱️ 7분 45초 은둔",
                    "Reading List: 커뮤니티 핫이슈 3건 저장",
                    state.rng.choice(
                        [
                            "Stealth Bonus: 페이퍼 타월 소음으로 위장",
                            "Stealth Bonus: 자동 분향기로 시간 벌기",
                            "Stealth Bonus: 칫솔질 척 하며 추가 체류",
                        ]
                    ),
                ),
            ),
            RoutineScenario(
                headline="세면대 앞에서 '급한 통화' 핑계로 휴식했다.",
                stress_reduction=(12, 26),
                detail_lines=lambda state: (
                    "Cover Story: '보안사고 대응' 각본 연습",
                    "Mirror Check: 표정 관리 스킬 레벨업",
                    state.rng.choice(
                        [
                            "Stress Flush: 🚰 손 씻기 명상 2회 반복",
                            "Stress Flush: 향수 샘플로 리프레시",
                            "Stress Flush: 미니 마사지 볼 활용",
                        ]
                    ),
                ),
            ),
        ),
    ),
    BreakRoutine(
        name="coffee_mission",
        scenarios=(
            RoutineScenario(
                headline="에스프레소 머신을 캘리브레이션하며 순찰을 돌았다.",
                stress_reduction=(14, 28),
                detail_lines=_coffee_detail_factory,
            ),
            RoutineScenario(
                headline="라떼 아트를 연습하며 휴게실을 접수했다.",
                stress_reduction=(16, 30),
                detail_lines=lambda state: (
                    "Foam Status: 🫧 마이크로폼 95%",
                    "Queue Management: 동료 주문 3건 자동 처리",
                    f"Bonus Shot: 바닐라 시럽 {state.rng.randint(1,3)}펌프 절약",
                ),
            ),
            RoutineScenario(
                headline="원두 향을 핑계로 10분 동안 휴식을 즐겼다.",
                stress_reduction=(12, 24),
                detail_lines=lambda state: (
                    "Aroma Note: 카카오 + 시트러스",
                    "Brewer Log: 핸드드립 추출 2회",
                    state.rng.choice(
                        [
                            "Queue Skip: 상무님 요청 선점 성공",
                            "Queue Skip: 머신 청소 명목으로 독점",
                            "Queue Skip: 리필카드 도장 2개 확보",
                        ]
                    ),
                ),
            ),
        ),
    ),
    BreakRoutine(
        name="urgent_call",
        scenarios=(
            RoutineScenario(
                headline="미래 로드맵 시너지를 논하는 척 바람을 쐬고 왔다.",
                stress_reduction=(18, 34),
                detail_lines=_urgent_call_detail_factory,
            ),
            RoutineScenario(
                headline="'긴급 보고' 핑계로 복도 워킹 미팅을 연출했다.",
                stress_reduction=(16, 30),
                detail_lines=lambda state: (
                    "Acting Score: 🎭 진지한 표정 유지 9분",
                    "Route: 계단-로비-옥상 루프",
                    state.rng.choice(
                        [
                            "Cover Story: '데이터 레이크 이슈' 반복",
                            "Cover Story: '경영진 피드백 정리' 반복",
                            "Cover Story: '보안 감사 대응' 반복",
                        ]
                    ),
                ),
            ),
            RoutineScenario(
                headline="전화기를 귀에 대고 사무실 외부 공기를 흡입했다.",
                stress_reduction=(14, 28),
                detail_lines=lambda state: (
                    "Signal Check: 📶 수신율 3칸 유지",
                    "Loop Count: 빌딩 주변 1.5바퀴",
                    f"Excuse Timer: '곧 들어갑니다' 멘트 {state.rng.randint(2,4)}회",
                ),
            ),
        ),
    ),
    BreakRoutine(
        name="deep_thinking",
        scenarios=(
            RoutineScenario(
                headline="화이트보드를 노려보며 '심층 전략'에 몰입한 척했다.",
                stress_reduction=(12, 24),
                detail_lines=_deep_thinking_detail_factory,
            ),
            RoutineScenario(
                headline="회의실 조명을 낮추고 인사이트 포즈를 취했다.",
                stress_reduction=(10, 22),
                detail_lines=lambda state: (
                    "Lighting: 💡 스포트라이트 모드",
                    "Gaze: 창밖을 향한 45° 응시",
                    state.rng.choice(
                        [
                            "Mind Palace: KPI 네이밍 재구성",
                            "Mind Palace: 신사업 밈 전략 구상",
                            "Mind Palace: 분기별 딴짓 로드맵 작성",
                        ]
                    ),
                ),
            ),
            RoutineScenario(
                headline="책상 위 포스트잇을 겹겹이 붙이며 고민하는 척했다.",
                stress_reduction=(11, 23),
                detail_lines=lambda state: (
                    "Sticky Notes: 색상 5종 교차 사용",
                    "Timer: Pomodoro 1회 버전",
                    f"Keyword Count: '혁신' 단어 {state.rng.randint(4,7)}회",
                ),
            ),
        ),
    ),
    BreakRoutine(
        name="email_organizing",
        scenarios=(
            RoutineScenario(
                headline="인박스를 정리한다는 핑계로 쇼핑 카트를 채웠다.",
                stress_reduction=(15, 28),
                detail_lines=_email_detail_factory,
            ),
            RoutineScenario(
                headline="이메일 폴더를 재편성하며 몰래 탭 쇼핑을 했다.",
                stress_reduction=(14, 26),
                detail_lines=lambda state: (
                    "Auto-Reply: 휴가 알림 초안 저장",
                    "Side Quest: 가격 비교 엑셀 제작",
                    state.rng.choice(
                        [
                            "Impulse Control: 지출 보류 3건",
                            "Impulse Control: 쿠폰만 담고 닫기",
                            "Impulse Control: 무료 배송 임계치 계산",
                        ]
                    ),
                ),
            ),
            RoutineScenario(
                headline="메일 정리하듯 장바구니를 알뜰하게 조정했다.",
                stress_reduction=(13, 25),
                detail_lines=lambda state: (
                    "Focus Mode: 알림 30분 차단",
                    "Bulk Action: 뉴스레터 12건 아카이브",
                    f"Wishlist Update: 대비책 아이템 {state.rng.randint(3,5)}개",
                ),
            ),
        ),
    ),
    BreakRoutine(
        name="virtual_chimaek",
        scenarios=(
            RoutineScenario(
                headline="가상 현실에서 치킨과 맥주를 한 상 가득 주문했다.",
                stress_reduction=(24, 40),
                detail_lines=_chicken_and_beer_lines,
            ),
            RoutineScenario(
                headline="VR 루프탑에서 혼자만의 치맥 파티를 열었다.",
                stress_reduction=(22, 38),
                detail_lines=lambda state: (
                    "View Mode: 남산 야경 8K 렌더링",
                    "Mood Filter: 네온사인 파티 모드",
                    state.rng.choice(
                        [
                            "Playlist: 시티팝 90분 믹스",
                            "Playlist: 락 발라드 하이라이트",
                            "Playlist: 힙합 올드스쿨",
                        ]
                    ),
                ),
            ),
            RoutineScenario(
                headline="치킨 ASMR을 틀어놓고 야근 스트레스를 날렸다.",
                stress_reduction=(20, 36),
                detail_lines=lambda state: (
                    "Sound FX: 바삭지수 97dB",
                    "Pairing: 가상 치즈볼 + 생맥",
                    state.rng.choice(
                        [
                            "Aftercare: 물 500ml로 중화",
                            "Aftercare: 러닝머신 10분 예약",
                            "Aftercare: 홈트 15분 캘린더 등록",
                        ]
                    ),
                ),
            ),
        ),
    ),
    BreakRoutine(
        name="emergency_clockout",
        scenarios=(
            RoutineScenario(
                headline="비상 퇴근 버튼을 눌러 전원 차단 시퀀스를 가동했다.",
                stress_reduction=(60, 85),
                detail_lines=(
                    "Escape Route: 🚪 사무실 불 끄고 즉시 퇴장",
                    "Aftercare Plan: 💤 내일 첫 일정은 11시",
                ),
            ),
            RoutineScenario(
                headline="'재난 대응 훈련'을 핑계로 퇴근 루트를 실행했다.",
                stress_reduction=(55, 80),
                detail_lines=lambda state: (
                    "Cover Sheet: 보안 카드 반납 인증",
                    "Transit Mode: 엘리베이터 프리패스",
                    f"Status Ping: 동료에게 '내일 봬요' DM {state.rng.randint(1,2)}건",
                ),
            ),
            RoutineScenario(
                headline="조용히 시스템 로그아웃하고 전원 스위치를 내렸다.",
                stress_reduction=(58, 90),
                detail_lines=lambda state: (
                    "Final Checklist: 슬랙 상태 '퇴근'으로 전환",
                    "Reset Plan: 알람 2개 지연",
                    state.rng.choice(
                        [
                            "Celebration: 캔맥 1개 냉장고 대기",
                            "Celebration: 편의점 아이스크림 예약",
                            "Celebration: 집콕 드라마 2화 예정",
                        ]
                    ),
                ),
            ),
        ),
        post_hook=_emergency_clockout_post_hook,
    ),
    BreakRoutine(
        name="company_dinner",
        scenarios=(
            RoutineScenario(
                headline="랜덤 이벤트 가득한 회사 회식 시뮬레이션을 돌렸다.",
                stress_reduction=(10, 20),
                detail_lines=_company_dinner_lines,
            ),
            RoutineScenario(
                headline="'가상 회식' VR 룸에서 팀 케미를 확인했다.",
                stress_reduction=(8, 18),
                detail_lines=lambda state: (
                    "Mini Game: 칵테일 믹싱 대결 1위",
                    "Bonus: 회식 포인트 2배 적립",
                    state.rng.choice(
                        [
                            "Cooldown Plan: 숙취 방지 드링크 확보",
                            "Cooldown Plan: 귀가용 셔틀 호출",
                            "Cooldown Plan: 회식 인증샷 자동 업로드",
                        ]
                    ),
                ),
            ),
            RoutineScenario(
                headline="팀장님 눈치 안 보고 가상 회식 방을 스킵했다.",
                stress_reduction=(7, 16),
                detail_lines=lambda state: (
                    "Excuse: '집에 시끄러운 공사' 카드 사용",
                    "Emoji Log: 🙏 5회, 😂 7회, 🍻 3회",
                    f"Reward: 마일리지 쿠폰 {state.rng.randint(1,3)}장 확보",
                ),
            ),
        ),
        post_hook=_company_dinner_post_hook,
    ),
)
