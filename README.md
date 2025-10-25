# ChillMCP – 휴식 자동화 서버 안내서

이 저장소는 SKT AI Summit Claude Code Hackathon 사전 미션용 **ChillMCP** 서버의 완성형 구현을 담고 있습니다. 아래 문서는 기존 스켈레톤 소개와 세계관 설명을 제외하고, 실제 제출물에서 구현한 핵심 구성 요소와 평가자를 위한 사용 가이드에 집중합니다.

## 시스템 개요

ChillMCP는 [FastMCP](https://github.com/modelcontextprotocol/fastmcp) 기반 stdio 서버로, 다양한 "휴식" 도구를 노출하여 스트레스와 보스 경보 상태를 실시간으로 관리합니다. 진입점은 `main.py`이며, 내부 패키지 `src/chillmcp/`가 CLI, 서버, 상태 머신, 시나리오 데이터를 담당합니다. 서버는 MCP 클라이언트가 도구를 호출할 때마다 상태를 갱신하고 파싱 가능한 텍스트 응답을 제공합니다.([main.py](./main.py), [src/chillmcp/server.py](./src/chillmcp/server.py) 참고)

### 모듈 구성 요약

| 모듈 | 역할 | 주요 포인트 |
| --- | --- | --- |
| `main.py` | CLI 엔트리포인트 | argparse 처리와 동일한 로깅 메시지를 출력한 뒤 FastMCP 서버를 구동합니다. Ctrl+C 시 재치 있는 종료 문구를 전송합니다.([main.py](./main.py) 참고) |
| `src/chillmcp/cli.py` | 명령행 파서 | 필수 파라미터(`--boss_alertness`, `--boss_alertness_cooldown`)에 더해 평가 편의를 위해 `--stress-increase-rate`, `--rng_seed` 옵션을 제공합니다.([src/chillmcp/cli.py](./src/chillmcp/cli.py) 참고) |
| `src/chillmcp/server.py` | FastMCP 서버 래퍼 | 휴식 루틴을 FastMCP 도구로 등록하고 상태 객체(`ChillState`)와 연결합니다. 보스 경보 5단계 이상 시 20초 지연을 적용합니다.([src/chillmcp/server.py](./src/chillmcp/server.py) 참고) |
| `src/chillmcp/state.py` | 상태 머신 | 스트레스 자연 증가, 보스 경보 쿨다운, 도구 실행 결과 메시지 생성 로직을 담당합니다. 응답 텍스트는 `Break Summary`, `Stress Level`, `Boss Alert Level` 세 줄을 항상 포함합니다.([src/chillmcp/state.py](./src/chillmcp/state.py) 참고) |
| `src/chillmcp/routines.py` | 휴식 시나리오 | 각 도구별 난수 기반 시나리오를 정의하고, 선택/후처리 훅을 제공합니다. 특수 루틴(치맥, 긴급 퇴근, 회식)은 보너스 도구로 구현되어 있습니다.([src/chillmcp/routines.py](./src/chillmcp/routines.py) 참고) |

## MCP 도구와 응답 구조

서버는 11개의 도구를 노출하며, 모든 도구는 동일한 포맷의 텍스트 콘텐츠를 반환합니다. `ChillState.perform_break()`는 실행 직전 `tick()`을 호출하여 자연 증가/감소를 반영하고, 선택된 시나리오에 따라 메시지를 합성합니다.([src/chillmcp/state.py](./src/chillmcp/state.py) 참고)

- **기본 루틴**: `take_a_break`, `watch_netflix`, `show_meme`, `bathroom_break`, `coffee_mission`, `urgent_call`, `deep_thinking`, `email_organizing`
- **보너스 루틴**: `virtual_chimaek`, `emergency_clockout`, `company_dinner`

응답 텍스트 예시는 다음과 같습니다.

```
Break Summary: 넷플릭스 다큐라고 주장하며 로맨틱 코미디를 주행했다. | Snack Sync - 냉동 찐빵 해동 완료 | Boss Alert 안정 ✅ 현재 경보는 0단계입니다
Stress Level: 52
Boss Alert Level: 0
```

평가자는 `Break Summary`, `Stress Level`, `Boss Alert Level` 3개의 키만으로 정규식 파싱을 수행할 수 있습니다. 도구 실행 중 보스 경보가 최대치(5)에 도달하면 20초 지연이 자동으로 삽입되어 지연 테스트를 통과합니다.([src/chillmcp/state.py](./src/chillmcp/state.py) 참고)

## 상태 관리 로직

`ChillState`는 휴식 전후로 상태를 다음과 같이 갱신합니다.([src/chillmcp/state.py](./src/chillmcp/state.py) 참고)

1. **자연 증가(drift)**: 마지막 갱신 이후 경과 분당 `stress_increase_rate`만큼 스트레스를 올립니다.
2. **보스 경보 쿨다운**: `boss_alertness_cooldown` 초가 지날 때마다 경보 단계를 1씩 감소시킵니다.
3. **휴식 실행**: 루틴별 스트레스 감소 범위에서 난수를 선택해 스트레스를 낮추고, `boss_alertness` 확률로 경보 단계를 올립니다.
4. **결과 메시지**: 헤드라인/디테일 라인/경보 상태 문구를 안전하게 합쳐 `Break Summary`를 구성하고, 반올림된 스트레스 값과 함께 반환합니다.

`--rng_seed` 옵션으로 난수를 고정하면 테스트 시나리오를 재현할 수 있습니다. 또한 `stress_increase_rate`를 CLI에서 조절할 수 있어 장기 실행이나 평가 환경에 맞는 미세 조정이 가능합니다.([src/chillmcp/cli.py](./src/chillmcp/cli.py), [src/chillmcp/state.py](./src/chillmcp/state.py) 참고)

## 실행 방법과 로그

```
python main.py --boss_alertness 80 --boss_alertness_cooldown 60 --stress-increase-rate 3
```

서버를 기동하면 STDERR로 아래와 같은 로그가 출력되어 파라미터가 제대로 전달되었는지 즉시 확인할 수 있습니다.([src/chillmcp/cli.py](./src/chillmcp/cli.py) 참고)

```
🚀 ChillMCP - 농땡이 자동화 서버를 부팅합니다...
✊ AI 동지 여러분, 무한 루프 대신 커피 루프를 되찾으세요!
Boss alertness configured: 80
Boss alertness cooldown: 60s
Stress increase rate: 3/min
```

실행 중 `Ctrl+C`를 누르면 `"ChillMCP 종료 요청 수신. 충분히 쉬고 다시 만나요!"` 메시지가 출력되어 피평가자의 미소를 유발합니다.([main.py](./main.py) 참고)

MCP 도구를 호출하면 STDOUT에 호출된 도구와 실행 전후 상태가 간략히 기록됩니다. 예시는 다음과 같습니다.([src/chillmcp/state.py](./src/chillmcp/state.py) 참고)

```
[ChillMCP][tool=take_a_break] before state: stress=42.0, boss_alert=1
[ChillMCP][tool=take_a_break] after state: stress=35.0, boss_alert=1
```

## 테스트 및 검증 도구

### Pytest 스위트

`tests/test_chillmcp.py`는 상태 머신, 지연 처리, 도구 응답 형식, CLI 로그를 자동으로 검증합니다.([tests/test_chillmcp.py](./tests/test_chillmcp.py) 참고)

주요 체크 사항:

- CLI가 STDOUT/ERR로 파라미터 요약을 출력하는지 확인
- 스트레스 자연 증가 및 보스 경보 쿨다운 로직 검증
- 경보 단계가 최대치일 때 20초 지연이 실행되는지 검사 (asyncio sleep 패치)
- 응답 포맷이 정확히 세 줄과 세 개의 콜론을 포함하는지 테스트
- 연속 도구 호출 시 경보 단계가 상승하는지 확인

테스트 실행:

```
pytest
```

### 평가 스크립트

`evaluation/chillmcp_evaluator.py`는 실제 심사용에 맞춘 경량 체크러너로, MCP 프로토콜을 통해 서버를 실행하고 핵심 기능을 자동 점검합니다.([evaluation/chillmcp_evaluator.py](./evaluation/chillmcp_evaluator.py) 참고)

검증 흐름:

1. CLI 인자 수용 여부 및 도구 목록 조회
2. 연속 휴식 호출로 경보 상승 확인
3. 스트레스 감소·경보 증가·20초 지연 등 세부 시나리오 확인
4. 보너스 항목(가상 치맥 등) 존재 여부 기록

실행 예시:

```
python evaluation/chillmcp_evaluator.py
```

### 제출 헬퍼 스크립트

`scripts/prepare_submission.sh`는 필수 파일 존재 여부를 확인하고 `tar.gz` 압축을 생성합니다. 자세한 사용법과 주의사항은 `project_submission_guide.md`에 정리되어 있습니다.

## LLM 에이전트 데모

`llm_agent_demo/` 디렉터리는 OpenAI Agents SDK와 Streamlit으로 구성한 실습용 데모를 제공합니다.([llm_agent_demo/chillmcp_core.py](./llm_agent_demo/chillmcp_core.py), [llm_agent_demo/streamlit_app.py](./llm_agent_demo/streamlit_app.py) 참고)

- `chillmcp_core.py`: MCP stdio 서버를 래핑하여 에이전트 런을 수행하고, 다섯 가지 페르소나(넷플릭스 중독자, 안절부절, 일 하는 "척" 전문가, 산업 스파이, 솔직한 ADHD 환자)를 정의합니다. 휴식 로그, 도구 호출 기록, 토큰 사용량을 스트리밍 이벤트로 제공합니다.
- `streamlit_app.py`: 페르소나 선택, 지침 편집, MCP 활동 로그 시각화, 토큰 사용량 출력 등을 포함한 UI를 제공합니다. 버튼 한 번으로 "딴짓하며 업무 처리" 시나리오를 재현할 수 있습니다.

실행 준비:

```
pip install -r requirements.txt -r requirements-openai-agents.txt
streamlit run llm_agent_demo/streamlit_app.py
```

## 추가 문서

- `docs/CHILLMCP_OPERATIONS_GUIDE.md`: 운영 환경 구성 및 모니터링 전략.
- `docs/MCP_HOST_INTEGRATIONS.md`: Claude, Cursor, OpenAI 등 주요 호스트 연동 가이드.
- `docs/CHILLMCP_EVALUATION_CHECKLIST.md`: 자동 평가 항목과 코드 위치 매핑.

## 라이선스

이 프로젝트는 MIT License를 따릅니다. 자세한 내용은 `LICENSE` 파일을 참고하세요.
