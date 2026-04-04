import json
import sys

from auth import device_flow_auth
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


def run():
    if len(sys.argv) < 2:
        exit_with_error(DevloopError("bad_request", "Missing command."))

    cmd = sys.argv[1]

    try:
        if cmd == "auth":
            scope = sys.argv[2] if len(sys.argv) > 2 else "repo"
            device_flow_auth(scope=scope)
            _print_json({"status": "ok", "token_saved": True})
            return

        if cmd == "create":
            if len(sys.argv) < 4:
                raise DevloopError("bad_request", "Usage: create <owner/name> <title> [body]")
            repo = sys.argv[2]
            title = sys.argv[3]
            body = sys.argv[4] if len(sys.argv) > 4 else None
            data = create_issue(repo, title, body)
            _print_json(data)
            return

        if cmd == "edit":
            if len(sys.argv) < 4:
                raise DevloopError("bad_request", "Usage: edit <owner/name> <number> [title] [body] [state]")
            repo = sys.argv[2]
            number = int(sys.argv[3])
            remaining = sys.argv[4:]

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
