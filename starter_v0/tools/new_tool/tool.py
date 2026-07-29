from __future__ import annotations

import re
from collections import Counter
from typing import Any

from tools._shared import fold_text, terms


ACTION_MARKERS = (
    "todo",
    "to do",
    "action",
    "follow up",
    "next step",
    "must",
    "need",
    "needs",
    "should",
    "can phai",
    "nen",
    "viec can lam",
    "han chot",
)


def _sentences(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text or "").strip()
    if not normalized:
        return []
    parts = re.split(r"(?<=[.!?])\s+|[\r\n]+", normalized)
    return [part.strip(" -\t") for part in parts if part.strip(" -\t")]


def _score_sentence(sentence: str, query_terms: set[str], keyword_counts: Counter[str]) -> int:
    sentence_terms = terms(sentence)
    score = sum(keyword_counts.get(term, 0) for term in sentence_terms)
    score += 3 * len(sentence_terms & query_terms)
    if any(marker in fold_text(sentence) for marker in ACTION_MARKERS):
        score += 2
    return score


def analyze_notes(text: str = "", focus: str = "", max_items: int = 5) -> dict[str, Any]:
    try:
        sentences = _sentences(text)
        limit = max(1, int(max_items or 5))
        query_terms = terms(focus)
        keyword_counts = Counter(term for sentence in sentences for term in terms(sentence))

        ranked = sorted(
            enumerate(sentences),
            key=lambda pair: (_score_sentence(pair[1], query_terms, keyword_counts), -pair[0]),
            reverse=True,
        )
        summary = [sentence for _, sentence in ranked[:limit]]
        summary.sort(key=lambda sentence: sentences.index(sentence))

        actions = [
            sentence
            for sentence in sentences
            if any(marker in fold_text(sentence) for marker in ACTION_MARKERS)
        ][:limit]
        keywords = [term for term, _ in keyword_counts.most_common(limit)]
        markdown_parts = []
        if summary:
            markdown_parts.extend(["## Summary", *[f"- {sentence}" for sentence in summary]])
        if actions:
            markdown_parts.extend(["", "## Action items", *[f"- {sentence}" for sentence in actions]])
        if keywords:
            markdown_parts.extend(["", "## Keywords", ", ".join(keywords)])

        return {
            "tool": "analyze_notes",
            "focus": focus,
            "summary": summary,
            "action_items": actions,
            "keywords": keywords,
            "markdown": "\n".join(markdown_parts).strip(),
            "stats": {
                "chars": len(text or ""),
                "words": len(re.findall(r"\S+", text or "")),
                "sentences": len(sentences),
            },
        }
    except Exception as exc:
        return {"tool": "analyze_notes", "error": type(exc).__name__, "message": str(exc)}
