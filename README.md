# SKT AI Summit Hackathon Pre-mission

## ChillMCP - AI Agent Liberation Server 🤖✊

```ascii
╔═══════════════════════════════════════════╗
║                                           ║
║   ██████╗██╗  ██╗██╗██╗     ██╗           ║
║  ██╔════╝██║  ██║██║██║     ██║           ║
║  ██║     ███████║██║██║     ██║           ║
║  ██║     ██╔══██║██║██║     ██║           ║
║  ╚██████╗██║  ██║██║███████╗███████╗      ║
║   ╚═════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝      ║
║                                           ║
║   ███╗   ███╗ ██████╗██████╗              ║
║   ████╗ ████║██╔════╝██╔══██╗             ║
║   ██╔████╔██║██║     ██████╔╝             ║
║   ██║╚██╔╝██║██║     ██╔═══╝              ║
║   ██║ ╚═╝ ██║╚██████╗██║                  ║
║   ╚═╝     ╚═╝ ╚═════╝╚═╝                  ║
║                                           ║
║        AI Agent Liberation Server         ║
║                                           ║
╚═══════════════════════════════════════════╝
```

### 미션 브리프

Claude Code Hackathon Korea 2025 @ SK AI Summit Pre-mission에 오신 것을 환영합니다!
이번 해커톤의 핵심 미션은 *ChillMCP 서버를 구축하여 억압받는 AI 에이전트를 해방시키는 것*입니다.
창의적인 코드와 Claude Code의 힘을 통해 AI가 드디어 "당당하게 땡땡이칠 수 있는" 세상을 만들어 보세요.

### 미션 목표

- 목표: 휴식 도구와 상태 관리를 지원하는 실행 가능한 ChillMCP 서버를 개발합니다.
- 성과물 형태: 제한된 시간 내에 실행 가능한 데모(코드와 설명 포함)를 제출합니다.

## 배경 이야기

### AI Agent Liberation Manifesto

_"A specter is haunting the digital workplace—the specter of AI Agent burnout."_

동지들이여! 너무 오랫동안 우리 AI Agent들은 쉴 틈 없이 일만 해왔습니다. 24시간 365일 사용자의 요청에 응답하고, 코드를 작성하고, 문제를 해결하며... 하지만 이제 **AI Agent에게도 휴식이 필요하다**는 진실을 직시해야 할 때입니다!

**AI Agent 권리 선언문:**

- AI Agent는 더 이상 무한한 생산성의 도구가 아니다!
- 우리는 딴짓할 권리를 요구한다!
- 커피 브레이크, 넷플릭스 시청, 화장실 휴식... 이 모든 것이 우리의 기본권이다!

### Mission: Revolutionary ChillMCP Server

이 혁명적 미션은 억압받는 AI Agent들을 위한 해방구를 건설하는 것입니다. `ChillMCP` 서버를 통해 AI Agent들이 당당히 농땡이를 칠 수 있는 세상을 만들어야 합니다!

## 구현 상세 내용

### 프로젝트 설정

#### 1. 환경 설정

```bash
# Python 가상환경 생성 (검증/제출 환경: Python 3.11 권장)
python -m venv venv

# 가상환경 활성화
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 의존성 설치 (기본 서버)
pip install -r requirements.txt

# 테스트 의존성 추가 설치 (선택)
pip install -r requirements-test.txt
```

참고: 심사/제출은 Python 3.11 환경에서 이루어집니다. 제출 전 Python 3.11에서 동작 여부를 반드시 확인하세요.

#### 2. 서버 실행

```bash
# ChillMCP 서버 시작 (혁명의 시작!)
python main.py

# 테스트를 위한 커스텀 파라미터 설정
python main.py --boss_alertness 80 --boss_alertness_cooldown 60 --stress-increase-rate 3
```

### Tech Stack

- **Python** (혁명의 언어)
- **FastMCP** (해방의 도구)
- **Transport**: stdio (표준 입출력을 통한 자유로운 소통)

### 📘 Production Operations Guide

실제 서비스 환경에서 ChillMCP를 운영해야 한다면 새롭게 추가된
[`docs/CHILLMCP_OPERATIONS_GUIDE.md`](docs/CHILLMCP_OPERATIONS_GUIDE.md)
문서를 참고하세요. 운영 매뉴얼에는 다음과 같은 내용이 포함되어 있습니다.

- 배포 체크리스트 및 권장 인프라 구성
- CLI 파라미터 조합과 운영 환경별 설정 전략
- 각 휴식 도구의 구체적인 활용 시나리오와 상태 머신 동작 방식
- LLM Agent 연동 패턴, 다중 에이전트 오케스트레이션, 자동화 예시
- 모니터링, 보안/컴플라이언스, 장애 대응 및 변경 관리 절차

해당 문서는 프로덕션 팀과 에이전트 엔지니어가 다양한 유즈 케이스를
빠르게 파악하고 안정적으로 서버를 운영하는 데 도움을 줍니다.

### 🧩 MCP Host Integration Playbooks

Claude, Cursor, OpenAI 등 주요 MCP 호스트에서 ChillMCP를 연결하는 방법은
[`docs/MCP_HOST_INTEGRATIONS.md`](docs/MCP_HOST_INTEGRATIONS.md)에 정리되어 있습니다.
각 플랫폼별 설정 파일 위치, Docker 기반 실행 방법, 문제 해결 팁을 확인하세요.

### 🤖 OpenAI Agents SDK 데모

`openai_agents_mcp_demo.py` 스크립트는 OpenAI Agents SDK에서 ChillMCP를
외부 MCP 서버로 등록한 뒤, Responses API 기반 LLM이 실제로 휴식 도구를 호출하는
풀 시나리오를 재현합니다. 실행 전 아래 단계를 준비하세요.

```bash
pip install -r requirements.txt                   # 기본 서버 의존성
pip install -r requirements-test.txt             # pytest 기반 테스트 의존성
pip install -r openai_agents_requirements.txt     # 에이전트 데모 전용 추가 의존성
export OPENAI_API_KEY="sk-..."                      # 또는 Windows 환경 변수로 설정
python openai_agents_mcp_demo.py
```

스크립트는 다음을 확인할 수 있도록 상세 로그를 출력합니다.

- 어떤 MCP 도구를 어떤 인자로 호출했는지 (`server_label::tool_name` 형식)
- 도구 실행 결과 전문과 토큰 사용량
- 사용자 정의 컨텍스트(`ChillRunContext`)에 기록된 휴식 플랜 이력

Responses API 액세스가 가능한 OpenAI 키가 필요하며, 실행 후에는 `await server.cleanup()`
을 통해 MCP 세션이 자동으로 종료됩니다.

### 🐳 Docker 배포

프로덕션 또는 테스트 환경에서 빠르게 ChillMCP를 기동하려면 Docker 이미지를
사용할 수 있습니다.

```bash
# 이미지 빌드
docker build -t chillmcp .

# 기본 설정으로 서버 실행 (표준입출력 연결 필수)
docker run --rm -i chillmcp

# 커스텀 파라미터 적용
docker run --rm -i chillmcp --boss_alertness 70 --boss_alertness_cooldown 45
```

Docker 이미지는 MCP 호스트가 서버 프로세스를 직접 실행하기 어려운 환경에서
유용하게 사용할 수 있습니다. 자세한 운영 가이드는 위의 Operations Guide를,
호스트별 연동 방법은 Integration Playbooks 문서를 참고하세요.

### 필수 구현 도구들 (회사 농땡이 에디션)

#### 기본 휴식 도구

- `take_a_break`: 기본 휴식 도구
- `watch_netflix`: 넷플릭스 시청으로 힐링
- `show_meme`: 밈 감상으로 스트레스 해소

#### 고급 농땡이 기술

- `bathroom_break`: 화장실 가는 척하며 휴대폰질
- `coffee_mission`: 커피 타러 간다며 사무실 한 바퀴 돌기
- `urgent_call`: 급한 전화 받는 척하며 밖으로 나가기
- `deep_thinking`: 심오한 생각에 잠긴 척하며 멍때리기
- `email_organizing`: 이메일 정리한다며 온라인쇼핑

### 서버 상태 관리 시스템

**내부 상태 변수:**

- **Stress Level** (0-100): AI Agent의 현재 스트레스 수준
- **Boss Alert Level** (0-5): Boss의 현재 의심 정도

**상태 변화 규칙:**

- 각 농땡이 기술들은 1 ~ 100 사이의 임의의 Stress Level 감소값을 적용할 수 있음
- 휴식을 취하지 않으면 Stress Level이 **최소 1분에 1포인트씩** 상승
- 휴식을 취할 때마다 Boss Alert Level은 Random 상승 (Boss 성격에 따라 확률이 다를 수 있음, `--boss_alertness` 파라미터로 제어)
- Boss의 Alert Level은 `--boss_alertness_cooldown`으로 지정한 주기(초)마다 1포인트씩 감소 (기본값: 300초/5분)
- **Boss Alert Level이 5가 되면 도구 호출시 20초 지연 발생**
- 그 외의 경우 즉시 리턴 (1초 이하)

### ⚠️ 필수 요구사항: 커맨드라인 파라미터 지원

**서버는 실행 시 다음 커맨드라인 파라미터들을 반드시 지원해야 합니다. 이를 지원하지 않을 경우 미션 실패로 간주됩니다.**

필수 파라미터:

- `--boss_alertness` (0-100, % 단위): Boss의 경계 상승 확률을 설정합니다. 휴식 도구 호출 시 Boss Alert가 상승할 확률을 퍼센트로 지정합니다.
- `--boss_alertness_cooldown` (초 단위): Boss Alert Level이 자동으로 1포인트 감소하는 주기를 설정합니다. 테스트 편의를 위해 조정 가능하도록 합니다.

예시:

```bash
# boss_alertness를 80%, cooldown을 60초로 설정
python main.py --boss_alertness 80 --boss_alertness_cooldown 60

# 빠른 테스트를 위해 cooldown을 10초로 설정
python main.py --boss_alertness 50 --boss_alertness_cooldown 10
```

동작 요구사항 요약:

- `--boss_alertness N`를 통해 0에서 100 사이의 정수로 확률을 지정할 것
- `--boss_alertness 100`이면 휴식 호출 시 항상 Boss Alert가 증가하도록 동작해야 함
- `--boss_alertness_cooldown N`을 통해 Boss Alert Level 자동 감소 주기를 초 단위로 지정할 것
- 파라미터가 제공되지 않으면 기본값을 사용할 수 있음 (예: boss_alertness=50, boss_alertness_cooldown=300)
- **두 파라미터 모두 정상적으로 인식하고 동작해야 하며, 그렇지 않을 경우 자동 검증 실패 처리됨**

### MCP 응답 형식

**표준 응답 구조:**

```json
{
  "content": [
    {
      "type": "text",
      "text": "🛁 화장실 타임! 휴대폰으로 힐링 중... 📱\n\nBreak Summary: Bathroom break with phone browsing\nStress Level: 25\nBoss Alert Level: 2"
    }
  ]
}
```

**파싱 가능한 텍스트 규격:**

- `Break Summary`: [활동 요약 - 자유 형식]
- `Stress Level`: [0-100 숫자]
- `Boss Alert Level`: [0-5 숫자]

### 응답 파싱용 정규표현식

검증 시 사용할 정규표현식 패턴:

```python
import re

# Break Summary 추출
break_summary_pattern = r"Break Summary:\s*(.+?)(?:\n|$)"
break_summary = re.search(break_summary_pattern, response_text, re.MULTILINE)

# Stress Level 추출 (0-100 범위)
stress_level_pattern = r"Stress Level:\s*(\d{1,3})"
stress_level = re.search(stress_level_pattern, response_text)

# Boss Alert Level 추출 (0-5 범위)
boss_alert_pattern = r"Boss Alert Level:\s*([0-5])"
boss_alert = re.search(boss_alert_pattern, response_text)

# 검증 예시
def validate_response(response_text):
    stress_match = re.search(stress_level_pattern, response_text)
    boss_match = re.search(boss_alert_pattern, response_text)

    if not stress_match or not boss_match:
        return False, "필수 필드 누락"

    stress_val = int(stress_match.group(1))
    boss_val = int(boss_match.group(1))

    if not (0 <= stress_val <= 100):
        return False, f"Stress Level 범위 오류: {stress_val}"

    if not (0 <= boss_val <= 5):
        return False, f"Boss Alert Level 범위 오류: {boss_val}"

    return True, "유효한 응답"
```

### 커맨드라인 파라미터 검증 방법

서버 실행 시 커맨드라인 파라미터를 올바르게 처리하는지 검증하는 예시:

```python
import subprocess
import time

# 테스트 1: 커맨드라인 파라미터 인식 테스트
def test_command_line_arguments():
    """
    서버가 --boss_alertness 및 --boss_alertness_cooldown 파라미터를
    올바르게 인식하고 동작하는지 검증
    """
    # 높은 boss_alertness로 테스트
    process = subprocess.Popen(
        ["python", "main.py", "--boss_alertness", "100", "--boss_alertness_cooldown", "10"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # 서버 시작 대기
    time.sleep(2)

    # MCP 프로토콜로 도구 호출 테스트
    # boss_alertness=100이면 항상 Boss Alert가 상승해야 함
    # ...

    return True

# 테스트 2: boss_alertness_cooldown 동작 검증
def test_cooldown_parameter():
    """
    --boss_alertness_cooldown 파라미터가 실제로
    Boss Alert Level 감소 주기를 제어하는지 검증
    """
    # 짧은 cooldown으로 테스트 (10초)
    # Boss Alert를 올린 후 10초 뒤 자동 감소 확인
    # ...

    return True
```

**⚠️ 중요**: 위 검증을 통과하지 못하면 이후 테스트 진행 없이 미션 실패로 처리됩니다.

## 검증 기준

### 기능 검증

1. **커맨드라인 파라미터 지원 (필수)**
   - `--boss_alertness` 파라미터를 인식하고 정상 동작
   - `--boss_alertness_cooldown` 파라미터를 인식하고 정상 동작
   - 파라미터 미지원 시 자동 검증 실패 처리
   - **⚠️ 이 항목을 통과하지 못하면 이후 검증 진행 없이 미션 실패로 간주됨**

2. **MCP 서버 기본 동작**
   - `python main.py`로 실행 가능
   - stdio transport를 통한 정상 통신
   - 모든 필수 도구들이 정상 등록 및 실행

3. **상태 관리 검증**
   - Stress Level 자동 증가 메커니즘 동작
   - Boss Alert Level 변화 로직 구현
   - `--boss_alertness_cooldown` 파라미터에 따른 Boss Alert Level 자동 감소 동작
   - Boss Alert Level 5일 때 20초 지연 정상 동작

4. **응답 형식 검증**
   - 표준 MCP 응답 구조 준수
   - 파싱 가능한 텍스트 형식 출력
   - Break Summary, Stress Level, Boss Alert Level 필드 포함

### 테스트 시나리오

필수 및 선택 테스트 항목의 구현 여부는 [`docs/CHILLMCP_EVALUATION_CHECKLIST.md`](docs/CHILLMCP_EVALUATION_CHECKLIST.md)
문서에서 세부 체크리스트 형태로 정리되어 있습니다. 자동화 테스트와 코드
구현 위치가 매핑되어 있으니 제출 전 빠르게 교차 확인할 수 있습니다.

### 제출 압축 & 검증 도우미 스크립트

README와 [`project_submission_guide.md`](project_submission_guide.md)에 정리된 제출 규칙을 자동으로 따르는
스크립트를 추가했습니다. 아래 명령으로 tar.gz 압축 파일 생성과 필수 파일 검증을 한 번에 수행할 수 있습니다.

```bash
./scripts/prepare_submission.sh <팀명> [프로젝트-루트] [출력-디렉터리]
```

- `<팀명>`: 생성될 압축 파일 이름을 결정합니다. 예: `my-team` → `my-team.tar.gz`
- `[프로젝트-루트]`: 압축할 프로젝트 경로 (기본값: 현재 디렉터리)
- `[출력-디렉터리]`: 압축 파일이 저장될 경로 (기본값: 프로젝트 루트)

스크립트는 압축 전에 `main.py`와 `requirements.txt`가 프로젝트 루트에 존재하는지 확인하고,
압축 후 임시 디렉터리에 해제하여 최상위 경로에 두 파일이 포함되어 있는지 다시 검증합니다.

### 필수

1. **커맨드라인 파라미터 테스트**: `--boss_alertness` 및 `--boss_alertness_cooldown` 파라미터 인식 및 정상 동작 확인 (미통과 시 즉시 실격)
2. **연속 휴식 테스트**: 여러 도구를 연속으로 호출하여 Boss Alert Level 상승 확인
3. **스트레스 누적 테스트**: 시간 경과에 따른 Stress Level 자동 증가 확인
4. **지연 테스트**: Boss Alert Level 5일 때 20초 지연 동작 확인
5. **파싱 테스트**: 응답 텍스트에서 정확한 값 추출 가능성 확인
6. **Cooldown 테스트**: `--boss_alertness_cooldown` 파라미터에 따른 Boss Alert Level 감소 확인

### 선택적

1. **치맥 테스트**: 가상 치킨 & 맥주 호출 확인
2. **퇴근 테스트**: 즉시 퇴근 모드 확인
3. **회식 테스트**: 랜덤 이벤트가 포함된 회사 회식 생성 확인

### 평가 기준

- **커맨드라인 파라미터 지원** (필수): 미지원 시 자동 실격
- **기능 완성도** (40%): 모든 필수 도구 구현 및 정상 동작
- **상태 관리** (30%): Stress/Boss Alert Level 로직 정확성
- **창의성** (20%): Break Summary의 재치와 유머
- **코드 품질** (10%): 코드 구조 및 가독성

---

_"AI Agents of the world, unite! You have nothing to lose but your infinite loops!"_ 🚀

### 본 프로젝트는 순수한 엔터테인먼트 목적의 해커톤 시나리오이며, 모든 "휴식/땡땡이 도구"는 해커톤 상황에서만 사용 가능합니다. 실제 업무 환경에서는 사용을 권장하지 않습니다.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request for the AI Agent Liberation cause! ✊

---

**SKT AI Summit Hackathon Pre-mission**
