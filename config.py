import json
import os

from errors import raise_error

TOKEN_PATH = "token.json"
ENV_PATH = ".env"
_ENV_LOADED = False


def load_env(path: str = ENV_PATH):
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    if not os.path.exists(path):
        _ENV_LOADED = True
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("\"'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except OSError as exc:
        raise_error("config_error", "Failed to read .env file.", {"path": path, "error": str(exc)})
    _ENV_LOADED = True


def get_repo():
    load_env()
    repo = os.getenv("DEVLOOP_REPO")
    if not repo:
        raise_error("config_missing", "DEVLOOP_REPO not set.")
    return repo


def _read_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        raise_error("token_invalid", "token.json is not valid JSON.", {"path": path})


def get_token(path: str = TOKEN_PATH):
    load_env()
    data = _read_json(path)
    if not data:
        raise_error("token_missing", "OAuth token not found. Run auth first.", {"path": path})
    token = data.get("access_token")
    if not token or not isinstance(token, str):
        raise_error("token_invalid", "OAuth token is missing or invalid.", {"path": path})
    return token
