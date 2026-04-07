import json
import os

from errors import raise_error

_ENV_LOADED = False


def get_config_dir():
    override = os.getenv("DEVLOOP_CONFIG")
    if override:
        return override
    home = os.path.expanduser("~")
    return os.path.join(home, ".devloop")


def ensure_config_dir():
    path = get_config_dir()
    if not os.path.exists(path):
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as exc:
            raise_error("config_error", "Failed to create config directory.", {"path": path, "error": str(exc)})
    return path


def _env_paths():
    return [
        os.path.join(get_config_dir(), ".env"),
    ]


def load_env(paths=None):
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    paths = paths or _env_paths()
    for path in paths:
        if not os.path.exists(path):
            continue
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


def get_token_path():
    return os.path.join(get_config_dir(), "token.json")


def get_state_path():
    return "state.json"


def get_token(path: str = None):
    load_env()
    path = path or get_token_path()
    data = _read_json(path)
    if not data:
        raise_error("token_missing", "OAuth token not found. Run auth first.", {"path": path})
    token = data.get("access_token")
    if not token or not isinstance(token, str):
        raise_error("token_invalid", "OAuth token is missing or invalid.", {"path": path})
    return token
