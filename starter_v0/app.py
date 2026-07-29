from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from chat import run_model_tool_loop
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
load_lab_env(ROOT)


def load_agent(provider_name: str, version: str) -> tuple[Any, list[dict[str, Any]], str, str]:
    prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    system_prompt = prompt_path.read_text(encoding="utf-8")
    declarations = load_tool_declarations(tools_path)
    provider = make_provider(provider_name)
    artifact_version = build_artifact_version(version, prompt_path, tools_path).artifact_version
    return provider, to_openai_tools(declarations), system_prompt, artifact_version


st.set_page_config(page_title="Research Agent", layout="wide")
st.title("Research Agent")

with st.sidebar:
    provider_name = st.selectbox("Provider", ["openai", "openrouter", "anthropic", "gemini"], index=0)
    version = st.text_input("Version", value="v1")
    max_tool_rounds = st.slider("Tool rounds", min_value=1, max_value=6, value=4)
    if st.button("Reset chat"):
        st.session_state.messages = []
        st.session_state.traces = []

if "messages" not in st.session_state:
    st.session_state.messages = []
if "traces" not in st.session_state:
    st.session_state.traces = []

provider, tools, system_prompt, artifact_version = load_agent(provider_name, version)
st.caption(f"artifact_version: {artifact_version}")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_text = st.chat_input("Ask for news, tweets, article summaries, papers, policy, or note analysis")
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    messages = [{"role": "system", "content": system_prompt}, *st.session_state.messages]
    with st.spinner("Running agent..."):
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=tools,
            model=None,
            max_tool_rounds=max_tool_rounds,
        )

    assistant_text = result.get("assistant_text", "")
    st.session_state.messages.append({"role": "assistant", "content": assistant_text})
    st.session_state.traces.append(result)
    with st.chat_message("assistant"):
        st.markdown(assistant_text)

if st.session_state.traces:
    st.divider()
    st.subheader("Tool trace")
    for index, trace in enumerate(reversed(st.session_state.traces), start=1):
        with st.expander(f"Turn trace {len(st.session_state.traces) - index + 1}", expanded=index == 1):
            st.json(trace)
