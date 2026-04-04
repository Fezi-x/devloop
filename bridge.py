import argparse
import json
import subprocess

from errors import DevloopError, exit_with_error
from intent import detect_intent
from issue_template import build_issue_body, build_issue_title
from state import get_active_repo, is_mode_on, set_active_repo


def _print_json(payload):
    print(json.dumps(payload, indent=2))


def _run_create(repo: str, title: str, body: str):
    cmd = ["python", "cli.py", "create", repo, title, body]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise DevloopError("executor_error", "CLI create failed.", {"stderr": result.stderr, "stdout": result.stdout})
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw": result.stdout}


def main():
    parser = argparse.ArgumentParser(description="Passive capture bridge for Devloop")
    parser.add_argument("message", help="User message to analyze")
    parser.add_argument("--confirm", action="store_true", help="Create issue if intent is detected")
    parser.add_argument("--repo", default=None, help="Override repo owner/name")
    parser.add_argument("--expected", default="", help="Expected behavior")
    parser.add_argument("--scope", default="", help="Scope area")
    args = parser.parse_args()

    try:
        if not is_mode_on():
            _print_json({"status": "mode_off"})
            return

        intent = detect_intent(args.message)
        if not intent:
            _print_json({"status": "no_intent"})
            return

        issue_type = intent["type"]
        summary = intent["summary"]
        title = build_issue_title(issue_type, summary)
        body = build_issue_body(args.message, expected=args.expected, scope=args.scope)

        repo = args.repo or get_active_repo()
        if not repo:
            raise DevloopError("config_missing", "Active repo not set. Provide --repo or set active repo.")
        if args.repo:
            set_active_repo(args.repo)

        if not args.confirm:
            _print_json({"status": "detected", "type": issue_type, "title": title, "body": body, "repo": repo})
            return

        data = _run_create(repo, title, body)
        _print_json({"status": "created", "issue": data})

    except DevloopError as exc:
        exit_with_error(exc)


if __name__ == "__main__":
    main()
