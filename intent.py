TRIGGERS = {
    "bug": [
        "this is a bug",
        "this broke",
        "it broke",
        "broken",
        "bug",
        "regression",
        "error",
        "fails",
        "crash",
        "crashes",
        "exception",
        "stack trace",
        "doesn't work",
        "does not work",
        "failed",
        "failure",
    ],
    "feature": [
        "we should build",
        "add this",
        "feature",
        "enhancement",
        "support",
        "would be nice",
        "request",
        "could we",
        "can we add",
        "it would be great",
    ],
    "task": [
        "track this",
        "todo",
        "task",
        "follow up",
        "needs to be fixed",
        "needs fixing",
        "clean up",
        "refactor",
        "document",
        "update docs",
        "chore",
    ],
    "research": [
        "investigate",
        "research",
        "explore",
        "spike",
        "evaluate",
        "prototype",
        "assess",
    ],
}


def detect_intent(text: str):
    if not text:
        return None
    lowered = text.lower()
    for intent_type, phrases in TRIGGERS.items():
        for phrase in phrases:
            if phrase in lowered:
                return {
                    "type": intent_type,
                    "summary": _summarize(text),
                    "confidence": "high",
                }
    return None


def _summarize(text: str):
    cleaned = " ".join(text.strip().split())
    if len(cleaned) <= 80:
        return cleaned
    return cleaned[:77] + "..."
