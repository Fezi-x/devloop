from errors import raise_error
from issue_template import build_issue_body, build_issue_title, expand_compact_body
from issues import create_issue, edit_issue, get_issue, list_issues
from state import get_active_repo, set_active_repo

_STATE_MAP = {
    "o": "open",
    "open": "open",
    "p": "open",
    "progress": "open",
    "in_progress": "open",
    "d": "closed",
    "done": "closed",
    "closed": "closed",
}

_KIND_MAP = {
    "b": "bug",
    "bug": "bug",
    "f": "feature",
    "feature": "feature",
    "t": "task",
    "task": "task",
    "r": "research",
    "research": "research",
}


class CompactCommand:
    def __init__(self):
        self.action = None
        self.repo = None
        self.issue = None
        self.title = None
        self.body = None
        self.kind = None
        self.state = None


def _is_repo(token: str):
    return "/" in token and not token.startswith("/")


def _parse_kv(token: str):
    if ":" in token:
        key, value = token.split(":", 1)
    elif "=" in token:
        key, value = token.split("=", 1)
    else:
        return None, None
    key = key.strip().lower()
    value = value.strip()
    return key, value


def parse_compact(tokens):
    if not tokens:
        raise_error("bad_request", "Missing compact command.")

    cmd = CompactCommand()
    action = tokens[0].lower()
    if action in ("c", "create"):
        cmd.action = "create"
    elif action in ("e", "edit"):
        cmd.action = "edit"
    elif action in ("l", "list"):
        cmd.action = "list"
    elif action in ("g", "get"):
        cmd.action = "get"
    else:
        raise_error("bad_request", f"Unknown compact action: {action}")

    for token in tokens[1:]:
        if token.isdigit() and cmd.issue is None:
            cmd.issue = int(token)
            continue
        if _is_repo(token) and cmd.repo is None:
            cmd.repo = token
            continue

        key, value = _parse_kv(token)
        if key is None:
            continue

        if key in ("r", "repo"):
            cmd.repo = value
        elif key in ("t", "title"):
            cmd.title = value
        elif key in ("b", "body"):
            cmd.body = value
        elif key in ("k", "kind", "type"):
            cmd.kind = value
        elif key in ("s", "state"):
            cmd.state = value
        elif key in ("i", "issue"):
            if value.isdigit():
                cmd.issue = int(value)

    return cmd


def _resolve_repo(cmd: CompactCommand):
    if cmd.repo:
        set_active_repo(cmd.repo)
        return cmd.repo
    repo = get_active_repo()
    if not repo:
        raise_error("config_missing", "Active repo not set. Provide r:<owner/name>.")
    return repo


def _apply_kind_prefix(kind: str, title: str):
    if not title:
        return title
    if title.strip().startswith("["):
        return title
    kind = _KIND_MAP.get((kind or "").lower(), "task")
    return build_issue_title(kind, title)


def _looks_compact(body: str):
    if not body:
        return False
    return ("|" in body or ";" in body) and (":" in body or "=" in body)


def _expand_body(body: str):
    if not body:
        return body
    if _looks_compact(body):
        return expand_compact_body(body)
    return body


def run_compact(tokens):
    cmd = parse_compact(tokens)
    repo = _resolve_repo(cmd)

    if cmd.action == "list":
        return list_issues(repo)

    if cmd.action == "get":
        if cmd.issue is None:
            raise_error("bad_request", "Missing issue number.")
        return get_issue(repo, cmd.issue)

    if cmd.action == "create":
        if not cmd.title:
            raise_error("bad_request", "Missing title. Use t:<title> or t=<title>.")
        title = _apply_kind_prefix(cmd.kind, cmd.title)
        body = _expand_body(cmd.body) if cmd.body else None
        if body and body.startswith("## Context") is False and _looks_compact(cmd.body or ""):
            body = build_issue_body(cmd.body)
        return create_issue(repo, title, body)

    if cmd.action == "edit":
        if cmd.issue is None:
            raise_error("bad_request", "Missing issue number.")
        title = _apply_kind_prefix(cmd.kind, cmd.title) if cmd.title else None
        body = _expand_body(cmd.body) if cmd.body else None
        state = cmd.state
        if state:
            state = _STATE_MAP.get(state, state)
        return edit_issue(repo, cmd.issue, title=title, body=body, state=state)

    raise_error("bad_request", "Unsupported compact action.")

