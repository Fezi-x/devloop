import json
import sys


class DevloopError(Exception):
    def __init__(self, code: str, message: str, details=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self):
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


def raise_error(code: str, message: str, details=None):
    raise DevloopError(code, message, details)


def print_error(err: Exception):
    if isinstance(err, DevloopError):
        payload = err.to_dict()
    else:
        payload = {
            "error": {
                "code": "unexpected_error",
                "message": str(err),
                "details": {},
            }
        }
    print(json.dumps(payload, indent=2))


def exit_with_error(err: Exception, status: int = 1):
    print_error(err)
    raise SystemExit(status)
