import json
import os

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


def get_active_repo(path: str = STATE_PATH):
    return get_state(path).get("active_repo")


def is_mode_on(path: str = STATE_PATH):
    return get_state(path).get("mode") == "on"
