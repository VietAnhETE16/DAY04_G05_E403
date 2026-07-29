from __future__ import annotations

import re
from typing import Any

def analyze_notes(text: str = "", focus: str = "", max_items: int = 5) -> dict[str, Any]:
    """
    Analyze local text or notes to extract:
    - A summary (focusing on the specified 'focus' topic if provided)
    - Action items (lines starting with todo, task, [ ], or containing action verbs/imperatives)
    - Key terms / keywords
    - Basic statistics (word count, line count)
    """
    if not text:
        return {
            "summary": "No text provided to analyze.",
            "action_items": [],
            "keywords": [],
            "stats": {"words": 0, "lines": 0}
        }
        
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    words = text.split()
    
    # 1. Extract action items
    action_items = []
    for line in lines:
        lower_line = line.lower()
        is_action = False
        action_text = ""
        # Check standard indicators
        if lower_line.startswith(("todo", "task", "- todo", "- task", "[ ]", "- [ ]")):
            is_action = True
            action_text = re.sub(r"^(\-\s*)?(todo|task|\[\s*\]|\-\s*\[\s*\])\s*[:\-]?\s*", "", line, flags=re.IGNORECASE).strip()
        elif any(lower_line.startswith(p) for p in ["need to ", "should ", "must ", "please "]):
            is_action = True
            action_text = line
            
        if is_action and action_text:
            action_items.append(action_text)
            if len(action_items) >= max_items:
                break
                
    # 2. Extract keywords (simple word frequency excluding common stopwords)
    stopwords = {
        "the", "and", "a", "of", "to", "in", "is", "you", "that", "it", "he", "was", "for", "on", "are", 
        "as", "with", "his", "they", "i", "at", "be", "this", "have", "from", "or", "one", "had", "by", 
        "word", "but", "not", "what", "all", "were", "we", "when", "your", "can", "said", "there", "use",
        "an", "each", "which", "she", "do", "how", "their", "if", "will", "up", "other", "about", "out",
        "many", "then", "them", "these", "so", "some", "her", "would", "make", "like", "him", "into",
        "has", "look", "two", "more", "write", "go", "see", "number", "no", "way", "could", "people",
        "my", "than", "first", "water", "been", "call", "who", "oil", "its", "now", "find", "long", "down",
        "day", "did", "get", "come", "made", "may", "part"
    }
    word_freq = {}
    for w in words:
        clean_w = re.sub(r"[^\w]", "", w).lower()
        if clean_w and clean_w not in stopwords and len(clean_w) > 3:
            word_freq[clean_w] = word_freq.get(clean_w, 0) + 1
            
    sorted_keywords = sorted(word_freq.keys(), key=lambda k: word_freq[k], reverse=True)
    keywords = sorted_keywords[:max_items]
    
    # 3. Create a summary
    # If a focus is provided, filter lines containing the focus keyword
    summary_lines = []
    if focus:
        focus_lower = focus.lower()
        summary_lines = [line for line in lines if focus_lower in line.lower()]
        
    if not summary_lines:
        summary_lines = lines[:3]  # fallback to first 3 lines
        
    summary = " ".join(summary_lines[:3])
    
    return {
        "summary": summary,
        "action_items": action_items,
        "keywords": keywords,
        "stats": {
            "words": len(words),
            "lines": len(lines)
        }
    }
