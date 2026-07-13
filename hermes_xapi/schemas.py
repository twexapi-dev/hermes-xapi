from __future__ import annotations

_METHOD_ENUM = ["GET", "POST", "PATCH", "PUT", "DELETE"]
_API_PATH_PATTERN = r"^(?:/(?:twitter|x|v2|dm)/|/balance$|https?://[^/]+/(?:twitter|x|v2|dm)/|https?://[^/]+/balance$)"
_API_PATH_DESCRIPTION = (
    "Concrete TwexAPI endpoint path or copied API URL for /twitter/..., /x/..., "
    "/v2/..., /dm/..., or /balance."
)

XAPI_EXPLORE = {
    "name": "xapi_explore",
    "description": (
        "Search the bundled TwexAPI endpoint catalog. Use this before calling "
        "xapi_read or xapi_action. This tool does not make network calls."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "minLength": 1,
                "pattern": "\\S",
                "description": (
                    "Keyword search across endpoint paths, summaries, parameters, "
                    "and response shapes."
                ),
            },
            "category": {
                "type": "string",
                "minLength": 1,
                "pattern": "\\S",
                "description": "Endpoint category filter.",
            },
            "method": {
                "type": "string",
                "enum": _METHOD_ENUM,
                "description": "HTTP method filter.",
            },
            "path": {
                "type": "string",
                "minLength": 1,
                "pattern": "\\S",
                "description": "Exact or partial TwexAPI path filter.",
            },
            "free": {"type": "boolean", "description": "Filter no-approval read endpoints."},
            "risk": {
                "type": "string",
                "enum": ["read", "private-read", "paid-bulk", "write"],
                "description": "Filter endpoint risk classification.",
            },
            "include_actions": {
                "type": "boolean",
                "description": "Include write-like and private endpoints in catalog results.",
                "default": False,
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "default": 25,
                "description": "Maximum endpoint descriptors to return.",
            },
        },
        "additionalProperties": False,
    },
}

XAPI_READ = {
    "name": "xapi_read",
    "description": (
        "Invoke one catalog-listed no-approval TwexAPI read endpoint. Use concrete paths "
        "from xapi_explore. This tool rejects write-like and private endpoints."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "minLength": 8,
                "pattern": _API_PATH_PATTERN,
                "description": _API_PATH_DESCRIPTION,
            },
            "query": {
                "type": "object",
                "description": "Query parameters as string, number, or boolean values.",
                "propertyNames": {"minLength": 1, "pattern": "\\S"},
                "additionalProperties": {"type": ["string", "number", "boolean"]},
            },
        },
        "required": ["path"],
        "additionalProperties": False,
    },
}

XAPI_ACTION = {
    "name": "xapi_action",
    "description": (
        "Invoke one catalog-listed TwexAPI action endpoint, including writes and private reads. "
        "Disabled unless HERMES_XAPI_ENABLE_ACTIONS=true. Show the endpoint and payload "
        "to the user first."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "minLength": 8,
                "pattern": _API_PATH_PATTERN,
                "description": _API_PATH_DESCRIPTION,
            },
            "method": {"type": "string", "enum": _METHOD_ENUM, "default": "POST"},
            "query": {
                "type": "object",
                "description": "Query parameters as string, number, or boolean values.",
                "propertyNames": {"minLength": 1, "pattern": "\\S"},
                "additionalProperties": {"type": ["string", "number", "boolean"]},
            },
            "body": {
                "description": "JSON request body.",
                "type": ["object", "array", "string", "number", "boolean", "null"],
            },
            "reason": {
                "type": "string",
                "minLength": 1,
                "pattern": "\\S",
                "description": "Brief user-visible reason for the action.",
            },
        },
        "required": ["path", "reason"],
        "additionalProperties": False,
    },
}
