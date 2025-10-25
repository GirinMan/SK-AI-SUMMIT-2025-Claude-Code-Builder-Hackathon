# ChillMCP MCP 호스트 연동 가이드

이 문서는 ChillMCP FastMCP 서버를 여러 Model Context Protocol(MCP) 호스트에 등록하는 절차를 정리합니다. 각 섹션은 `python main.py` 또는 제공된 Docker 컨테이너로 stdio 통신을 수행하는 서버 프로세스가 이미 실행되고 있다고 가정합니다.

> ℹ️ **사전 준비:** `requirements.txt`의 의존성을 설치하고, 테스트나 CI 통합이 필요하다면 `requirements-pytest.txt`도 함께 설치하세요. 프로덕션에 노출하기 전에 [`CHILLMCP_OPERATIONS_GUIDE.md`](./CHILLMCP_OPERATIONS_GUIDE.md)의 운영 모범 사례를 확인하면 설정 품질을 높일 수 있습니다.

## 공통 CLI 참고

ChillMCP는 다음 기본 인자를 제공합니다.

```bash
python main.py \
  --boss_alertness 35 \
  --boss_alertness_cooldown 120 \
  --stress-increase-rate 1 \
  --rng_seed 2025
```

`--boss_alertness`와 `--boss_alertness_cooldown`이 핵심 필수 인자이며, `--stress-increase-rate`, `--rng_seed`는 개발/테스트 편의를 위한 선택 플래그입니다. Docker 이미지를 사용할 경우 동일한 인자를 컨테이너 실행 명령 뒤에 그대로 추가하면 됩니다.

## Claude Desktop

Claude Desktop은 `claude_desktop_config.json` 파일을 통해 MCP 서버를 지원합니다.

1. ChillMCP 서버를 로컬에서 실행하거나 Docker 컨테이너가 동작 중인지 확인합니다.
2. Claude Desktop 설정 디렉터리를 엽니다.
   - macOS: `~/Library/Application Support/Claude/`
   - Windows: `%AppData%/Claude/`
3. `claude_desktop_config.json`을 수정(또는 생성)하여 다음 항목을 추가합니다.

   ```json
   {
     "mcpServers": {
       "chillmcp": {
         "command": "python",
         "args": ["/path/to/main.py", "--boss_alertness", "45", "--stress-increase-rate", "2"],
         "env": {
           "PYTHONPATH": "/path/to/project"
         }
       }
     }
   }
   ```

4. Claude Desktop을 재시작하면 `chillmcp` 네임스페이스 아래에서 도구를 확인할 수 있습니다.
5. Docker 이미지를 사용할 경우 `command`를 `docker`로 지정하고 `"args": ["run", "--rm", "-i", "chillmcp", "--boss_alertness", "45"]`와 같이 설정합니다.

### 팁

- CLI 값을 덮어쓰려면 `"args": ["/path/to/main.py", "--boss_alertness", "75", "--boss_alertness_cooldown", "45"]`처럼 인자를 추가합니다.
- 서버 시작에 실패하면 Claude Desktop 개발자 도구(⌥⌘I, macOS)를 열어 stderr 로그를 확인합니다.

## Cursor IDE

Cursor의 MCP 설정은 프로젝트 루트의 `.cursor/mcp.json`에 저장됩니다.

1. Cursor 환경에서 `python`을 실행할 수 있는지 확인하거나 `docker build -t chillmcp .`로 이미지를 준비합니다.
2. `.cursor/mcp.json` 파일을 만들고 아래 구성을 추가합니다.

   ```json
   {
     "chillmcp": {
       "command": "python",
       "args": ["${workspaceFolder}/main.py", "--boss_alertness", "40", "--stress-increase-rate", "3"],
       "transport": "stdio"
     }
   }
   ```

3. Docker를 선호하면 `"command": "docker", "args": ["run", "--rm", "-i", "chillmcp", "--stress-increase-rate", "3"]`로 변경합니다.
4. Cursor를 재시작하거나 `Developer: Reload Window`를 실행하면 구성 변경이 반영되며, 지정한 워크스페이스에서 ChillMCP 도구를 명령 팔레트에서 사용할 수 있습니다.

### 팁

- Cursor는 파일 저장 시 MCP 서버를 자동으로 재시작하므로 상태 드리프트를 최소화하거나 내장 Cooldown 로직에 의존하세요.
- 사전 검증을 위해 통합 터미널에서 `pytest`를 실행해 구성이 지속적으로 유효한지 확인합니다.

## OpenAI (GPT/ChatGPT MCP Preview)

OpenAI의 MCP 호환 클라이언트(예: ChatGPT 데스크톱 프리뷰)는 설정 파일의 `servers` 블록을 사용합니다.

1. 구성 디렉터리를 찾습니다. (예: macOS의 `~/Library/Application Support/OpenAI/`)
2. `chatgpt_config.json`에 다음과 같이 ChillMCP 항목을 추가합니다.

   ```json
   {
     "servers": {
       "chillmcp": {
         "command": "python",
         "args": ["/path/to/main.py", "--boss_alertness", "30", "--boss_alertness_cooldown", "180"],
         "transport": "stdio"
       }
     }
   }
   ```

3. ChatGPT 데스크톱 앱을 재시작하면 MCP 통합 패널에서 ChillMCP 도구를 사용할 수 있습니다.
4. Docker를 활용할 경우 Docker Desktop이 실행 중인지 확인하고, 앞선 섹션과 같이 `command`를 `docker`로 지정합니다.

### 팁

- 샌드박스 데스크톱 앱에서는 절대 경로가 필요합니다.
- Alert 동작을 조정하려면 필요할 때만 `args` 배열에 `"--stress-increase-rate", "2"`나 `"--rng_seed", "2025"`와 같은 선택 플래그를 추가합니다.

## Generic FastMCP Clients

stdio를 사용하는 FastMCP 클라이언트라면 다음과 같이 ChillMCP를 실행할 수 있습니다.

```bash
python main.py --boss_alertness 60 --boss_alertness_cooldown 120 --stress-increase-rate 2
```

Docker 사용 시에는 다음과 같습니다.

```bash
docker run --rm -i chillmcp --boss_alertness 60 --boss_alertness_cooldown 120 --stress-increase-rate 2
```

Docker를 사용할 때는 ChillMCP 컨테이너의 stdin/stdout이 클라이언트 프로세스에 그대로 전달되는지 확인하세요. 전체 Python 연동 예시는 `agent_example.py`와 `tests/test_chillmcp.py::test_take_a_break_tool_via_client`를 참고합니다.

## 트러블슈팅 체크리스트

- MCP 호스트가 `python` 또는 `docker`를 실행할 권한이 있는지 확인합니다.
- ChillMCP 프로세스가 stderr로 시작 로그(`Boss alertness configured`, `Stress increase rate` 등)를 출력하는지 점검하세요. 로그가 없다면 호스트에서 프로세스를 시작하지 못한 경우가 많습니다.
- 호스트 환경 밖에서 흐름을 재현하려면 포함된 pytest 스위트(`pytest -k chillmcp`)로 통합 시나리오를 실행합니다.
