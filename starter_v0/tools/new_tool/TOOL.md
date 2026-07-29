# new_tool

Analyze notes, raw texts, logs, transcripts, or minutes of meetings locally to extract summaries, key action items (TODOs), and statistics.

## When to use
- When the user provides a chunk of raw text, notes, meeting minutes, logs, or reports and asks for a summary, key tasks/action items, keywords, or basic statistics.
- For local text analysis that does not require searching the web or external APIs.

## When NOT to use
- Do NOT use when the user asks for information that requires searching the web (use `lookup` instead) or Twitter (use `social_search` or `timeline` instead).
- Do NOT use for querying arXiv papers (use `papers` or `paper_text` instead).

## Arguments
- `text` (string, required): The raw text content to be analyzed.
- `focus` (string, optional): A keyword or topic to prioritize when extracting the summary. Default is `""`.
- `max_items` (integer, optional): The maximum number of action items or keywords to return. Default is `5`.

## Outputs
Returns a JSON object with:
- `summary` (string): A short summary of the text (focused on `focus` if provided).
- `action_items` (list of strings): Extracted tasks or action items (todos).
- `keywords` (list of strings): Top keywords sorted by frequency.
- `stats` (object): Word count and line count statistics.

## Confirmation boundary
No confirmation is required because this tool only performs local text analysis with no side effects.
