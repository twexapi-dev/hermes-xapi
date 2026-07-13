from __future__ import annotations

import json
import os
from math import isfinite
from typing import Any, cast
from urllib.parse import urljoin

import httpx

ALLOWED_PATH_PREFIXES = ("/twitter/", "/x/", "/v2/", "/dm/")
ALLOWED_EXACT_PATHS = ("/balance",)
DEFAULT_BASE_URL = "https://api.twexapi.io"
TIMEOUT_SECONDS = 30.0


def _env_text(name: str, default: str = "") -> str:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip()
    return normalized or default


def _request_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()


def normalize_query_params(value: Any) -> dict[str, str] | None:
    if not isinstance(value, dict):
        return None
    output: dict[str, str] = {}
    for key, item in cast("dict[object, object]", value).items():
        if not isinstance(key, str):
            continue
        normalized_key = key.strip()
        if not normalized_key:
            continue
        if isinstance(item, bool):
            output[normalized_key] = str(item).lower()
        elif isinstance(item, (str, int)) or (isinstance(item, float) and isfinite(item)):
            output[normalized_key] = str(item)
    return output or None


def base_url() -> str:
    return _env_text("TWEXAPI_BASE_URL", DEFAULT_BASE_URL).rstrip("/") + "/"


def api_key() -> str:
    return _env_text("TWEXAPI_KEY")


def check_api_available() -> bool:
    return bool(api_key())


def action_enabled() -> bool:
    return check_api_available() and _env_text("HERMES_XAPI_ENABLE_ACTIONS").lower() == "true"


def build_headers(key: str, *, has_body: bool) -> dict[str, str]:
    headers: dict[str, str] = {}
    if key:
        headers["authorization"] = f"Bearer {key}"
    if has_body:
        headers["content-type"] = "application/json"
    return headers


def _path_allowed(path: str) -> bool:
    return path in ALLOWED_EXACT_PATHS or path.startswith(ALLOWED_PATH_PREFIXES)


def request(
    method: Any,
    path: Any,
    query: Any = None,
    body: Any | None = None,
) -> Any:
    normalized_method = _request_text(method).upper() or "GET"
    normalized_path = _request_text(path)
    params = normalize_query_params(query)
    if not _path_allowed(normalized_path):
        return {
            "success": False,
            "error": ("Path must start with /twitter/, /x/, /v2/, /dm/, or be /balance."),
        }
    if "?" in normalized_path or "#" in normalized_path:
        return {
            "success": False,
            "error": "Pass query parameters through the query object, not in the path.",
        }

    key = api_key()
    if not key:
        return {"success": False, "error": "TWEXAPI_KEY is not configured."}

    url = urljoin(base_url(), normalized_path.lstrip("/"))
    try:
        with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
            response = client.request(
                method=normalized_method,
                url=url,
                params=params,
                json=body,
                headers=build_headers(key, has_body=body is not None),
            )
        try:
            payload = response.json()
        except ValueError:
            payload = {"text": response.text}
        if not response.is_success:
            return {
                "success": False,
                "error": "API request failed.",
                "status_code": response.status_code,
                "response": payload,
            }
        return payload
    except httpx.HTTPError as exc:
        return {"success": False, "error": str(exc)}


def dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))
