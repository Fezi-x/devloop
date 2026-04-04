import json
import sys

from auth import device_flow_auth
from compact import run_compact
from errors import DevloopError, exit_with_error
from issues import create_issue, edit_issue, list_issues, get_issue
from state import get_active_repo, get_state, set_active_repo, set_mode


def _print_json(payload):
    print(json.dumps(payload, indent=2))


def _clean(value):
    if value is None:
        return None
    trimmed = value.strip()
    if trimmed == "" or trimmed in ("-", "_"):
        return None
    return value


def _extract_tag(args):
    if not args:
        return None, []
    tag = None
    remaining = []
    i = 0
    while i < len(args):
        token = args[i]
        if token.startswith("--tag="):
            tag = token.split("=", 1)[1].strip()
        elif token == "--tag":
            if i + 1 >= len(args):
                raise DevloopError("bad_request", "Missing value for --tag.")
            tag = args[i + 1].strip()
            i += 1
        else:
            remaining.append(token)
        i += 1
    if tag == "":
        tag = None
    return tag, remaining


def _apply_tag_prefix(tag, title):
    if not tag or not title:
        return title
    trimmed = title.strip()
    expected = f"[{tag}]"
    if trimmed.lower().startswith(expected.lower()):
        return title
    return f"{expected} {title}"


def run():
    if len(sys.argv) < 2:
        exit_with_error(DevloopError("bad_request", "Missing command."))

    cmd = sys.argv[1]

    try:
        if cmd in ("/d", "d"):
            data = run_compact(sys.argv[2:])
            _print_json(data)
            return

        if cmd == "auth":
            scope = sys.argv[2] if len(sys.argv) > 2 else "repo"
            device_flow_auth(scope=scope)
            _print_json({"status": "ok", "token_saved": True})
            return

        if cmd == "create":
            if len(sys.argv) < 4:
                raise DevloopError("bad_request", "Usage: create <owner/name> <title> [body] [--tag TAG]")
            repo = sys.argv[2]
            tag, remaining = _extract_tag(sys.argv[3:])
            if not remaining:
                raise DevloopError("bad_request", "Missing title. Usage: create <owner/name> <title> [body]")
            title = remaining[0]
            body = remaining[1] if len(remaining) > 1 else None
            title = _apply_tag_prefix(tag, title)
            data = create_issue(repo, title, body)
            _print_json(data)
            return

        if cmd == "edit":
            if len(sys.argv) < 4:
                raise DevloopError("bad_request", "Usage: edit <owner/name> <number> [title] [body] [state] [--tag TAG]")
            repo = sys.argv[2]
            number = int(sys.argv[3])
            tag, remaining = _extract_tag(sys.argv[4:])

            title = None
            body = None
            state = None

            if len(remaining) == 1 and remaining[0] in ("open", "closed"):
                state = remaining[0]
            else:
                if len(remaining) >= 1:
                    title = _clean(remaining[0])
                if len(remaining) >= 2:
                    body = _clean(remaining[1])
                if len(remaining) >= 3:
                    state = _clean(remaining[2])
            if tag and not title:
                raise DevloopError("bad_request", "Tag requires a title when editing.")
            title = _apply_tag_prefix(tag, title)

            data = edit_issue(repo, number, title=title, body=body, state=state)
            _print_json(data)
            return

        if cmd == "list":
            if len(sys.argv) < 3:
                raise DevloopError("bad_request", "Usage: list <owner/name>")
            repo = sys.argv[2]
            data = list_issues(repo)
            _print_json(data)
            return

        if cmd == "get":
            if len(sys.argv) < 4:
                raise DevloopError("bad_request", "Usage: get <owner/name> <number>")
            repo = sys.argv[2]
            number = int(sys.argv[3])
            data = get_issue(repo, number)
            _print_json(data)
            return

        if cmd == "mode":
            if len(sys.argv) < 3:
                raise DevloopError("bad_request", "Usage: mode <on|off>")
            state = set_mode(sys.argv[2])
            _print_json({"status": "ok", "state": state})
            return

        if cmd == "repo":
            if len(sys.argv) < 3:
                raise DevloopError("bad_request", "Usage: repo <get|set> [owner/name]")
            action = sys.argv[2]
            if action == "get":
                _print_json({"repo": get_active_repo(), "state": get_state()})
                return
            if action == "set":
                if len(sys.argv) < 4:
                    raise DevloopError("bad_request", "Usage: repo set <owner/name>")
                state = set_active_repo(sys.argv[3])
                _print_json({"status": "ok", "state": state})
                return
            raise DevloopError("bad_request", "Usage: repo <get|set> [owner/name]")

        raise DevloopError("bad_request", f"Unknown command: {cmd}")

    except DevloopError as exc:
        exit_with_error(exc)


if __name__ == "__main__":
    run()
