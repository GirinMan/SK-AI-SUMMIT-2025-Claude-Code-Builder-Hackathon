#!/usr/bin/env python3
"""OpenAI Agents SDK orchestration example for the ChillMCP server.

The demo spins up the local MCP server exposed by ``main.py`` via the stdio transport, hands those tools to an OpenAI Agent instance, and prints the agent's reasoning along with detailed tool telemetry.

To run it locally:
1. ``pip install -r openai_agents_requirements.txt``
2. ``export OPENAI_API_KEY=...`` (or set the variable on Windows)
3. ``python openai_agents_mcp_demo.py``
"""
from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from agents import Agent, Runner
from agents.items import ToolCallItem, ToolCallOutputItem
from agents.mcp import MCPServerStdio
from agents.result import RunResult


@dataclass
class ChillRunContext:
    """Mutable container that tracks every break recipe we tried."""

    completed_breaks: list[str] = field(default_factory=list)


async def run_demo() -> None:
    """Boot an OpenAI Agent connected to ChillMCP and ask for rest advice."""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY must be set in the environment before running this demo."
        )

    project_root = Path(__file__).resolve().parent
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
        user_prompt = (
            "오늘 상사가 자꾸 옆에서 지켜보는 느낌이야. 들키지 않고 몰래 스트레스를 "
            "풀 수 있는 비밀 휴식 플랜을 짜줘."
        )
        result = await Runner.run(agent, user_prompt, context=context)
        display_summary(result)

    finally:
        await server.cleanup()


def display_summary(result: RunResult) -> None:
    """Pretty-print the final response and every MCP tool interaction."""

    print("\n=== Agent Response ===")
    print(result.final_output)

    context = result.context_wrapper.context
    print("\n=== MCP Tool Activity ===")
    activity_lines = list(iterate_tool_activity(result, context))
    if activity_lines:
        print("\n".join(activity_lines))
    else:
        print("(no MCP tool calls were recorded)")

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


def iterate_tool_activity(
    result: RunResult, context: Any
) -> Iterable[str]:
    """Yield a textual timeline of MCP tool calls and outputs."""

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


if __name__ == "__main__":
    asyncio.run(run_demo())
