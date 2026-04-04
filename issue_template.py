
def build_issue_title(issue_type: str, summary: str):
    label = issue_type.upper()
    summary = summary.strip()
    return f"[{label}] {summary}"


def build_issue_body(context: str, expected: str = "", scope: str = "", acceptance=None):
    if acceptance is None or len(acceptance) == 0:
        acceptance = ["Define success criteria"]
    lines = [
        "## Context",
        context.strip() if context else "",
        "",
        "## Expected",
        expected.strip() if expected else "",
        "",
        "## Scope",
        scope.strip() if scope else "",
        "",
        "## Acceptance Criteria",
    ]
    for item in acceptance:
        lines.append(f"- [ ] {item}")
    return "\n".join(lines).strip()


def _split_kv(part: str):
    if ":" in part:
        return part.split(":", 1)
    if "=" in part:
        return part.split("=", 1)
    return None, None


def expand_compact_body(compact: str):
    raw_parts = []
    for chunk in compact.split(";"):
        raw_parts.extend(chunk.split("|"))
    parts = [p for p in raw_parts if p]
    context = ""
    expected = ""
    scope = ""
    acceptance = []
    for part in parts:
        key, value = _split_kv(part)
        if not key:
            continue
        key = key.strip().lower()
        value = value.strip()
        if key in ("c", "ctx", "context"):
            context = value
        elif key in ("e", "exp", "expected"):
            expected = value
        elif key in ("s", "scope"):
            scope = value
        elif key in ("a", "ac", "acceptance"):
            acceptance = [v.strip() for v in value.split(",") if v.strip()]
    return build_issue_body(context, expected=expected, scope=scope, acceptance=acceptance)
