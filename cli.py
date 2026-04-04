import json
import sys

from auth import device_flow_auth
from errors import DevloopError, exit_with_error
from issues import create_issue, edit_issue, list_issues


def _print_json(payload):
    print(json.dumps(payload, indent=2))


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
            title = sys.argv[4] if len(sys.argv) > 4 else None
            body = sys.argv[5] if len(sys.argv) > 5 else None
            state = sys.argv[6] if len(sys.argv) > 6 else None
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

        raise DevloopError("bad_request", f"Unknown command: {cmd}")

    except DevloopError as exc:
        exit_with_error(exc)


if __name__ == "__main__":
    run()
