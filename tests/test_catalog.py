from __future__ import annotations

from hermes_xapi.catalog import (
    Endpoint,
    explore,
    find_endpoint,
    matches_path,
    normalize_limit,
    normalize_method,
)


def test_matches_openapi_path_parameters() -> None:
    assert matches_path("/twitter/{screen_name}/about", "/twitter/elonmusk/about") is True
    assert (
        matches_path("/twitter/{screen_name}/about", "/twitter/elonmusk/about?expand=profile")
        is True
    )
    assert matches_path(" /twitter/{screen_name}/about ", " /twitter/elonmusk/about ") is True
    assert matches_path("/twitter/tweets/:tweet_id/similar", "/twitter/tweets/123/similar") is True
    assert (
        matches_path(
            "/twitter/tweets/:tweet_id/similar",
            "https://api.twexapi.io/twitter/tweets/123/similar#metrics",
        )
        is True
    )
    assert matches_path("/twitter/tweets/{tweet_id}/extra", "/twitter/tweets//extra") is False
    assert matches_path("/twitter/tweets/:tweet_id/extra", "/twitter/tweets//extra") is False
    assert matches_path("/twitter/tweets/{tweet_id}/similar", "/twitter/tweets/") is False
    assert (
        matches_path("/twitter/tweets/{tweet_id}/similar", "/twitter/tweets/123/similar/extra")
        is False
    )
    assert matches_path("/twitter/tweets/{tweet_id}/similar", "/twitter/users/123") is False
    assert matches_path("/twitter/tweets/{tweet_id}/similar", "/twitter/tweets") is False


def test_catalog_contains_twexapi_read_endpoint() -> None:
    endpoint = find_endpoint("GET", "/twitter/elonmusk/about")
    assert endpoint is not None
    assert endpoint.action is False
    assert endpoint.risk == "read"
    assert find_endpoint(" get ", " /twitter/elonmusk/about ") == endpoint
    assert find_endpoint("GET", "/twitter/elonmusk/about?q=ai") == endpoint
    assert find_endpoint("GET", "https://api.twexapi.io/twitter/elonmusk/about?q=ai") == endpoint
    assert find_endpoint("GET", "/twitter/missing") is None


def test_catalog_excludes_agent_prohibited_twexapi_endpoints() -> None:
    assert find_endpoint("GET", "/twitter/auth-token/cookie") is None
    assert find_endpoint("POST", "/twitter/action") is None
    assert find_endpoint("POST", "/twitter/post-tweet-without-cookie") is None


def test_catalog_prefers_highest_twexapi_endpoint_versions() -> None:
    followers = find_endpoint("POST", "/v3/twitter/users/followers")
    send_dm = find_endpoint("POST", "/v3/twitter/send-dm")
    dm_history = find_endpoint("POST", "/v3/twitter/dm-history")

    assert followers is not None
    assert followers.risk == "paid-bulk"
    assert send_dm is not None
    assert send_dm.risk == "write"
    assert dm_history is not None
    assert dm_history.risk == "private-read"
    assert find_endpoint("GET", "/twitter/followers/elonmusk/10") is None
    assert find_endpoint("POST", "/twitter/send-dm") is None
    assert find_endpoint("POST", "/twitter/dm-history") is None


def test_explore_hides_actions_by_default() -> None:
    results = explore({"query": "tweet", "limit": 100})
    assert results
    assert all(item["action"] is False for item in results)


def test_explore_parses_string_boolean_filters() -> None:
    hidden_actions = explore({"include_actions": "false", "query": "tweets/create", "limit": 100})
    visible_actions = explore({"include_actions": "true", "query": "tweets/create", "limit": 100})
    paid = explore({"free": "false", "include_actions": "true", "limit": 100})

    assert all(item["action"] is False for item in hidden_actions)
    assert any(item["action"] is True for item in visible_actions)
    assert paid
    assert all(item["free"] is False for item in paid)


def test_explore_ignores_unknown_boolean_filter_strings() -> None:
    unfiltered = explore({"category": "trending", "include_actions": True, "limit": 100})
    unknown_free = explore(
        {
            "category": "trending",
            "free": "maybe",
            "include_actions": True,
            "limit": 100,
        }
    )

    assert unknown_free == unfiltered


def test_explore_ignores_malformed_optional_text_filters() -> None:
    unfiltered = explore({"include_actions": True, "limit": 100})
    malformed = explore(
        {
            "category": 123,
            "include_actions": True,
            "limit": 100,
            "method": True,
            "path": False,
            "query": [],
        }
    )
    blank_method = explore({"include_actions": True, "limit": 100, "method": "  "})

    assert malformed == unfiltered
    assert blank_method == unfiltered


def test_explore_filters_catalog() -> None:
    results = explore(
        {
            "category": "tweet-replies",
            "free": False,
            "include_actions": True,
            "method": "GET",
            "path": "/twitter/tweets/123/replies/10",
            "query": "replies",
            "risk": "paid-bulk",
        }
    )

    assert results
    assert results[0]["path"] == "/twitter/tweets/{tweet_id}/replies/{count}"


def test_explore_filters_catalog_with_copied_url_path() -> None:
    results = explore(
        {
            "include_actions": True,
            "path": "https://api.twexapi.io/x/article/123/markdown?q=ignored#results",
        }
    )

    assert results
    assert results[0]["path"] == "/x/article/{tweet_id}/markdown"


def test_explore_filters_by_risk() -> None:
    private_reads = explore({"risk": "private-read", "include_actions": True, "limit": 100})
    reads = explore({"risk": "read", "include_actions": True, "limit": 100})

    assert private_reads
    assert reads
    assert all(item["risk"] == "private-read" for item in private_reads)
    assert all(item["risk"] == "read" for item in reads)


def test_normalizers() -> None:
    truthy_limit = True
    falsey_limit = False

    assert normalize_method(None) == "GET"
    assert normalize_method("post") == "POST"
    assert normalize_method(" post ") == "POST"
    assert normalize_method("") == "GET"
    assert normalize_method(123) == "GET"
    assert normalize_method(None, default="POST") == "POST"
    assert normalize_limit(None) == 25
    assert normalize_limit(truthy_limit) == 25
    assert normalize_limit(falsey_limit) == 25
    assert normalize_limit(0) == 1
    assert normalize_limit("0") == 1
    assert normalize_limit(" 7 ") == 7
    assert normalize_limit(101) == 100
    assert normalize_limit("101") == 100
    assert normalize_limit(7) == 7
    assert normalize_limit("seven") == 25


def test_endpoint_to_dict_includes_optional_fields() -> None:
    endpoint = Endpoint(
        action=True,
        category="tweet-actions",
        cost="$0.0025 per call",
        free=False,
        method="POST",
        parameters=({"name": "text", "in": "body", "required": True, "type": "string"},),
        path="/twitter/tweets/create",
        response_shape="{ PostTweetResponse }",
        risk="write",
        sensitive=True,
        summary="Create Tweet",
    )

    assert endpoint.to_dict() == {
        "action": True,
        "category": "tweet-actions",
        "cost": "$0.0025 per call",
        "free": False,
        "method": "POST",
        "parameters": [{"name": "text", "in": "body", "required": True, "type": "string"}],
        "path": "/twitter/tweets/create",
        "responseShape": "{ PostTweetResponse }",
        "risk": "write",
        "sensitive": True,
        "summary": "Create Tweet",
    }
