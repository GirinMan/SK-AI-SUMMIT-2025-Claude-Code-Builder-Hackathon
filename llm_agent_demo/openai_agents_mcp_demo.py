"""OpenAI Agents + ChillMCP 데모 (CLI & Streamlit UI 지원)."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, List

import streamlit as st
from agents import Agent, Runner
from agents.items import ToolCallItem, ToolCallOutputItem
from agents.mcp import MCPServerStdio
from agents.result import RunResult


@dataclass
class ChillRunContext:
    """실행 중 수집된 휴식 기록을 보관하는 컨테이너."""

    completed_breaks: List[str] = field(default_factory=list)


def _ensure_api_key() -> str:
    """OpenAI API 키가 존재하는지 확인하고 반환한다."""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 환경 변수를 먼저 설정하세요.")
    return api_key


async def run_agent_once(prompt: str) -> RunResult:
    """주어진 프롬프트로 ChillMCP 상담사를 호출한다."""

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

    await server.connect()
    try:
        agent = Agent(
            name="Chill-Companion",
            instructions=(
                "너는 번아웃 직전의 AI 동료에게 맞춤형 휴식 전략을 추천하는 상담사야. "
                "사용 가능한 MCP 도구 목록을 살펴보고, 현재 상황에 딱 맞는 휴식 미션을 추천해. "
                "도구 실행 결과를 바탕으로 생생한 후기를 곁들여 답변해줘."
            ),
            mcp_servers=[server],
        )
        context = ChillRunContext()
        return await Runner.run(agent, prompt, context=context)
    finally:
        await server.cleanup()


def iterate_tool_activity(result: RunResult, context: Any) -> Iterable[str]:
    """MCP 도구 호출 타임라인을 순차적으로 생성한다."""

    call_labels: dict[str, str] = {}
    for item in result.new_items:
        if isinstance(item, ToolCallItem):
            label = _build_tool_label(item.raw_item)
            arguments = _extract_arguments(item.raw_item)
            call_id = getattr(item.raw_item, "call_id", None) or getattr(item.raw_item, "id", None)
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
            call_id = getattr(item.raw_item, "call_id", None) or getattr(item.raw_item, "id", None)
            label = call_labels.get(call_id, "tool-call")
            _record_break_history(context, output_text)
            yield f"   ↳ result ({label}): {output_text}"


def _build_tool_label(raw_item: Any) -> str:
    server = getattr(raw_item, "server_label", None)
    name = getattr(raw_item, "name", None) or getattr(raw_item, "type", raw_item.__class__.__name__)
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


def render_cli_report(result: RunResult) -> None:
    """터미널에서 읽기 쉬운 요약을 출력한다."""

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


def run_streamlit_app() -> None:
    """Streamlit 기반 실시간 상담 UI를 실행한다."""

    st.set_page_config(page_title="ChillMCP 휴식 상담소", page_icon="😴")
    st.title("😴 ChillMCP 휴식 상담소")
    st.caption("농땡이 감지기를 속이기 위한 완벽한 휴식 전략을 상담합니다.")

    default_prompt = (
        "오늘 상사가 자꾸 옆에서 지켜보는 느낌이에요. 들키지 않고 몰래 스트레스를 "
        "풀 수 있는 비밀 휴식 플랜을 추천해주세요."
    )
    prompt = st.text_area("휴식 상담 요청", default_prompt, height=140)

    if st.button("휴식 플랜 생성", type="primary"):
        if not os.getenv("OPENAI_API_KEY"):
            st.error("OPENAI_API_KEY 환경 변수를 설정한 뒤 다시 시도하세요.")
            return
        with st.spinner("AI 상담사가 휴식 미션을 꾸리는 중..."):
            try:
                result = asyncio.run(run_agent_once(prompt))
            except Exception as exc:
                st.error(f"상담 실행 중 오류가 발생했습니다: {exc}")
                return

        st.success("휴식 전략이 도착했습니다!")
        st.subheader("상담사 응답")
        st.write(result.final_output)

        st.subheader("MCP 도구 호출 로그")
        for line in iterate_tool_activity(result, result.context_wrapper.context):
            st.code(line)

        usage = result.context_wrapper.usage
        st.subheader("토큰 사용량")
        st.write(
            f"요청 수: {usage.requests}  입력 토큰: {usage.input_tokens}  출력 토큰: {usage.output_tokens}  총합: {usage.total_tokens}"
        )

        context = result.context_wrapper.context
        if isinstance(context, ChillRunContext) and context.completed_breaks:
            st.subheader("비공식 휴식 로그")
            for idx, log in enumerate(context.completed_breaks, start=1):
                st.markdown(f"{idx}. {log}")


async def run_cli_demo(prompt: str) -> None:
    """기존 CLI 방식으로 상담을 단발성 실행한다."""

    result = await run_agent_once(prompt)
    render_cli_report(result)


def _is_streamlit_invocation() -> bool:
    """Streamlit 런타임에서 실행되고 있는지 판별한다."""

    return any(arg.startswith("--server.") or arg.startswith("--browser.") for arg in sys.argv)


def main() -> None:
    """스크립트 진입점."""

    if _is_streamlit_invocation():
        run_streamlit_app()
        return

    parser = argparse.ArgumentParser(description="ChillMCP OpenAI Agents 데모")
    parser.add_argument(
        "--prompt",
        default=(
            "오늘 상사가 자꾸 옆에서 지켜보는 느낌이야. 들키지 않고 몰래 스트레스를 풀 수 있는 비밀 휴식 플랜을 짜줘."
        ),
        help="상담사에게 전달할 기본 프롬프트.",
    )
    parser.add_argument(
        "--streamlit",
        action="store_true",
        help="Streamlit UI를 직접 실행합니다.",
    )
    args, _unknown = parser.parse_known_args()

    if args.streamlit:
        run_streamlit_app()
        return

    asyncio.run(run_cli_demo(args.prompt))


if __name__ == "__main__":
    main()
