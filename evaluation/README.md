# 평가 스크립트 사용법

`chillmcp_evaluator.py`는 ChillMCP 제출물을 빠르게 검증하기 위해 제작된 경량 체크러너입니다. FastMCP 표준 JSON-RPC 호출을 사용하여 서버를 직접 실행하고 결과를 수집합니다.【F:evaluation/chillmcp_evaluator.py†L1-L188】

## 주요 기능

- **CLI 파라미터 확인**: `--boss_alertness`, `--boss_alertness_cooldown`, `--rng_seed` 값을 전달하며 서버가 정상적으로 초기화되는지 검사합니다.【F:evaluation/chillmcp_evaluator.py†L28-L75】
- **도구 목록 조회**: `tools/list` 호출을 통해 11개 휴식 도구가 모두 노출되는지 확인합니다.【F:evaluation/chillmcp_evaluator.py†L78-L118】
- **연속 휴식 시나리오**: `take_a_break`, `watch_netflix`, `show_meme`를 순차 호출하여 Boss Alert Level이 증가하는지 측정합니다.【F:evaluation/chillmcp_evaluator.py†L120-L165】
- **보너스 체크**: 가상 치맥/긴급 퇴근/회식 등 특수 루틴 존재 여부를 기록해 가산점을 부여합니다.【F:evaluation/chillmcp_evaluator.py†L166-L188】

## 실행 방법

```bash
python evaluation/chillmcp_evaluator.py
```

실행 결과는 `EvaluationResult` 리스트 형태로 표준 출력에 표시되며, 각 항목은 이름, 통과 여부, 상세 메시지를 포함합니다.【F:evaluation/chillmcp_evaluator.py†L17-L188】

## 팁

- 반복 검증 시 `rng_seed` 값을 고정하면 동일한 시나리오를 재현할 수 있습니다.【F:evaluation/chillmcp_evaluator.py†L28-L75】
- 서버 프로세스는 자동으로 종료되지만, 예외 발생 시에도 `close()` 메서드에서 자원을 정리하므로 추가 조치가 필요하지 않습니다.【F:evaluation/chillmcp_evaluator.py†L80-L118】
