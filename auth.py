import json
import os
import time
import webbrowser
import requests

from config import load_env
from errors import raise_error

TOKEN_PATH = "token.json"
GITHUB_DEVICE_CODE_URL = "https://github.com/login/device/code"
GITHUB_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
DEFAULT_SCOPE = "repo"


def _client_id():
    load_env()
    client_id = os.getenv("GITHUB_CLIENT_ID")
    if not client_id:
        raise_error("config_missing", "Missing GITHUB_CLIENT_ID in environment.")
    return client_id


def device_flow_auth(scope: str = DEFAULT_SCOPE, poll_interval: int = None):
    client_id = _client_id()
    headers = {"Accept": "application/json", "User-Agent": "devloop/oauth-issue-client"}

    resp = requests.post(
        GITHUB_DEVICE_CODE_URL,
        data={"client_id": client_id, "scope": scope},
        headers=headers,
        timeout=20,
    )
    if resp.status_code >= 300:
        raise_error("oauth_request_failed", "Failed to start device flow.", {"status": resp.status_code, "body": resp.text})

    data = resp.json()
    device_code = data.get("device_code")
    user_code = data.get("user_code")
    verification_uri = data.get("verification_uri")
    verification_uri_complete = data.get("verification_uri_complete")
    expires_in = data.get("expires_in")
    interval = data.get("interval") or 5

    if poll_interval is not None:
        interval = max(1, int(poll_interval))

    if not device_code or not user_code or not verification_uri:
        raise_error("oauth_response_invalid", "Device flow response missing required fields.", {"response": data})

    print(
        json.dumps(
            {
                "status": "pending_authorization",
                "device_code": device_code,
                "user_code": user_code,
                "verification_uri": verification_uri,
                "verification_uri_complete": verification_uri_complete,
                "expires_in": expires_in,
                "interval": interval,
            },
            indent=2,
        )
    )
    try:
        if verification_uri_complete:
            webbrowser.open(verification_uri_complete, new=2)
        else:
            webbrowser.open(verification_uri, new=2)
    except Exception:
        pass

    start = time.time()
    while True:
        if expires_in and (time.time() - start) > int(expires_in):
            raise_error("oauth_expired", "Device code expired before authorization completed.")

        token_resp = requests.post(
            GITHUB_ACCESS_TOKEN_URL,
            data={
                "client_id": client_id,
                "device_code": device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            },
            headers=headers,
            timeout=20,
        )
        if token_resp.status_code >= 300:
            raise_error("oauth_request_failed", "Token request failed.", {"status": token_resp.status_code, "body": token_resp.text})

        token_data = token_resp.json()
        if "access_token" in token_data:
            token = token_data["access_token"]
            with open(TOKEN_PATH, "w", encoding="utf-8") as f:
                json.dump({"access_token": token}, f, indent=2)
            return {"access_token": token}

        error = token_data.get("error")
        if error == "authorization_pending":
            time.sleep(interval)
            continue
        if error == "slow_down":
            interval = interval + 5
            time.sleep(interval)
            continue
        if error == "access_denied":
            raise_error("oauth_denied", "User denied authorization.")
        if error == "expired_token":
            raise_error("oauth_expired", "Device code expired.")

        raise_error("oauth_error", "Unexpected OAuth error.", {"response": token_data})

if __name__ == "__main__":
    import sys

    scope = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SCOPE
    device_flow_auth(scope=scope)
    print(json.dumps({"status": "ok", "token_saved": True}, indent=2))


