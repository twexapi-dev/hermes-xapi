from __future__ import annotations

import json
from typing import TYPE_CHECKING

from hermes_xapi import tools
from hermes_xapi.tools import call_action, call_read, explore

if TYPE_CHECKING:
    import pytest


def test_read_rejects_action_endpoint() -> None:
    result = json.loads(call_read({"path": "/twitter/tweets/123/replies/10"}))
    assert result["success"] is False
    assert "xapi_action" in result["error"]


def test_action_is_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HERMES_XAPI_ENABLE_ACTIONS", raising=False)
    expected = {"success": False, "error": tools.ACTION_DISABLED_ERROR}

    assert (
        json.loads(
            call_action(
                {
                    "path": "/twitter/tweets/create",
                    "method": "POST",
                    "body": {"text": "hello"},
                    "reason": "test",
                }
            )
        )
        == expected
    )
    assert json.loads(call_action({"path": "/twitter/missing", "reason": "test"})) == expected


def test_explore_returns_json_string() -> None:
    result = json.loads(explore({"query": "trending"}))
    assert result["success"] is True
    assert result["endpoints"]


def test_explore_returns_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(_args: dict[str, object]) -> list[dict[str, object]]:
        raise ValueError("broken")

    monkeypatch.setattr(tools, "explore_catalog", fail)

    assert json.loads(explore({})) == {"success": False, "error": "broken"}


def test_handlers_reject_non_object_arguments() -> None:
    error = {"success": False, "error": "Tool arguments must be a JSON object."}

    assert json.loads(explore([])) == error
    assert json.loads(call_read(None)) == error
    assert json.loads(call_action("bad")) == error


def test_read_missing_endpoint() -> None:
    result = json.loads(call_read({"path": "/twitter/missing"}))
    assert result == {
        "success": False,
        "error": "Endpoint is not in the Hermes XAPI catalog: GET /twitter/missing",
    }


def test_read_success(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_request(
        method: str,
        path: str,
        query: dict[str, str] | None = None,
        body: object | None = None,
    ) -> dict[str, object]:
        return {"method": method, "path": path, "query": query, "body": body}

    monkeypatch.setattr(tools, "request", fake_request)

    result = json.loads(
        call_read(
            {
                "path": "/twitter/elonmusk/about",
                "query": {
                    1: "ignored",
                    "  ": "ignored",
                    "bad": [],
                    "bad_inf": float("inf"),
                    "bad_nan": float("nan"),
                    "include": True,
                    "limit": 2,
                    " q ": "ai",
                    "ratio": 1.5,
                    "verified": False,
                },
            }
        )
    )

    assert result == {
        "body": None,
        "method": "GET",
        "path": "/twitter/elonmusk/about",
        "query": {
            "include": "true",
            "limit": "2",
            "q": "ai",
            "ratio": "1.5",
            "verified": "false",
        },
    }


def test_read_normalizes_path_values(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_request(
        method: str,
        path: str,
        query: dict[str, str] | None = None,
        body: object | None = None,
    ) -> dict[str, object]:
        return {"method": method, "path": path, "query": query, "body": body}

    monkeypatch.setattr(tools, "request", fake_request)

    assert json.loads(call_read({"path": " /twitter/elonmusk/about "})) == {
        "body": None,
        "method": "GET",
        "path": "/twitter/elonmusk/about",
        "query": None,
    }
    assert json.loads(call_read({"path": None})) == {
        "success": False,
        "error": "Endpoint is not in the Hermes XAPI catalog: GET ",
    }


def test_read_normalizes_copied_endpoint_url_before_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_request(
        method: str,
        path: str,
        query: dict[str, str] | None = None,
        body: object | None = None,
    ) -> dict[str, object]:
        return {"method": method, "path": path, "query": query, "body": body}

    monkeypatch.setattr(tools, "request", fake_request)

    assert json.loads(call_read({"path": "https://api.twexapi.io/twitter/elonmusk/about"})) == {
        "body": None,
        "method": "GET",
        "path": "/twitter/elonmusk/about",
        "query": None,
    }


def test_read_rejects_query_or_fragment_in_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tools, "request", None)

    expected = {
        "success": False,
        "error": "Pass query parameters through the query object, not in path.",
    }
    assert (
        json.loads(
            call_read({"path": "https://api.twexapi.io/twitter/elonmusk/about?ignored=true"})
        )
        == expected
    )
    assert json.loads(call_read({"path": "/twitter/elonmusk/about#section"})) == expected


def test_read_rejects_non_catalog_copied_url_before_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(tools, "request", None)

    assert json.loads(call_read({"path": "https://api.twexapi.io/not-api/account"})) == {
        "success": False,
        "error": (
            "Endpoint is not in the Hermes XAPI catalog: GET https://api.twexapi.io/not-api/account"
        ),
    }


def test_read_success_without_query_dict(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_request(
        method: str,
        path: str,
        query: dict[str, str] | None = None,
        body: object | None = None,
    ) -> dict[str, object]:
        return {"method": method, "path": path, "query": query, "body": body}

    monkeypatch.setattr(tools, "request", fake_request)

    assert json.loads(call_read({"path": "/twitter/elonmusk/about", "query": []})) == {
        "body": None,
        "method": "GET",
        "path": "/twitter/elonmusk/about",
        "query": None,
    }


def test_read_ignores_empty_query_after_normalization(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_request(
        method: str,
        path: str,
        query: dict[str, str] | None = None,
        body: object | None = None,
    ) -> dict[str, object]:
        return {"method": method, "path": path, "query": query, "body": body}

    monkeypatch.setattr(tools, "request", fake_request)

    assert json.loads(
        call_read(
            {
                "path": "/twitter/elonmusk/about",
                "query": {
                    1: "ignored",
                    "  ": "ignored",
                    "bad": [],
                    "bad_inf": float("inf"),
                    "bad_nan": float("nan"),
                },
            }
        )
    ) == {
        "body": None,
        "method": "GET",
        "path": "/twitter/elonmusk/about",
        "query": None,
    }


def test_read_returns_handler_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(_method: str, _path: str) -> object:
        raise ValueError("catalog failed")

    monkeypatch.setattr(tools, "find_endpoint", fail)

    assert json.loads(call_read({"path": "/twitter/elonmusk/about"})) == {
        "success": False,
        "error": "catalog failed",
    }


def test_action_missing_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tools, "action_enabled", lambda: True)

    result = json.loads(
        call_action(
            {
                "method": "POST",
                "path": "/twitter/missing",
                "reason": "test",
            }
        )
    )

    assert result == {
        "success": False,
        "error": "Endpoint is not in the Hermes XAPI catalog: POST /twitter/missing",
    }


def test_action_rejects_query_or_fragment_in_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tools, "action_enabled", lambda: True)
    monkeypatch.setattr(tools, "request", None)

    expected = {
        "success": False,
        "error": "Pass query parameters through the query object, not in path.",
    }
    assert (
        json.loads(
            call_action(
                {
                    "method": "POST",
                    "path": "https://api.twexapi.io/twitter/tweets/create?debug=true",
                    "reason": "test",
                }
            )
        )
        == expected
    )
    assert (
        json.loads(
            call_action(
                {
                    "method": "POST",
                    "path": "/twitter/tweets/create#section",
                    "reason": "test",
                }
            )
        )
        == expected
    )


def test_action_blocks_prohibited_twexapi_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tools, "action_enabled", lambda: True)
    monkeypatch.setattr(tools, "request", None)

    result = json.loads(
        call_action(
            {
                "method": "POST",
                "path": "/twitter/action",
                "body": {"quantity": 100},
                "reason": "prohibited route",
            }
        )
    )

    assert result == {
        "success": False,
        "error": tools.BLOCKED_ACTION_ERROR,
    }


def test_action_requires_reason_when_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tools, "action_enabled", lambda: True)

    error = {"success": False, "error": "Action reason is required."}

    assert json.loads(call_action({"path": "/twitter/tweets/create", "method": "POST"})) == error
    assert (
        json.loads(
            call_action({"path": "/twitter/tweets/create", "method": "POST", "reason": "  "})
        )
        == error
    )
    assert (
        json.loads(
            call_action({"path": "/twitter/tweets/create", "method": "POST", "reason": None})
        )
        == error
    )


def test_action_success(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_request(
        method: str,
        path: str,
        query: dict[str, str] | None = None,
        body: object | None = None,
    ) -> dict[str, object]:
        return {"method": method, "path": path, "query": query, "body": body}

    monkeypatch.setattr(tools, "action_enabled", lambda: True)
    monkeypatch.setattr(tools, "request", fake_request)

    result = json.loads(
        call_action(
            {
                "body": {"text": "hello"},
                "method": "POST",
                "path": "/twitter/tweets/create",
                "query": {"dry": True, "preview": False},
                "reason": "test",
            }
        )
    )

    assert result == {
        "body": {"text": "hello"},
        "method": "POST",
        "path": "/twitter/tweets/create",
        "query": {"dry": "true", "preview": "false"},
    }


def test_action_defaults_missing_or_malformed_method_to_post(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_request(
        method: str,
        path: str,
        query: dict[str, str] | None = None,
        body: object | None = None,
    ) -> dict[str, object]:
        return {"method": method, "path": path, "query": query, "body": body}

    monkeypatch.setattr(tools, "action_enabled", lambda: True)
    monkeypatch.setattr(tools, "request", fake_request)

    assert json.loads(
        call_action(
            {
                "body": {"text": "hello"},
                "path": "/twitter/tweets/create",
                "reason": "test",
            }
        )
    ) == {
        "body": {"text": "hello"},
        "method": "POST",
        "path": "/twitter/tweets/create",
        "query": None,
    }

    result = json.loads(
        call_action(
            {
                "body": {"text": "hello"},
                "method": None,
                "path": "/twitter/tweets/create",
                "reason": "test",
            }
        )
    )

    assert result == {
        "body": {"text": "hello"},
        "method": "POST",
        "path": "/twitter/tweets/create",
        "query": None,
    }


def test_action_normalizes_path_values(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_request(
        method: str,
        path: str,
        query: dict[str, str] | None = None,
        body: object | None = None,
    ) -> dict[str, object]:
        return {"method": method, "path": path, "query": query, "body": body}

    monkeypatch.setattr(tools, "action_enabled", lambda: True)
    monkeypatch.setattr(tools, "request", fake_request)

    result = json.loads(
        call_action(
            {
                "body": {"text": "hello"},
                "method": "POST",
                "path": " /twitter/tweets/create ",
                "reason": "test",
            }
        )
    )

    assert result == {
        "body": {"text": "hello"},
        "method": "POST",
        "path": "/twitter/tweets/create",
        "query": None,
    }


def test_action_normalizes_copied_endpoint_url_before_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_request(
        method: str,
        path: str,
        query: dict[str, str] | None = None,
        body: object | None = None,
    ) -> dict[str, object]:
        return {"method": method, "path": path, "query": query, "body": body}

    monkeypatch.setattr(tools, "action_enabled", lambda: True)
    monkeypatch.setattr(tools, "request", fake_request)

    assert json.loads(
        call_action(
            {
                "body": {"text": "hello"},
                "method": "POST",
                "path": "https://api.twexapi.io/twitter/tweets/create",
                "reason": "test",
            }
        )
    ) == {
        "body": {"text": "hello"},
        "method": "POST",
        "path": "/twitter/tweets/create",
        "query": None,
    }


def test_action_rejects_non_catalog_copied_url_before_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(tools, "action_enabled", lambda: True)
    monkeypatch.setattr(tools, "request", None)

    assert json.loads(
        call_action(
            {
                "method": "POST",
                "path": "https://api.twexapi.io/not-api/tweet",
                "reason": "test",
            }
        )
    ) == {
        "success": False,
        "error": (
            "Endpoint is not in the Hermes XAPI catalog: POST https://api.twexapi.io/not-api/tweet"
        ),
    }


def test_action_returns_handler_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail() -> bool:
        raise ValueError("env failed")

    monkeypatch.setattr(tools, "action_enabled", fail)

    assert json.loads(call_action({"path": "/twitter/tweets/create", "method": "POST"})) == {
        "success": False,
        "error": "env failed",
    }


def test_slash_commands(monkeypatch: pytest.MonkeyPatch) -> None:
    action_calls: list[dict[str, object]] = []
    read_calls: list[dict[str, object]] = []

    def fake_call_action(args: dict[str, object]) -> str:
        action_calls.append(args)
        return json.dumps({"ok": "action"})

    def fake_call_read(args: dict[str, object]) -> str:
        read_calls.append(args)
        return json.dumps({"ok": "read"})

    monkeypatch.setattr(tools, "call_action", fake_call_action)
    monkeypatch.setattr(tools, "call_read", fake_call_read)

    assert json.loads(tools.xstatus(None)) == {"ok": "action"}
    assert json.loads(tools.xtrends(" tech ")) == {"ok": "read"}
    assert json.loads(tools.xtrends(None)) == {"ok": "read"}
    assert action_calls == [
        {"method": "GET", "path": "/balance", "reason": "Check TwexAPI balance."}
    ]
    assert read_calls == [
        {"path": "/twitter/tech/trending"},
        {"path": "/twitter/worldwide/trending"},
    ]
