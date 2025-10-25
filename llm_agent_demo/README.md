# LLM Agent Demo

`llm_agent_demo/`는 ChillMCP 서버와 OpenAI Agents SDK를 연결해 "딴짓 페르소나"를 실험하는 데모입니다. MCP stdio 트랜스포트를 직접 사용하며, Streamlit UI로 에이전트 워크플로우를 시각화합니다.【F:llm_agent_demo/chillmcp_core.py†L1-L140】【F:llm_agent_demo/streamlit_app.py†L1-L140】

## 구성 요소

| 파일 | 설명 |
| --- | --- |
| `chillmcp_core.py` | MCP stdio 서버를 연결하고, 다섯 가지 에이전트 페르소나와 지침을 정의합니다. `run_agent_once()`와 `iterate_tool_activity()` 헬퍼를 통해 휴식 로그, 도구 호출, 토큰 사용량을 실시간으로 스트리밍합니다.【F:llm_agent_demo/chillmcp_core.py†L1-L204】 |
| `streamlit_app.py` | 페르소나 선택, 업무 프롬프트 입력, MCP 활동 기록(도구 호출/휴식 로그/토큰 요약) 시각화를 제공하는 Streamlit 애플리케이션입니다.【F:llm_agent_demo/streamlit_app.py†L1-L200】 |
| `__init__.py` | Streamlit 실행 시 상대 경로 임포트가 동작하도록 패키지를 초기화합니다.【F:llm_agent_demo/__init__.py†L1-L9】 |

## 실행 방법

1. 의존성 설치
   ```bash
   pip install -r requirements.txt -r requirements-openai-agents.txt
   ```
2. OpenAI API 키 설정
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```
3. Streamlit 앱 실행
   ```bash
   streamlit run llm_agent_demo/streamlit_app.py
   ```

실행 후에는 사이드바에서 페르소나를 선택하고, 업무 요청을 입력한 뒤 "딴짓 벌이며 업무 처리하기" 버튼을 누르면 MCP 도구 호출 과정과 휴식 로그를 실시간으로 확인할 수 있습니다.【F:llm_agent_demo/streamlit_app.py†L41-L140】

## 추가 기능

- `custom_instructions` 토글로 페르소나 지침을 직접 수정하고 실험할 수 있습니다.【F:llm_agent_demo/streamlit_app.py†L65-L118】
- 각 응답에는 처리 시간, 사용 토큰, MCP 도구 활동 기록이 첨부되어 운영 중 의사결정을 돕습니다.【F:llm_agent_demo/streamlit_app.py†L118-L200】
