
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
