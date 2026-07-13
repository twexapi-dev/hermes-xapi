from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlsplit

import yaml

METHODS = {"get", "post", "put", "patch", "delete"}
EXPECTED_ARG_COUNT = 2
OUTPUT = Path(__file__).resolve().parents[1] / "hermes_xapi" / "catalog_data.json"

JsonDict = dict[str, Any]

BLOCKED_PATHS = {
    "/twitter/{auth_token}/cookie",
    "/twitter/{auth_token}/user_info",
    "/twitter/action",
    "/twitter/action/order-status",
    "/twitter/profile",
    "/twitter/list/create",
    "/twitter/post-tweet-without-cookie",
    "/twitter/tweets/sentiment",
}

WRITE_METHODS = {"DELETE", "PATCH", "PUT"}
WRITE_PATH_PATTERNS = (
    re.compile(r"^/twitter/tweets/create$"),
    re.compile(r"^/twitter/tweets/quote$"),
    re.compile(r"^/twitter/tweets/delete-batch$"),
    re.compile(r"^/twitter/tweets/[^/]+/(?:like|retweet|bookmark)$"),
    re.compile(r"^/twitter/user/(?:follow|block)$"),
    re.compile(r"^/twitter/send-dm$"),
    re.compile(r"^/x/articles(?:/.*)?$"),
)
PRIVATE_PATH_PATTERNS = (
    re.compile(r"^/balance$"),
    re.compile(r"^/v2/dm/status$"),
    re.compile(r"^/twitter/dm-history$"),
    re.compile(r"^/twitter/notifications$"),
)
PAID_CATEGORY_PATTERNS = (
    re.compile(r"search", re.IGNORECASE),
    re.compile(r"followers", re.IGNORECASE),
    re.compile(r"following", re.IGNORECASE),
    re.compile(r"replies", re.IGNORECASE),
    re.compile(r"engagement", re.IGNORECASE),
    re.compile(r"timeline", re.IGNORECASE),
    re.compile(r"lists", re.IGNORECASE),
    re.compile(r"communities", re.IGNORECASE),
    re.compile(r"tweets", re.IGNORECASE),
    re.compile(r"article", re.IGNORECASE),
)
READ_PATH_PATTERNS = (
    re.compile(r"^/twitter/global-trending/(?:countries|topics|contents)$"),
    re.compile(r"^/twitter/[^/]+/trending$"),
    re.compile(r"^/twitter/[^/]+/about$"),
    re.compile(r"^/twitter/community/[^/]+$"),
    re.compile(r"^/twitter/community/search$"),
    re.compile(r"^/twitter/list/search$"),
    re.compile(r"^/twitter/tweets/[^/]+/similar$"),
    re.compile(r"^/x/account/verify$"),
    re.compile(r"^/twitter/account/based$"),
    re.compile(r"^/x/article/[^/]+/markdown$"),
    re.compile(r"^/twitter/(?:followers|following)/task/[^/]+/status$"),
)


def _as_dict(value: object) -> JsonDict:
    return cast("JsonDict", value) if isinstance(value, dict) else {}


def _as_list(value: object) -> list[object]:
    return cast("list[object]", value) if isinstance(value, list) else []


def _api_path(path: str) -> str:
    parsed = urlsplit(path.strip())
    normalized = parsed.path if parsed.scheme else path.strip()
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"
    return normalized.removesuffix("/") or "/"


def _slug(value: object) -> str:
    text = str(value or "Other")
    text = re.sub(r"\s*Endpoints\s*$", "", text, flags=re.IGNORECASE)
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "other"


def _category(tags: object) -> str:
    values = _as_list(tags)
    return _slug(values[0]) if values else "uncategorized"


def _schema_type(schema: JsonDict) -> str:
    value = schema.get("type")
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        values = cast("list[object]", value)
        return "|".join(str(item) for item in values)
    if isinstance(schema.get("$ref"), str):
        return str(schema["$ref"]).rsplit("/", maxsplit=1)[-1]
    if "properties" in schema:
        return "object"
    if "schema" in schema:
        return _schema_type(_as_dict(schema["schema"]))
    return "unknown"


def _resolve_parameter_ref(parameter: JsonDict, parameter_components: JsonDict) -> JsonDict:
    ref = parameter.get("$ref")
    if not isinstance(ref, str) or not ref.startswith("#/components/parameters/"):
        return parameter
    name = ref.removeprefix("#/components/parameters/")
    return _as_dict(parameter_components.get(name))


def _body_schema(request_body: JsonDict) -> JsonDict:
    content = _as_dict(request_body.get("content"))
    for content_type in ("application/json", "multipart/form-data"):
        schema = _as_dict(_as_dict(content.get(content_type)).get("schema"))
        if schema:
            return schema
    return {}


def _parameters(
    path_item: JsonDict,
    operation: JsonDict,
    parameter_components: JsonDict,
) -> list[JsonDict]:
    merged: list[JsonDict] = []
    for source in (path_item.get("parameters"), operation.get("parameters")):
        merged.extend(
            _resolve_parameter_ref(_as_dict(item), parameter_components)
            for item in _as_list(source)
        )

    output: list[JsonDict] = []
    for parameter in merged:
        name = str(parameter.get("name", "")).strip()
        if not name:
            continue
        schema = _as_dict(parameter.get("schema"))
        output.append(
            {
                "name": name,
                "in": str(parameter.get("in", "query")),
                "required": bool(parameter.get("required", False)),
                "type": _schema_type(schema),
                "description": str(parameter.get("description", "")).strip(),
            }
        )

    request_body = _as_dict(operation.get("requestBody"))
    schema = _body_schema(request_body)
    properties = _as_dict(schema.get("properties"))
    required_names = {str(item) for item in _as_list(schema.get("required"))}
    if properties:
        for name, property_schema in properties.items():
            property_data = _as_dict(property_schema)
            output.append(
                {
                    "name": str(name),
                    "in": "body",
                    "required": str(name) in required_names,
                    "type": _schema_type(property_data),
                    "description": str(property_data.get("description", "")).strip(),
                }
            )
    elif request_body:
        output.append(
            {
                "name": "body",
                "in": "body",
                "required": bool(request_body.get("required", False)),
                "type": _schema_type(schema) if schema else "object",
                "description": (
                    str(request_body.get("description", "JSON request body")).strip()
                    or "JSON request body"
                ),
            }
        )

    return output


def _response_shape(operation: JsonDict) -> str | None:
    responses = _as_dict(operation.get("responses"))
    for status in ("200", "201", "202", "default"):
        response = _as_dict(responses.get(status))
        if not response:
            continue
        schema = _body_schema(response)
        if isinstance(schema.get("$ref"), str):
            return f"{{ {str(schema['$ref']).rsplit('/', maxsplit=1)[-1]} }}"
        if schema:
            return f"{{ {_schema_type(schema)} }}"
        description = str(response.get("description", "")).strip()
        return description[:240] if description else None
    return None


def _is_write(method: str, path: str) -> bool:
    return method in WRITE_METHODS or any(pattern.search(path) for pattern in WRITE_PATH_PATTERNS)


def _is_private(path: str) -> bool:
    return any(pattern.search(path) for pattern in PRIVATE_PATH_PATTERNS)


def _is_read(path: str) -> bool:
    return any(pattern.search(path) for pattern in READ_PATH_PATTERNS)


def _risk(method: str, path: str, category: str) -> str:
    if _is_write(method, path):
        return "write"
    if _is_private(path):
        return "private-read"
    if _is_read(path):
        return "read"
    if any(pattern.search(category) for pattern in PAID_CATEGORY_PATTERNS):
        return "paid-bulk"
    return "read"


def _cost(risk: str, path: str) -> str | None:
    if risk == "write":
        return "$0.0025 per call"
    if risk == "paid-bulk" and re.search(r"followers|following", path, re.IGNORECASE):
        return "$0.14 per 1,000 users"
    if risk == "paid-bulk" and re.search(r"replies", path, re.IGNORECASE):
        return "$0.14 per 1,000 replies"
    if risk == "paid-bulk" and re.search(r"search|tweets", path, re.IGNORECASE):
        return "$0.14 per 1,000 tweets"
    return None


def _compact(endpoint: JsonDict) -> JsonDict:
    return {
        key: value
        for key, value in endpoint.items()
        if value is not None and value is not False and value not in ([], "")
    }


def build(source: Path) -> list[JsonDict]:
    spec = _as_dict(cast("object", yaml.safe_load(source.read_text(encoding="utf-8"))))
    paths = _as_dict(spec.get("paths"))
    components = _as_dict(spec.get("components"))
    parameter_components = _as_dict(components.get("parameters"))
    output: list[JsonDict] = []

    for raw_path, path_item in sorted(paths.items()):
        path_item_dict = _as_dict(path_item)
        if not path_item_dict:
            continue

        for raw_method, operation in sorted(path_item_dict.items()):
            method_name = str(raw_method)
            operation_dict = _as_dict(operation)
            if method_name.lower() not in METHODS or not operation_dict:
                continue

            method = method_name.upper()
            path = _api_path(str(raw_path))
            if path in BLOCKED_PATHS:
                continue

            category = _category(operation_dict.get("tags"))
            risk = _risk(method, path, category)
            cost = _cost(risk, path)
            output.append(
                _compact(
                    {
                        "action": risk != "read",
                        "category": category,
                        "cost": cost,
                        "free": risk == "read",
                        "method": method,
                        "parameters": _parameters(
                            path_item_dict,
                            operation_dict,
                            parameter_components,
                        ),
                        "path": path,
                        "responseShape": _response_shape(operation_dict),
                        "risk": risk,
                        "sensitive": risk in {"private-read", "write"},
                        "summary": str(
                            operation_dict.get("summary")
                            or operation_dict.get("description")
                            or f"{method} {path}",
                        ).strip(),
                    }
                )
            )

    return output


def main() -> int:
    if len(sys.argv) != EXPECTED_ARG_COUNT:
        print("Usage: python scripts/build_catalog.py /path/to/openapi.yaml", file=sys.stderr)
        return 2
    source = Path(sys.argv[1]).resolve()
    data = build(source)
    OUTPUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(data)} endpoints to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
