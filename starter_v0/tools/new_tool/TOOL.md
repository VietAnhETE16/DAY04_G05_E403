---
name: new_tool
track: bonus
kind: local_formatter
provider: Local Python
requires_env: []
inputs: [text, focus, max_items]
outputs: [summary, action_items, keywords, markdown, stats]
side_effect: false
---
# new_tool

Analyzes a block of notes or meeting text without calling an external API.

Use this tool when the user provides raw text and asks for a compact summary,
next steps, action items, keywords, or basic text statistics. The optional
`focus` argument helps rank sentences that mention a particular topic. The
`max_items` argument controls how many summary sentences, action items, and
keywords are returned. The `markdown` output is ready for direct display in the
UI or final answer.

This tool is deterministic, local-only, and has no side effects.
