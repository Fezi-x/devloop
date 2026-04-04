import os
import json
import argparse
import requests

DEFAULT_API_BASE = "https://api.github.com"


def _require_token():
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PAT")
    if not token:
        raise SystemExit("Missing GITHUB_TOKEN or GITHUB_PAT in environment.")
    return token


def _headers(token: str):
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "lead-intelligence-engine/issue-tool",
    }


def create_issue(repo: str, title: str, body: str = None, labels=None, assignees=None, api_base=DEFAULT_API_BASE):
    token = _require_token()
    url = f"{api_base}/repos/{repo}/issues"
    payload = {"title": title}
    if body is not None:
        payload["body"] = body
    if labels:
        payload["labels"] = labels
    if assignees:
        payload["assignees"] = assignees

    resp = requests.post(url, headers=_headers(token), json=payload, timeout=20)
    if resp.status_code >= 300:
        raise SystemExit(f"Create failed: {resp.status_code} {resp.text[:300]}")
    data = resp.json()
    print(json.dumps({"number": data.get("number"), "url": data.get("html_url")}, indent=2))


def edit_issue(repo: str, issue_number: int, title: str = None, body: str = None, state: str = None, labels=None, assignees=None, api_base=DEFAULT_API_BASE):
    token = _require_token()
    url = f"{api_base}/repos/{repo}/issues/{issue_number}"
    payload = {}
    if title is not None:
        payload["title"] = title
    if body is not None:
        payload["body"] = body
    if state is not None:
        payload["state"] = state
    if labels is not None:
        payload["labels"] = labels
    if assignees is not None:
        payload["assignees"] = assignees

    if not payload:
        raise SystemExit("Nothing to update. Provide at least one field.")

    resp = requests.patch(url, headers=_headers(token), json=payload, timeout=20)
    if resp.status_code >= 300:
        raise SystemExit(f"Edit failed: {resp.status_code} {resp.text[:300]}")
    data = resp.json()
    print(json.dumps({"number": data.get("number"), "url": data.get("html_url"), "state": data.get("state")}, indent=2))


def _parse_csv(value: str):
    if not value:
        return None
    return [v.strip() for v in value.split(",") if v.strip()]


def main():
    parser = argparse.ArgumentParser(description="Create or edit GitHub issues via API")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_create = sub.add_parser("create", help="Create a new issue")
    p_create.add_argument("repo", help="owner/name")
    p_create.add_argument("title", help="Issue title")
    p_create.add_argument("--body", default=None, help="Issue body")
    p_create.add_argument("--labels", default=None, help="Comma-separated labels")
    p_create.add_argument("--assignees", default=None, help="Comma-separated assignees")

    p_edit = sub.add_parser("edit", help="Edit an existing issue")
    p_edit.add_argument("repo", help="owner/name")
    p_edit.add_argument("issue_number", type=int, help="Issue number")
    p_edit.add_argument("--title", default=None, help="New title")
    p_edit.add_argument("--body", default=None, help="New body")
    p_edit.add_argument("--state", default=None, choices=["open", "closed"], help="State")
    p_edit.add_argument("--labels", default=None, help="Comma-separated labels (replaces)")
    p_edit.add_argument("--assignees", default=None, help="Comma-separated assignees (replaces)")

    args = parser.parse_args()

    if args.cmd == "create":
        create_issue(
            args.repo,
            args.title,
            body=args.body,
            labels=_parse_csv(args.labels),
            assignees=_parse_csv(args.assignees),
        )
    elif args.cmd == "edit":
        edit_issue(
            args.repo,
            args.issue_number,
            title=args.title,
            body=args.body,
            state=args.state,
            labels=_parse_csv(args.labels),
            assignees=_parse_csv(args.assignees),
        )


if __name__ == "__main__":
    main()
