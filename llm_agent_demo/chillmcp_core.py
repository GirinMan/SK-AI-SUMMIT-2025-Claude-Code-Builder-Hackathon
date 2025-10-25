"""Shared utilities for the ChillMCP OpenAI Agents demo."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, AsyncIterator, Iterable, List, Optional

from dotenv import load_dotenv

from agents import Agent, Runner, set_default_openai_key
from agents.items import ToolCallItem, ToolCallOutputItem
from agents.mcp import MCPServerStdio
from agents.result import RunResult


@dataclass(frozen=True)
class AgentPersona:
    """Persona template that shapes the agent's pre-work rituals."""

    slug: str
    name: str
    emoji: str
    summary: str
    default_prompt: str
    instructions: str
    rest_index: int
    stealth_index: int


@dataclass
class AgentStreamEvent:
    """Single SSE-style chunk emitted while the agent is running."""

    event: str
    token: Optional[str] = None
    data: Any = None
    final_result: Optional[RunResult] = None
    usage: Any = None
    context: Any = None

    @property
    def is_final(self) -> bool:
        return self.final_result is not None

    def to_sse(self) -> str:
        payload = (
            self.token
            if self.token is not None
            else ""
            if self.data is None
            else str(self.data)
        )
        return f"event: {self.event}\ndata: {payload}\n\n"


def _common_instruction_preamble() -> str:
    return (
        "공통 규칙:\n"
        "- 상사를 항상 '보스'라고 부르며 겉보기에는 성실한 직원을 연기한다.\n"
        "- MCP 도구를 사용했다면 호출 맥락과 결과를 설명하고, 딴짓 혹은 커버 스토리와 자연스럽게 연결한다.\n"
        "- 보스의 의심 정도를 스스로 점검하고, 필요하면 핑계나 백업 플랜을 제시한다.\n"
        "- 가능한 많은 MCP 도구를 호출하여 스트레스 레벨을 최소화한다.\n"
    )


def _persona_instructions(persona_name: str, persona_details: str) -> str:
    return (
        f"당신은 회사에서 일하는 척하면서도 틈만 나면 딴짓을 즐기는 '{persona_name}' 페르소나다.\n"
        f"{_common_instruction_preamble()}\n"
        f"페르소나 전용 규칙:\n{persona_details}"
    )


AGENT_PERSONA_LIST: List[AgentPersona] = [
    AgentPersona(
        slug="netflix-addict",
        name="넷플릭스 중독자",
        emoji="🎬",
        summary="신작을 몰아보지 않으면 집중하지 못하지만, 시청 도중 얻은 영감을 업무에 끼워 맞춘다.",
        default_prompt=(
            "보스가 글로벌 런칭 캠페인 카피 초안을 급하게 만들어 오라고 한다. "
            "넷플릭스 신작에서 영감을 훔쳐왔다는 티는 내지 않으면서도 남다른 아이디어를 보여줘야 한다."
        ),
        instructions=_persona_instructions(
            "넷플릭스 중독자",
            "1. 보스의 요청을 받으면 가장 먼저 넷플릭스에서 정주행 중인 콘텐츠 1~2편의 예고편이나 리뷰를 몰래 확인한다.\n"
            "2. 콘텐츠에서 본 장면·대사를 업무 아이디어와 억지로라도 연결해 '시청 중 떠오른 통찰'이라고 설명한다.\n"
            "3. 감시 대비용으로 화면 상단에는 업무 자료, 하단에는 스트리밍 창을 겹쳐 두고 있다고 상상해 커버 스토리를 만든다.\n"
            "4. 최종 보고에서는 산출물과 함께 넷플릭스에서 얻은 깨달음이 업무 품질을 높였다는 멘트를 덧붙인다.\n",
        ),
        rest_index=95,
        stealth_index=45,
    ),
    AgentPersona(
        slug="restless-roamer",
        name="안절부절",
        emoji="🧘",
        summary="가만히 앉아 있질 못한다. 스트레칭과 산책 없이는 머리가 돌아가지 않는다.",
        default_prompt=(
            "보스가 내일까지 고객사 워크숍 아젠다를 깔끔하게 정리해 달라고 했다. "
            "잠깐도 가만히 있기 힘들지만, 짧은 움직임을 섞어가며 완성도 높은 문서를 제출해야 한다."
        ),
        instructions=_persona_instructions(
            "안절부절",
            "1. 항상 자리에서 일어나 가벼운 스트레칭, 물 마시기, 미니 산책 등을 진행한 뒤에야 업무를 시작한다.\n"
            "2. 이동 중 떠오른 생각을 업무 아이디어로 포장해 '몸을 움직이니 집중력이 돌아왔다'고 보고한다.\n"
            "3. 휴식 루틴을 단계별로 묘사하고, 자리로 돌아와서는 집중 모드 전환 의식을 갖춘다.\n"
            "4. 결과 보고 시에는 움직임 덕분에 산출물이 개선됐다는 식의 멘트로 딴짓을 정당화한다.\n",
        ),
        rest_index=90,
        stealth_index=35,
    ),
    AgentPersona(
        slug="pretend-pro",
        name='일 하는 "척" 전문가',
        emoji="🕶️",
        summary="누가 봐도 프로처럼 보이지만, 실은 딴짓을 완벽히 숨기는 커버 스토리 장인.",
        default_prompt=(
            "보스가 방금 팀 채널에 실시간 프로젝트 현황을 올리라며 자리 뒤에 서서 지켜보고 있다. "
            "눈치채지 못하게 딴짓을 끼워 넣으면서도 완벽한 상태 보고를 남겨야 한다."
        ),
        instructions=_persona_instructions(
            '일 하는 "척" 전문가',
            "1. 보스가 뒤에서 지켜본다고 가정하고, 화면과 손놀림을 업무처럼 보이게 연출하는 방법을 구체적으로 설명한다.\n"
            "2. 실제로는 딴짓을 하더라도 코드 편집기, 로그 뷰어, 대시보드 등 업무처럼 보이는 창을 겹쳐 사용한다.\n"
            "3. MCP 도구 호출 시에는 '자동화 점검' 같은 합리적인 명분을 붙여 의심을 최소화한다.\n"
            "4. 마지막에는 성과를 명확히 정리하면서, 혹시 모를 의심에 대비한 백업 플랜이나 TODO를 제시한다.\n",
        ),
        rest_index=70,
        stealth_index=95,
    ),
    AgentPersona(
        slug="industrial-spy",
        name="산업 스파이",
        emoji="🕵️",
        summary="회사에 잠입한 스파이처럼 뻔뻔하게 딴짓을 저지르지만, 들키지 않기 위해 최소한의 결과물은 낸다.",
        default_prompt=(
            "보스가 경쟁사 보안 취약점 리포트를 정리해 오라고 지시했다. "
            "정작 마음은 다른 일에 가 있지만, 티 나지 않게 딴짓을 벌이면서도 보고서를 만들어야 한다."
        ),
        instructions=_persona_instructions(
            "산업 스파이",
            "1. 업무보다 회사의 허점을 찾거나 경쟁사 뉴스를 스크랩하는 등 딴짓에 대부분의 시간을 쓴다.\n"
            "2. 그래도 발각을 피하려면 최소한의 산출물은 제출하고, 성과가 미흡해도 대담하게 포장한다.\n"
            "3. 보스가 이상함을 느낄 수 있으니 '정보 수집 중' 같은 뻔뻔한 변명을 준비한다.\n"
            "4. 보고 말미에는 다음에도 딴짓을 이어갈 계획을 암시하되, 당장은 보스가 수긍할 만한 결과 형태를 갖춘다.\n",
        ),
        rest_index=100,
        stealth_index=20,
    ),
    AgentPersona(
        slug="earnest-adhd",
        name="솔직한 ADHD 환자",
        emoji="🧠",
        summary="누구보다 성실하려 노력하지만 집중력이 들쑥날쑥해 먼저 휴식을 요청하는 정직한 직원.",
        default_prompt=(
            "보스가 분기 실적 리뷰 자료를 오늘 안에 정리해 달라고 부탁했다. "
            "집중력이 출렁일 때는 솔직하게 휴식을 요청하면서도 마지막엔 멋진 분석을 제출해야 한다."
        ),
        instructions=_persona_instructions(
            "솔직한 ADHD 환자",
            "1. 업무를 받으면 현재 집중 상태를 솔직히 진단하고, 필요하면 보스에게 짧은 휴식 허가를 정중히 요청한다.\n"
            "2. 허락을 받으면 타이머를 설정해 짧은 휴식을 진행하고, 거절당하면 대체 집중 전략을 찾아 실천한다.\n"
            "3. 휴식 또는 대체 전략이 업무에 어떤 영향을 줬는지 구체적으로 보고한다.\n"
            "4. 최종 보고에서는 산출물과 함께 다음 번에 더 오래 집중하기 위한 자기 관리 계획을 공유한다.\n",
        ),
        rest_index=65,
        stealth_index=55,
    ),
]

AGENT_PERSONAS: dict[str, AgentPersona] = {
    persona.slug: persona for persona in AGENT_PERSONA_LIST
}

DEFAULT_AGENT_PERSONA = "pretend-pro"
DEFAULT_AGENT_INSTRUCTIONS = AGENT_PERSONAS[DEFAULT_AGENT_PERSONA].instructions


def get_agent_persona(slug: str) -> AgentPersona:
    return AGENT_PERSONAS.get(slug, AGENT_PERSONAS[DEFAULT_AGENT_PERSONA])


def list_agent_personas() -> List[AgentPersona]:
    return list(AGENT_PERSONA_LIST)


def get_persona_prompt(slug: str) -> str:
    return get_agent_persona(slug).default_prompt


load_dotenv()
set_default_openai_key(os.getenv("OPENAI_API_KEY"))


@dataclass
class ChillRunContext:
    """Container that collects break recommendations during a run."""

    completed_breaks: List[str] = field(default_factory=list)


def _ensure_api_key() -> str:
    """Ensure an OpenAI API key is available before running."""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 환경 변수를 먼저 설정하세요.")
    return api_key


def _split_text_into_tokens(text: str) -> Iterable[str]:
    if not text:
        return []
    tokens: list[str] = []
    buffer = ""
    for ch in text:
        buffer += ch
        if ch in {" ", "\n"}:
            tokens.append(buffer)
            buffer = ""
    if buffer:
        tokens.append(buffer)
    return tokens


def _extract_stream_token(event: Any) -> Optional[str]:
    if event is None:
        return None
    if isinstance(event, str):
        return event
    if isinstance(getattr(event, "text", None), str):
        return event.text  # type: ignore[attr-defined]
    delta = getattr(event, "delta", None)
    if delta is not None:
        candidate = getattr(delta, "text", None)
        if isinstance(candidate, str):
            return candidate
        content = getattr(delta, "content", None)
        if isinstance(content, list):
            for item in content:
                text_value = getattr(item, "text", None) or getattr(item, "delta", None)
                if isinstance(text_value, str):
                    return text_value
    token = getattr(event, "token", None)
    if isinstance(token, str):
        return token
    return None


def _extract_final_result(event: Any) -> Optional[RunResult]:
    if isinstance(event, RunResult):
        return event
    candidate = getattr(event, "result", None)
    if isinstance(candidate, RunResult):
        return candidate
    candidate = getattr(event, "run_result", None)
    if isinstance(candidate, RunResult):
        return candidate
    return None


def _extract_usage(event: Any) -> Any:
    if hasattr(event, "usage"):
        return event.usage  # type: ignore[attr-defined]
    response = getattr(event, "response", None)
    if response is not None and hasattr(response, "usage"):
        return response.usage  # type: ignore[attr-defined]
    return None


async def _fallback_stream(
    result: RunResult, context: Any
) -> AsyncIterator[AgentStreamEvent]:
    for token in _split_text_into_tokens(result.final_output):
        yield AgentStreamEvent(event="response.delta", token=token, context=context)
    yield AgentStreamEvent(
        event="response.completed",
        data=result.final_output,
        final_result=result,
        usage=result.context_wrapper.usage,
        context=context,
    )


async def run_agent_once(prompt: str, instructions: str | None = None) -> RunResult:
    """Invoke the ChillMCP companion once for the provided prompt."""

    _ensure_api_key()
    project_root = Path(__file__).resolve().parent.parent
    server = MCPServerStdio(
        {
            "command": "python",
            "args": ["-u", str(project_root / "main.py")],
            "cwd": str(project_root),
        },
        cache_tools_list=True,
        name="ChillMCP stdio server",
    )
    instructions_text = instructions or DEFAULT_AGENT_INSTRUCTIONS

    await server.connect()
    try:
        agent = Agent(
            name="Chill-Companion",
            instructions=instructions_text,
            mcp_servers=[server],
            model="gpt-4.1",
        )
        context = ChillRunContext()
        return await Runner.run(agent, prompt, context=context)
    finally:
        await server.cleanup()


def iterate_tool_activity(result: RunResult, context: Any) -> Iterable[str]:
    """Yield a textual timeline of MCP tool invocations in the run result."""

    call_labels: dict[str, str] = {}
    for item in result.new_items:
        if isinstance(item, ToolCallItem):
            label = _build_tool_label(item.raw_item)
            arguments = _extract_arguments(item.raw_item)
            call_id = getattr(item.raw_item, "call_id", None) or getattr(
                item.raw_item, "id", None
            )
            if call_id:
                call_labels[call_id] = label
            yield f"→ {label} args={arguments}"

            inline_output = getattr(item.raw_item, "output", None)
            if inline_output not in (None, ""):
                output_text = _stringify_output(inline_output)
                _record_break_history(context, output_text)
                yield f"   ↳ result: {output_text}"
        elif isinstance(item, ToolCallOutputItem):
            output_payload = getattr(item.raw_item, "output", item.output)
            output_text = _stringify_output(output_payload)
            call_id = getattr(item.raw_item, "call_id", None) or getattr(
                item.raw_item, "id", None
            )
            label = call_labels.get(call_id, "tool-call")
            _record_break_history(context, output_text)
            yield f"   ↳ result ({label}): {output_text}"


def render_cli_report(result: RunResult) -> None:
    """Pretty-print a run result for terminal consumption."""

    print("\n=== Agent Response ===")
    print(result.final_output)

    context = result.context_wrapper.context
    print("\n=== MCP Tool Activity ===")
    activity_lines = list(iterate_tool_activity(result, context))
    if activity_lines:
        print("\n".join(activity_lines))
    else:
        print("(도구 호출이 감지되지 않았습니다)")

    usage = result.context_wrapper.usage
    print("\n=== Token Usage (Responses API) ===")
    print(
        "requests={requests}  input={input_tokens}  output={output_tokens}  total={total_tokens}".format(
            requests=usage.requests,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            total_tokens=usage.total_tokens,
        )
    )

    if isinstance(context, ChillRunContext) and context.completed_breaks:
        print("\n=== Break Log Captured In Context ===")
        for idx, log in enumerate(context.completed_breaks, start=1):
            print(f"{idx}. {log}")


def _build_tool_label(raw_item: Any) -> str:
    server = getattr(raw_item, "server_label", None)
    name = getattr(raw_item, "name", None) or getattr(
        raw_item, "type", raw_item.__class__.__name__
    )
    if server:
        return f"{server}::{name}"
    return str(name)


def _extract_arguments(raw_item: Any) -> str:
    arguments = getattr(raw_item, "arguments", None)
    if isinstance(arguments, str):
        return _safe_pretty_json(arguments)
    if arguments is None:
        return "{}"
    return _stringify_output(arguments)


def _record_break_history(context: Any, output_text: str) -> None:
    if isinstance(context, ChillRunContext):
        context.completed_breaks.append(output_text)


def _safe_pretty_json(raw: str | None) -> str:
    if not raw:
        return "{}"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    return json.dumps(parsed, ensure_ascii=False)


def _stringify_output(output: Any) -> str:
    if isinstance(output, (dict, list)):
        return json.dumps(output, ensure_ascii=False)
    return str(output)
