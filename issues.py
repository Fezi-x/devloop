import requests

from config import get_token
from errors import raise_error

API = "https://api.github.com"


def _headers():
    return {
        "Authorization": f"Bearer {get_token()}",
        "Accept": "application/vnd.github+json",
    }


def _request(method: str, url: str, json_body=None):
    try:
        resp = requests.request(method, url, headers=_headers(), json=json_body, timeout=20)
    except requests.RequestException as exc:
        raise_error("api_error", "Network error contacting GitHub API.", {"error": str(exc)})

    if resp.status_code >= 300:
        details = {"status": resp.status_code}
        try:
            details["body"] = resp.json()
        except ValueError:
            details["body"] = resp.text
        code = "bad_request" if 400 <= resp.status_code < 500 else "api_error"
        raise_error(code, "GitHub API request failed.", details)

    return resp.json()


def create_issue(repo: str, title: str, body: str = None):
    payload = {"title": title}
    if body is not None:
        payload["body"] = body
    return _request("POST", f"{API}/repos/{repo}/issues", json_body=payload)


def edit_issue(repo: str, number: int, title: str = None, body: str = None, state: str = None):
    data = {}
    if title is not None:
        data["title"] = title
    if body is not None:
        data["body"] = body
    if state is not None:
        data["state"] = state
    if not data:
        raise_error("bad_request", "Nothing to update. Provide at least one field.")
    return _request("PATCH", f"{API}/repos/{repo}/issues/{number}", json_body=data)


def list_issues(repo: str):
    return _request("GET", f"{API}/repos/{repo}/issues")


def get_issue(repo: str, number: int):
    return _request("GET", f"{API}/repos/{repo}/issues/{number}")
