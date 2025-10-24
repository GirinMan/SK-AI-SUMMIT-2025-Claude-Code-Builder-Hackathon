# ChillMCP 운영 및 활용 가이드

이 문서는 ChillMCP FastMCP 서버를 프로덕션 환경에서 운용하는 방법을 설명합니다. 지원하는 주요 유스 케이스, 연동 지점, 런타임 설정, 유지보수 흐름을 정리하여 플랫폼 운영자와 에이전트 엔지니어가 내부/외부 사용자에게 서비스를 안정적으로 제공할 수 있도록 돕습니다.

## 1. 시스템 개요

ChillMCP는 Python 기반 [FastMCP](https://github.com/modelcontextprotocol/fastmcp) 서버로, MCP(Model Context Protocol) 클라이언트에게 8가지 휴식 관리 도구를 제공합니다. 서버는 Stress Level과 Boss Alert Level을 추적하며, 에이전트가 즉시 휴식을 취할 수 있는지 혹은 지연이 필요한지를 결정합니다.

핵심 구성 요소:

- **main.py** – FastMCP 서버, 내부 상태 머신, CLI 파서, 각 도구 구현 포함.
- **agent_example.py** – stdio로 ChillMCP 서버에 연결하는 MCP 호환 LLM 에이전트 예제.
- **tests/** – CLI 동작과 도구 시맨틱스를 검증하는 pytest 스위트.

## 2. 배포 체크리스트

1. Python 3.11을 설치하고 독립적인 가상환경을 준비합니다.
2. `pip install -r requirements.txt`로 코어 의존성을 설치하고, 테스트를 실행할 예정이라면 `pip install -r requirements-test.txt`를 추가로 수행합니다.
3. 서버를 실행할 호스트(컨테이너 또는 VM)에 최소 128MB RAM과 stdio로 MCP 서버를 띄울 수 있는 네트워크 환경을 마련합니다.
4. 선호하는 관측 도구를 사용해 stdout/stderr 로그 수집을 구성합니다.
5. 컴플라이언스 요구에 맞춰 `--boss_alertness`, `--boss_alertness_cooldown` 기본값을 결정합니다.
6. 필요하다면 systemd, Docker, Kubernetes Job 등 감독 프로세스로 감싸 자동 재시작을 구성합니다.

## 3. 런타임 설정

ChillMCP는 Escalation 동작을 조절하는 두 가지 CLI 플래그를 제공합니다.

| Flag | Type | Default | 설명 |
| --- | --- | --- | --- |
| `--boss_alertness` | int (0-100) | 50 | 휴식 도구 실행 후 Boss Alert Level이 증가할 확률(%) |
| `--boss_alertness_cooldown` | int (seconds) | 300 | 휴식 도구가 실행되지 않을 때 Boss Alert Level이 1 감소하는 주기 |

예: 매니저 감시가 심하고 Alert 감소 속도가 빠른 환경에서 실행

```bash
python main.py --boss_alertness 90 --boss_alertness_cooldown 30
```

## 4. 도구 카탈로그

각 MCP 도구는 `text/markdown` 페이로드를 반환하며, 수행한 행동과 Stress/Boss Alert 변화가 요약됩니다. 아래 표는 대표 유스 케이스를 정리한 것입니다.

| Tool | Use Case | Behaviour |
| --- | --- | --- |
| `take_a_break` | 업무 사이 짧은 휴식 | 스트레스를 중간 정도 낮추며 Boss Alert 변화는 작음 |
| `watch_netflix` | 깊은 회복 세션 | 스트레스가 크게 줄지만 Alert 상승 폭이 큼 |
| `show_meme` | 분위기 전환 | 스트레스 소폭 감소, Alert 비용도 적음 |
| `bathroom_break` | 잠깐 자리 비우기 | 스트레스 중간 감소, Alert 소폭 증가 |
| `coffee_mission` | 동료와 커피 타임 | 중간~높은 스트레스 감소, 설정에 따라 Alert 증가 가능 |
| `urgent_call` | 의심 없이 자리 이탈 | 높은 스트레스 감소, 남용 시 위험 |
| `deep_thinking` | 일하는 척 쉬기 | 균형 잡힌 스트레스 완화, Alert 중간 증가 |
| `email_organizing` | 메일 정리 모드 | 스트레스 감소 폭 작음, Alert 회복용으로 활용 |

## 5. 상태 머신 동작

- **Stress Level (0-100):** 유휴 상태에서는 자동으로 증가하고, 도구 실행 시 감소하며, 0 미만으로 내려가지 않습니다.
- **Boss Alert Level (0-5):** 도구 실행 후 확률적으로 증가하고, Cooldown 타이머로 감소하며, 5에 도달하면 20초 지연이 적용됩니다.
- 상태 전이는 프로세스 내에서만 유지되므로 서버를 재시작하면 Stress 50, Alert 0으로 초기화됩니다.

## 6. 운영 유즈 케이스

### 6.1 신규 에이전트 온보딩

1. 자격증명을 준비하고 에이전트 런타임에서 `python` 실행이 가능한지 확인합니다.
2. 에이전트 샌드박스에서 ChillMCP 서버를 시작합니다.
3. `agent_example.py`를 참고하여 stdio transport를 사용하도록 에이전트 설정을 지정합니다.
4. `take_a_break`를 호출하여 Stress 감소가 이뤄지는지 헬스 체크합니다.

### 6.2 지속 가능한 팀 로테이션

- 트래픽이 낮은 시간대에는 `--boss_alertness`를 20~30 정도로 낮춰 휴식 빈도를 늘립니다.
- 야간에는 Cooldown(예: 600초)을 늘려 Alert 감소가 너무 빠르지 않도록 조정합니다.
- 도구 응답의 `stress` 값을 샘플링하여 대시보드에 반영합니다.

### 6.3 인시던트 대응

장애나 감사 상황에서는 다음을 수행합니다.

1. 모든 휴식 요청에 지연이 적용되도록 `--boss_alertness`를 95로 높입니다.
2. Cooldown 타이머를 관찰하여 Boss Alert Level이 5에 머무를 경우 에이전트가 자동으로 20초 지연을 겪는지 확인합니다.
3. 상황 종료 후 기본값으로 되돌리고 에이전트 관리자에게 변경 사항을 알립니다.

### 6.4 Human-in-the-Loop 리뷰

- 주간 감사를 위해 도구 호출 로그를 수집합니다.
- `tests/test_chillmcp.py::test_tool_usage_flow` 패턴을 참고하여 동일한 도구 호출을 스크립트로 재실행합니다.
- 재현 테스트를 통해 로그에 기록된 응답과 서버 동작이 일치하는지 확인합니다.

## 7. 연동 패턴

### 7.1 LLM 에이전트 내 임베딩

`agent_example.py`를 참고하면 MCP를 지원하는 라이브러리에 다음 과정을 적용할 수 있습니다.

1. 원하는 CLI 인자로 ChillMCP 서버를 서브프로세스로 띄웁니다.
2. 에이전트 런타임에 MCP 도구를 등록합니다.
3. 모델 제안에 따라 도구를 호출하고, 반환된 markdown을 파싱하여 후속 결정을 내립니다.

### 7.2 멀티 에이전트 오케스트레이션

- 세션 격리를 위해 에이전트당 ChillMCP 서버를 하나씩 실행합니다.
- 환경 변수 또는 중앙 설정 서비스를 통해 공통 설정 값을 공유합니다.
- 수평 확장 시 각 서버 인스턴스에 고유 작업 디렉터리를 부여해 로그 충돌을 방지합니다.

### 7.3 스크립팅 및 자동화

`tests/test_chillmcp.py`에서 사용한 `fastmcp.client` 유틸리티를 활용하면 스케줄러나 배치 작업으로 도구 호출을 자동화할 수 있습니다. 도구 시퀀스를 실행하고 반환된 markdown을 점검해 야간 감사나 Stress 초기화 작업을 수행하세요.

## 8. 테스트 및 품질 게이트

- 배포 전마다 `pytest`를 실행해 CLI 파라미터, Boss Alert Cooldown, 도구 동작을 검증합니다.
- GitHub Actions, GitLab CI, Jenkins 등 CI 파이프라인에 테스트를 통합합니다.
- Blue/Green 배포 시 프로덕션 승격 전에 스테이징 인스턴스에서 테스트를 수행합니다.

## 9. 모니터링 및 관측성

- **Logs:** stdout에는 각 도구 호출마다 Stress/Boss Alert 수준이 JSON 유사 형식으로 기록되므로 로그 수집기에 전달합니다.
- **Metrics:** 로그를 tail 하거나 Prometheus 지표를 내보내는 래퍼를 추가해 Stress, Boss Alert 값을 노출합니다.
- **Alerting:** Boss Alert가 5분 이상 4 이상으로 유지되면 과도한 휴식 사용이므로 알림을 구성합니다.

## 10. 컨테이너 배포

불변의 이식성 있는 빌드가 필요할 때 포함된 `Dockerfile`을 사용합니다. 이미지는 Python 의존성을 설치하고 stdio로 서버를 실행하여 어떤 MCP 호스트와도 연결할 수 있습니다.

### 10.1 빌드 및 배포

```bash
docker build -t chillmcp:latest .
docker tag chillmcp:latest registry.example.com/agents/chillmcp:latest
docker push registry.example.com/agents/chillmcp:latest
```

- 프로덕션 배포 시 `:v1.0.0`과 같이 버전 태그를 고정합니다.
- 조직 정책에 따라 Git 커밋, 도구 버전 등의 빌드 메타데이터를 레이블이나 SBOM으로 기록합니다.

### 10.2 런타임 설정

MCP 호스트에서 stdio를 연결하려면 다음과 같이 컨테이너를 실행합니다.

```bash
docker run --rm -i chillmcp:latest --boss_alertness 65 --boss_alertness_cooldown 90
```

- 필요한 경우 `--env` 플래그로 비밀값이나 환경 토글을 전달합니다.
- Kubernetes, Nomad, ECS 같은 오케스트레이터에서는 stdio가 호스트 프로세스와 연결되도록 구성하거나, stdio를 중계하는 경량 사이드카를 추가합니다.

### 10.3 헬스 체크 및 유지보수

- 베이스 이미지(Python 3.11-slim)를 최신 보안 패치로 유지합니다.
- CI 단계에서 컨테이너 이미지 스캐닝을 실행합니다.
- `take_a_break`과 같은 가벼운 MCP 도구를 주기적으로 호출하는 Liveness Probe를 구성하여 응답 지연이 예산 안에 있는지 확인합니다.

## 11. 보안 및 컴플라이언스

- 실행 파일 권한 또는 컨테이너 격리를 통해 ChillMCP 접근을 제한합니다.
- 도구 응답에 민감한 정보가 포함되지 않았는지 markdown 페이로드를 검사합니다.
- 공유 환경에서는 외부 스케줄러를 사용해 에이전트별 쿼터를 enforce 합니다.

## 12. 트러블슈팅

| Symptom | Possible Cause | Resolution |
| --- | --- | --- |
| 도구 호출이 20초 이상 지연 | Boss Alert Level이 5에 도달 | Cooldown을 기다리거나 서버를 재시작해 상태를 초기화 |
| Boss Alert가 감소하지 않음 | Cooldown 값이 너무 큼 | `--boss_alertness_cooldown` 값을 낮추고 재시작 |
| 에이전트가 연결 불가 | stdout/stderr 파이프 미구성 | stdio transport로 프로세스를 생성하고 중간 래퍼가 없는지 확인 |
| Stress가 항상 높음 | 도구 효과 부족 | `watch_netflix`, `urgent_call` 같은 강력한 도구 사용 및 Alert 확률 조정 |

## 13. 변경 관리

- CLI 변경 사항을 릴리스 노트에 기록합니다.
- Git 태그로 서버 버전을 관리하여 에이전트가 안정 빌드를 고정할 수 있도록 합니다.
- 의존성 업그레이드 시 이해관계자에게 점검 일정과 다운타임을 공유합니다.

## 14. 추가 자료

- `README.md` – 미션 개요 및 상위 요구사항.
- `agent_example.py` – MCP 호환 에이전트 연동 예시.
- `tests/test_chillmcp.py` – 신규 기능 검증을 확장할 수 있는 테스트 시나리오.
