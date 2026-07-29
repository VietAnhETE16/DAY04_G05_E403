from __future__ import annotations

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Adjust path to import chat.py
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version
from chat import run_model_tool_loop, trim_history, now_iso, safe_slug, write_transcript, assistant_tool_message, tool_results_message

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    load_lab_env(ROOT)
    
    # Configuration
    provider_name = "openai"
    version = "v3"
    system_prompt_path = ROOT / "artifacts" / "system_prompt.md"
    tools_path = ROOT / "artifacts" / "tools.yaml"
    transcripts_dir = ROOT / "transcripts"
    history_window = 5
    max_tool_rounds = 4
    
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(tools_path)
    openai_tools = to_openai_tools(tool_declarations)
    provider = make_provider(provider_name)
    selected_model = getattr(provider, "default_model", None)
    artifact_version = build_artifact_version(version, system_prompt_path, tools_path)

    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([
        safe_slug(version),
        safe_slug(provider_name),
        timestamp,
    ])
    transcript_path = transcripts_dir / f"{transcript_id}.transcript.json"
    transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": selected_model,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }

    # Simulated inputs
    user_inputs = [
        "Hãy tìm kiếm tin tức về OpenAI trên web giúp mình.",
        "Hãy đọc nội dung bài viết này",
        "URL là https://openai.com/blog",
        "Gửi thông báo 'Chào buổi sáng' lên Telegram",
        "Có"
    ]

    print(f"Starting simulated chat. artifact_version={artifact_version.artifact_version}")
    
    history = []
    for turn_index, user_text in enumerate(user_inputs, 1):
        print(f"\nYou> {user_text}")
        
        messages = [
            {"role": "system", "content": system_prompt},
            *trim_history(history, history_window),
            {"role": "user", "content": user_text},
        ]

        turn_record = {
            "turn_index": turn_index,
            "started_at": now_iso(),
            "user": user_text,
            "status": "started",
            "assistant_text": None,
            "rounds": [],
            "tool_events": [],
        }

        try:
            # We run the loop
            result = run_model_tool_loop(
                provider=provider,
                messages=messages,
                tools=openai_tools,
                model=None,
                max_tool_rounds=max_tool_rounds,
            )
            turn_record.update(result)
            assistant_text = result["assistant_text"]
            print(f"\nAgent> {assistant_text}")
            history.append({"role": "user", "content": user_text})
            history.append({"role": "assistant", "content": assistant_text})
        except Exception as exc:
            turn_record.update({
                "status": "provider_error",
                "error": f"{type(exc).__name__}: {str(exc)}",
            })
            print(f"\nERROR> {turn_record['error']}")

        turn_record["ended_at"] = now_iso()
        transcript["turns"].append(turn_record)
        write_transcript(transcript_path, transcript)
        print(f"Transcript saved: {transcript_path}")

    write_transcript(transcript_path, transcript)
    print(f"\nFinished simulation. Final transcript: {transcript_path}")

if __name__ == "__main__":
    main()
