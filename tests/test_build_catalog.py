from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).parents[1]


def load_build_catalog_module() -> Any:
    module_path = ROOT / "scripts" / "build_catalog.py"
    spec = importlib.util.spec_from_file_location("build_catalog", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


build_catalog = load_build_catalog_module()


def write_openapi(tmp_path: Path, paths: dict[str, object]) -> Path:
    source = tmp_path / "openapi.yaml"
    source.write_text(yaml.safe_dump({"paths": paths}), encoding="utf-8")
    return source


def test_build_skips_twexapi_agent_prohibited_endpoints(tmp_path: Path) -> None:
    source = write_openapi(
        tmp_path,
        {
            "/twitter/{auth_token}/cookie": {"get": {"summary": "Get cookie"}},
            "/twitter/action": {"post": {"summary": "Purchase engagement"}},
            "/twitter/profile": {"post": {"summary": "Modify profile"}},
            "/twitter/{screen_name}/about": {
                "get": {"summary": "Get profile", "tags": ["Twitter User About"]}
            },
        },
    )

    endpoints = build_catalog.build(source)

    assert [endpoint["path"] for endpoint in endpoints] == ["/twitter/{screen_name}/about"]


def test_build_marks_twexapi_risk_and_action_flags(tmp_path: Path) -> None:
    source = write_openapi(
        tmp_path,
        {
            "/balance": {"get": {"summary": "Get Balance", "tags": ["Balance"]}},
            "/twitter/{screen_name}/about": {
                "get": {"summary": "Get profile", "tags": ["Twitter User About"]}
            },
            "/twitter/followers/{screen_name}/{count}": {
                "get": {"summary": "Get Followers", "tags": ["Followers & Following"]}
            },
            "/twitter/tweets/create": {
                "post": {"summary": "Create Tweet", "tags": ["Tweet Actions"]}
            },
        },
    )

    endpoints = build_catalog.build(source)
    by_path = {endpoint["path"]: endpoint for endpoint in endpoints}

    assert by_path["/balance"]["risk"] == "private-read"
    assert by_path["/balance"]["action"] is True
    assert by_path["/balance"]["sensitive"] is True
    assert by_path["/twitter/{screen_name}/about"]["risk"] == "read"
    assert by_path["/twitter/{screen_name}/about"]["free"] is True
    assert "action" not in by_path["/twitter/{screen_name}/about"]
    assert by_path["/twitter/followers/{screen_name}/{count}"]["risk"] == "paid-bulk"
    assert by_path["/twitter/followers/{screen_name}/{count}"]["cost"] == ("$0.14 per 1,000 users")
    assert by_path["/twitter/tweets/create"]["risk"] == "write"
    assert by_path["/twitter/tweets/create"]["cost"] == "$0.0025 per call"


def test_build_extracts_parameters_body_properties_and_response_shape(
    tmp_path: Path,
) -> None:
    source = write_openapi(
        tmp_path,
        {
            "/twitter/tweets/create": {
                "parameters": [
                    {
                        "name": "dry_run",
                        "in": "query",
                        "schema": {"type": "boolean"},
                    }
                ],
                "post": {
                    "summary": "Create Tweet",
                    "tags": ["Tweet Actions"],
                    "parameters": [
                        {
                            "name": "account",
                            "in": "query",
                            "required": True,
                            "description": "Account handle",
                            "schema": {"type": "string"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["text"],
                                    "properties": {
                                        "text": {
                                            "type": "string",
                                            "description": "Tweet text",
                                        }
                                    },
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PostTweetResponse"}
                                }
                            }
                        }
                    },
                },
            }
        },
    )

    [endpoint] = build_catalog.build(source)

    assert endpoint == {
        "action": True,
        "category": "tweet-actions",
        "cost": "$0.0025 per call",
        "method": "POST",
        "parameters": [
            {
                "name": "dry_run",
                "in": "query",
                "required": False,
                "type": "boolean",
                "description": "",
            },
            {
                "name": "account",
                "in": "query",
                "required": True,
                "type": "string",
                "description": "Account handle",
            },
            {
                "name": "text",
                "in": "body",
                "required": True,
                "type": "string",
                "description": "Tweet text",
            },
        ],
        "path": "/twitter/tweets/create",
        "responseShape": "{ PostTweetResponse }",
        "risk": "write",
        "sensitive": True,
        "summary": "Create Tweet",
    }


def test_build_resolves_referenced_parameters_and_skips_unnamed_entries(
    tmp_path: Path,
) -> None:
    source = tmp_path / "openapi.yaml"
    source.write_text(
        yaml.safe_dump(
            {
                "components": {
                    "parameters": {
                        "Cursor": {
                            "name": "cursor",
                            "in": "query",
                            "description": "Pagination cursor",
                            "schema": {"type": "string"},
                        }
                    }
                },
                "paths": {
                    "/twitter/global-trending/tweets": {
                        "get": {
                            "summary": "Get Global Trending Tweets",
                            "tags": ["Trending"],
                            "parameters": [
                                {"$ref": "#/components/parameters/Cursor"},
                                {"$ref": "#/components/parameters/Missing"},
                                {},
                            ],
                        }
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    [endpoint] = build_catalog.build(source)

    assert endpoint["parameters"] == [
        {
            "name": "cursor",
            "in": "query",
            "required": False,
            "type": "string",
            "description": "Pagination cursor",
        }
    ]


def test_build_defaults_empty_metadata(tmp_path: Path) -> None:
    source = write_openapi(
        tmp_path,
        {
            "twitter/worldwide/trending": {
                "get": {
                    "description": "Trend lookup",
                    "parameters": [{"name": "limit", "schema": {"schema": {"type": "integer"}}}],
                }
            }
        },
    )

    [endpoint] = build_catalog.build(source)

    assert endpoint["category"] == "uncategorized"
    assert endpoint["free"] is True
    assert endpoint["method"] == "GET"
    assert endpoint["parameters"] == [
        {
            "name": "limit",
            "in": "query",
            "required": False,
            "type": "integer",
            "description": "",
        }
    ]
    assert endpoint["path"] == "/twitter/worldwide/trending"
    assert endpoint["risk"] == "read"
    assert endpoint["summary"] == "Trend lookup"
