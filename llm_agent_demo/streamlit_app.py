"""Streamlit UI for the ChillMCP OpenAI Agents demo."""

from __future__ import annotations

import asyncio
import os
import time
from typing import Any, Dict, Iterable, List

import streamlit as st

from llm_agent_demo.chillmcp_core import (
    DEFAULT_AGENT_PERSONA,
    collect_tool_activity_entries,
    get_agent_persona,
    list_agent_personas,
    run_agent_once,
)


def _ensure_session_defaults() -> None:
    if "persona_slug" not in st.session_state:
        st.session_state.persona_slug = DEFAULT_AGENT_PERSONA
    persona = get_agent_persona(st.session_state.persona_slug)
    if "prompt_text" not in st.session_state:
        st.session_state.prompt_text = persona.default_prompt
    if "instructions_text" not in st.session_state:
        st.session_state.instructions_text = persona.instructions
    if "custom_instructions" not in st.session_state:
        st.session_state.custom_instructions = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history: List[Dict[str, Any]] = []
    if "last_run" not in st.session_state:
        st.session_state.last_run = None


def _restore_instructions_to_persona() -> None:
    persona = get_agent_persona(
        st.session_state.get("persona_slug", DEFAULT_AGENT_PERSONA)
    )
    st.session_state.instructions_text = persona.instructions
    st.session_state.custom_instructions = False
    st.toast("지침을 페르소나 기본값으로 되돌렸습니다.", icon="🔁")


def _clear_chat_history() -> None:
    persona = get_agent_persona(
        st.session_state.get("persona_slug", DEFAULT_AGENT_PERSONA)
    )
    st.session_state.chat_history = []
    st.session_state.last_run = None
    st.session_state.prompt_text = persona.default_prompt
    if not st.session_state.custom_instructions:
        st.session_state.instructions_text = persona.instructions
    st.toast("대화 기록을 초기화했습니다.", icon="🧹")


def _build_chat_transcript(history: Iterable[Dict[str, Any]]) -> str:
    lines: List[str] = []
    for message in history:
        speaker = "보스" if message["role"] == "user" else "에이전트"
        lines.append(f"{speaker}: {message['content']}")
    return "\n".join(lines)


def _stream_markdown(
    text: str,
    placeholder: st.delta_generator.DeltaGenerator,
    chunk_size: int = 80,
    delay: float = 0.05,
) -> None:
    if not text:
        placeholder.markdown("")
        return
    final_text = text.replace("\n", "  \n")
    for end in range(chunk_size, len(text) + chunk_size, chunk_size):
        snippet = text[: min(end, len(text))]
        placeholder.markdown(snippet.replace("\n", "  \n"))
        time.sleep(delay)
        if end >= len(text):
            break
    placeholder.markdown(final_text)


def _looks_like_json(text: str) -> bool:
    stripped = text.strip()
    return (stripped.startswith("{") and stripped.endswith("}")) or (
        stripped.startswith("[") and stripped.endswith("]")
    )


def _render_payload(payload: Dict[str, Any]) -> None:
    json_payload = payload.get("json") if isinstance(payload, dict) else None
    text_payload = payload.get("text", "") if isinstance(payload, dict) else ""

    if json_payload not in (None, ""):
        st.json(json_payload)
        return

    if text_payload:
        language = "json" if _looks_like_json(text_payload) else "text"
        st.code(text_payload, language=language)
    else:
        st.caption("(비어 있음)")


def _render_tool_activity(entries: Iterable[Dict[str, Any]]) -> None:
    for entry in entries:
        label = entry.get("label", "tool-call")
        arguments_payload = entry.get("arguments", {})
        results = entry.get("results", [])

        with st.container(border=True):
            st.markdown(f"**{label}**")
            st.caption("요청 매개변수")
            _render_payload(arguments_payload)

            if results:
                for idx, result_payload in enumerate(results, start=1):
                    caption_label = "결과" if len(results) == 1 else f"결과 {idx}"
                    st.caption(caption_label)
                    _render_payload(result_payload)
            else:
                st.caption("도구 결과 없음")


def run_streamlit_app() -> None:
    """Launch the Streamlit consultation UI with persona-driven controls."""

    st.set_page_config(page_title="ChillMCP 휴식 상담소", page_icon="😴", layout="wide")
    _ensure_session_defaults()

    all_personas = list_agent_personas()
    persona_map = {persona.slug: persona for persona in all_personas}

    st.title("😴 ChillMCP 휴식 상담소")
    st.caption(
        "보스 몰래 딴짓하며 성과는 똑 부러지게 내는 에이전트 워크플로우를 체험하세요."
    )

    current_slug = st.session_state.persona_slug
    slug_options = [persona.slug for persona in all_personas]
    current_index = slug_options.index(current_slug)

    st.sidebar.header("에이전트 페르소나")
    selected_slug = st.sidebar.radio(
        "기본 페르소나 선택",
        options=slug_options,
        index=current_index,
        format_func=lambda slug: f"{persona_map[slug].emoji} {persona_map[slug].name}",
    )
    if selected_slug != current_slug:
        st.session_state.persona_slug = selected_slug
        persona = persona_map[selected_slug]
        st.session_state.prompt_text = persona.default_prompt
        if not st.session_state.custom_instructions:
            st.session_state.instructions_text = persona.instructions
        st.toast(f"{persona.emoji} {persona.name} 페르소나로 전환했습니다.", icon="🎭")

    persona = get_agent_persona(st.session_state.persona_slug)

    st.sidebar.markdown(f"**{persona.emoji} {persona.name}**")
    st.sidebar.info(persona.summary)

    rest_col, stealth_col = st.sidebar.columns(2)
    rest_col.metric("휴식 집착", f"{persona.rest_index}/100")
    stealth_col.metric("위장 능력", f"{persona.stealth_index}/100")

    st.sidebar.divider()
    sidebar_toggle = getattr(st.sidebar, "toggle", st.sidebar.checkbox)
    sidebar_toggle("지침 직접 편집", key="custom_instructions")
    st.sidebar.button("대화 초기화", type="secondary", on_click=_clear_chat_history)
    st.sidebar.button(
        "페르소나 기본 지침 복원",
        type="secondary",
        on_click=_restore_instructions_to_persona,
    )

    with st.sidebar.expander(
        "현재 지침", expanded=st.session_state.custom_instructions
    ):
        st.text_area(
            "Chill-Companion 지침",
            value=st.session_state.instructions_text,
            height=220,
            key="instructions_text",
            disabled=not st.session_state.custom_instructions,
        )
        if st.session_state.custom_instructions:
            st.caption(f"현재 글자 수: {len(st.session_state.instructions_text)}")
        else:
            st.caption("토글을 켜면 지침을 직접 수정할 수 있습니다.")

    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            role = "user" if message["role"] == "user" else "assistant"
            avatar = (
                "🧑‍💼"
                if role == "user"
                else get_agent_persona(message.get("persona_slug", persona.slug)).emoji
            )
            with st.chat_message(role, avatar=avatar):
                st.markdown(message["content"])
                if role == "assistant":
                    st.caption(f"⏱️ 처리 시간: {message['duration']:.2f}초")
                    activity_entries = message.get("activity_entries")
                    if activity_entries:
                        with st.expander("MCP 도구 활동 기록", expanded=False):
                            _render_tool_activity(activity_entries)
                    else:
                        legacy_lines = message.get("activity_lines", [])
                        if legacy_lines:
                            with st.expander("MCP 도구 활동 기록", expanded=False):
                                for line in legacy_lines:
                                    st.markdown(f"- {line}")
                        else:
                            st.caption("도구 호출 기록 없음")
                    usage = message.get("usage")
                    if usage:
                        st.caption(
                            f"토큰 — 요청 {usage['requests']}, 입력 {usage['input_tokens']}, 출력 {usage['output_tokens']}, 총 {usage['total_tokens']}"
                        )

    left_col, right_col = st.columns([3, 2])
    with left_col:
        prompt = st.text_area(
            "보스에게 전달할 새 업무 요청",
            value=st.session_state.prompt_text,
            height=160,
            key="prompt_text",
        )
        run_button = st.button("딴짓 벌이며 업무 처리하기", type="primary")
    with right_col:
        st.subheader("현재 페르소나")
        st.markdown(f"{persona.emoji} **{persona.name}**")
        st.caption(persona.summary)

    effective_instructions = (
        st.session_state.instructions_text
        if st.session_state.custom_instructions
        else persona.instructions
    )

    if run_button:
        if not os.getenv("OPENAI_API_KEY"):
            st.error("OPENAI_API_KEY 환경 변수를 설정한 뒤 다시 시도하세요.")
            return

        user_message = prompt.strip()
        if not user_message:
            st.warning("보스의 지시 내용을 입력해주세요.")
            return

        user_entry = {
            "role": "user",
            "content": user_message,
            "persona_slug": persona.slug,
        }
        st.session_state.chat_history.append(user_entry)

        with st.chat_message("user", avatar="🧑‍💼"):
            st.markdown(user_message)

        transcript = _build_chat_transcript(st.session_state.chat_history)

        assistant_container = st.chat_message("assistant", avatar=persona.emoji)
        with assistant_container:
            stream_placeholder = st.empty()
            status_placeholder = st.empty()
            status_placeholder.caption("에이전트가 딴짓 전략을 구상하는 중... ⏳")

            start_time = time.perf_counter()
            try:
                result = asyncio.run(
                    run_agent_once(transcript, instructions=effective_instructions)
                )
            except Exception as exc:
                status_placeholder.empty()
                st.error(f"상담 실행 중 오류가 발생했습니다: {exc}")
                st.session_state.chat_history.pop()  # roll back user entry on failure
                return

            duration = time.perf_counter() - start_time
            status_placeholder.empty()
            _stream_markdown(result.final_output, stream_placeholder)

            context = result.context_wrapper.context
            activity_entries = collect_tool_activity_entries(result, context)
            usage = result.context_wrapper.usage

            st.caption(f"⏱️ 처리 시간: {duration:.2f}초")

            if activity_entries:
                with st.expander("MCP 도구 활동 기록", expanded=False):
                    _render_tool_activity(activity_entries)
            else:
                st.caption("도구 호출 기록 없음")

            with st.expander("토큰 사용량", expanded=False):
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("요청 수", usage.requests)
                col2.metric("입력 토큰", usage.input_tokens)
                col3.metric("출력 토큰", usage.output_tokens)
                col4.metric("총 토큰", usage.total_tokens)

        assistant_entry = {
            "role": "assistant",
            "content": result.final_output,
            "duration": duration,
            "activity_entries": activity_entries,
            "usage": {
                "requests": usage.requests,
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
                "total_tokens": usage.total_tokens,
            },
            "persona_slug": persona.slug,
            "instructions": effective_instructions,
        }
        st.session_state.chat_history.append(assistant_entry)
        st.session_state.last_run = assistant_entry
        st.toast("딴짓을 마치고 결과를 보고했습니다! ☕️", icon="✅")


if __name__ == "__main__":
    run_streamlit_app()
