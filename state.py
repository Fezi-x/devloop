import json
import os
import re

from errors import raise_error

STATE_PATH = "state.json"


def _default_state():
    return {
        "mode": "off",
        "active_repo": None,
    }


def get_state(path: str = STATE_PATH):
    if not os.path.exists(path):
        return _default_state()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        raise_error("state_invalid", "state.json is not valid JSON.", {"path": path})
    except OSError as exc:
        raise_error("state_error", "Failed to read state.json.", {"path": path, "error": str(exc)})

    merged = _default_state()
    if isinstance(data, dict):
        merged.update(data)
    return merged


def save_state(state: dict, path: str = STATE_PATH):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except OSError as exc:
        raise_error("state_error", "Failed to write state.json.", {"path": path, "error": str(exc)})


def set_mode(mode: str, path: str = STATE_PATH):
    if mode not in ("on", "off"):
        raise_error("bad_request", "Mode must be 'on' or 'off'.")
    state = get_state(path)
    state["mode"] = mode
    save_state(state, path)
    return state


def set_active_repo(repo: str, path: str = STATE_PATH):
    state = get_state(path)
    state["active_repo"] = repo
    save_state(state, path)
    return state


def _find_git_root(start: str = None):
    cur = os.path.abspath(start or os.getcwd())
    while True:
        candidate = os.path.join(cur, ".git")
        if os.path.isdir(candidate):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent


def _parse_remote_url(url: str):
    if not url:
        return None
    url = url.strip()
    https_match = re.search(r"https?://[^/]+/([^/]+)/([^/]+?)(?:\\.git)?$", url)
    if https_match:
        return f"{https_match.group(1)}/{https_match.group(2)}"
    ssh_match = re.search(r"git@[^:]+:([^/]+)/([^/]+?)(?:\\.git)?$", url)
    if ssh_match:
        return f"{ssh_match.group(1)}/{ssh_match.group(2)}"
    return None


def _discover_repo():
    root = _find_git_root()
    if not root:
        return None
    config_path = os.path.join(root, ".git", "config")
    if not os.path.exists(config_path):
        return None
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return None

    in_origin = False
    for raw in lines:
        line = raw.strip()
        if line.startswith("["):
            in_origin = line.lower() == '[remote "origin"]'
            continue
        if in_origin and line.lower().startswith("url"):
            parts = line.split("=", 1)
            if len(parts) == 2:
                return _parse_remote_url(parts[1].strip())
    return None


def get_active_repo(path: str = STATE_PATH):
    repo = get_state(path).get("active_repo")
    if repo:
        return repo
    return _discover_repo()


def is_mode_on(path: str = STATE_PATH):
    return get_state(path).get("mode") == "on"
