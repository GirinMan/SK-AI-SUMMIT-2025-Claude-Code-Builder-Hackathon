# ChillMCP 평가 체크리스트

이 문서는 최신 ChillMCP 코드베이스가 README와 평가 기준에서 요구하는 항목을 충족하는지 자체 점검하기 위한 자료입니다. 각 항목은 구현 위치와 검증 방법(테스트, 문서 등)을 함께 표기해 빠르게 추적할 수 있도록 구성했습니다.

## 필수 기능 요구사항

| 항목 | 구현 위치 | 검증 방법 |
| --- | --- | --- |
| MCP 서버 실행 (`python main.py`) | `main.py` – `main()` 및 `ChillServer.run()` | 수동 실행 또는 `tests/test_chillmcp.py::test_take_a_break_tool_via_client` |
| stdio transport 지원 | `ChillServer.run(transport="stdio")` | `tests/test_chillmcp.py::test_take_a_break_tool_via_client` |
| 11개 휴식 도구 등록 | `ChillServer._register_routines` | FastMCP 클라이언트 호출(`tests/test_chillmcp.py::test_take_a_break_tool_via_client`) |
| Stress Level 자연 증가 (기본 1/min) | `ChillState._apply_stress_drift` | `tests/test_chillmcp.py::test_stress_increases_over_time` |
| Boss Alert Level 확률 상승 | `ChillState.perform_break` | `tests/test_chillmcp.py::test_boss_alert_increases_with_high_probability` |
| Boss Alert Level 5 도달 시 20초 지연 | `ChillState.perform_break` | `tests/test_chillmcp.py::test_boss_alert_level_triggers_delay` |
| `--boss_alertness` 파라미터 (기본 35) | `parse_args`, `ChillServer.__init__` | `tests/test_chillmcp.py::test_cli_arguments_are_logged` |
| `--boss_alertness_cooldown` 파라미터 (기본 120초) | `parse_args`, `ChillState._apply_boss_cooldown` | `tests/test_chillmcp.py::test_cli_arguments_are_logged`, `tests/test_chillmcp.py::test_boss_alert_cooldown_reduces_level` |
| `--stress-increase-rate` 파라미터 (기본 1/min) | `parse_args`, `ChillState` | `tests/test_chillmcp.py::test_cli_arguments_are_logged`, `tests/test_chillmcp.py::test_stress_increases_over_time` *(선택 기능 – 테스트 편의)* |
| `--rng_seed` 파라미터 | `parse_args`, `ChillState.__post_init__` | 수동 실행(시드 고정) 또는 평가 스크립트 *(선택 기능 – 테스트 편의)* |
| Boss Alert Level 자동 감소 | `ChillState._apply_boss_cooldown` | `tests/test_chillmcp.py::test_boss_alert_cooldown_reduces_level` |
| 응답 파싱 필드 포함 | `ChillState.perform_break` | `tests/test_chillmcp.py::test_tool_response_format` |
| 연속 휴식 시 Boss Alert 상승 | `ChillState.perform_break` | `tests/test_chillmcp.py::test_consecutive_tool_calls_raise_boss_alert` |

## 선택 요구사항 (창의적 확장)

| 항목 | 구현/문서 |
| --- | --- |
| 추가 휴식 시나리오 및 유머러스한 텍스트 | `src/chillmcp/routines.py` – 11개 루틴의 시나리오/보너스 후크 |
| 프로덕션 운영 가이드 | `docs/CHILLMCP_OPERATIONS_GUIDE.md` |
| MCP 호스트 연동 플레이북 | `docs/MCP_HOST_INTEGRATIONS.md` |
| Docker 배포 지원 | `Dockerfile`, 운영 가이드(컨테이너 섹션), README Docker 안내 |

## 테스트 시나리오 매핑

| README 테스트 시나리오 | 대응 테스트 |
| --- | --- |
| 커맨드라인 파라미터 테스트 | `test_cli_arguments_are_logged` |
| 연속 휴식 테스트 | `test_consecutive_tool_calls_raise_boss_alert` |
| 스트레스 누적 테스트 | `test_stress_increases_over_time` |
| 지연 테스트 | `test_boss_alert_level_triggers_delay` |
| 파싱 테스트 | `test_tool_response_format` |
| Cooldown 테스트 | `test_boss_alert_cooldown_reduces_level` |
| MCP 클라이언트 연동 테스트 | `test_take_a_break_tool_via_client` |

## 채점 기준별 요약

- **커맨드라인 파라미터 지원 (필수)**: `parse_args` 구현과 CLI 로그 테스트로 확인 (`--boss_alertness`, `--boss_alertness_cooldown`).
- **참고:** `--stress-increase-rate`와 `--rng_seed`는 개발 및 평가 편의를 위한 선택 플래그로, 구현 여부가 필수 요건에는 포함되지 않습니다.
- **기능 완성도 (40%)**: 11개 도구 구현, 응답 형식 보장, `agent_example.py`를 통한 실제 호출 예시 제공.
- **상태 관리 (30%)**: 스트레스 증가/감소, Boss Alert 상승/감소, 20초 지연 로직 모두 테스트로 검증.
- **창의성 (20%)**: 보너스 루틴, 디테일 메시지, 운영/호스트 문서를 통해 테마 확장.
- **코드 품질 (10%)**: 모듈화된 설계(`ChillState`, `ChillServer`), 타입 힌트, 테스트 커버리지 확보.

이 체크리스트를 기준으로 변경 사항을 점검하면 README에 기재된 과제 채점 기준을 최신 구현과 비교해 명확하게 확인할 수 있습니다.
