from __future__ import annotations

import importlib.util
import inspect
import re
import sys
import types
from pathlib import Path
from typing import Any

from hermes_xapi import register
from hermes_xapi.tools import action_enabled, check_api_available


class DummyContext:
    def __init__(self) -> None:
        self.tools: list[dict[str, Any]] = []
        self.commands: list[dict[str, Any]] = []
        self.skills: list[tuple[str, Path]] = []

    def register_tool(self, **kwargs: Any) -> None:
        self.tools.append(kwargs)

    def register_command(self, name: str, **kwargs: Any) -> None:
        self.commands.append({"name": name, **kwargs})

    def register_skill(self, name: str, skill_md: Path) -> None:
        self.skills.append((name, skill_md))


def test_register_wires_tools_commands_and_skill() -> None:
    ctx = DummyContext()

    register(ctx)

    assert [tool["name"] for tool in ctx.tools] == [
        "xapi_explore",
        "xapi_read",
        "xapi_action",
    ]
    assert [command["name"] for command in ctx.commands] == ["xstatus", "xtrends"]
    assert ctx.skills == [
        (
            "hermes-xapi",
            Path(__file__).parents[1] / "hermes_xapi" / "skills" / "hermes-xapi" / "SKILL.md",
        )
    ]


def test_register_keeps_official_hermes_plugin_gates_aligned() -> None:
    ctx = DummyContext()

    register(ctx)

    tools = {tool["name"]: tool for tool in ctx.tools}
    explore = tools["xapi_explore"]
    read = tools["xapi_read"]
    action = tools["xapi_action"]
    nonblank_property_names = {"minLength": 1, "pattern": "\\S"}

    assert "check_fn" not in explore
    assert "requires_env" not in explore
    assert explore["schema"]["name"] == "xapi_explore"
    assert explore["is_async"] is False
    explore_parameters = explore["schema"]["parameters"]
    for filter_name in ("query", "category", "path"):
        assert explore_parameters["properties"][filter_name]["minLength"] == 1
        assert explore_parameters["properties"][filter_name]["pattern"] == "\\S"

    assert read["check_fn"] is check_api_available
    assert read["requires_env"] == ["TWEXAPI_KEY"]
    assert read["schema"]["name"] == "xapi_read"
    assert read["is_async"] is False
    read_parameters = read["schema"]["parameters"]
    assert read_parameters["properties"]["path"]["minLength"] == len("/balance")
    assert read_parameters["properties"]["path"]["pattern"] == (
        "^(?:/(?:twitter|x|v2|dm)/|/balance$|https?://[^/]+/(?:twitter|x|v2|dm)/|https?://[^/]+/balance$)"
    )
    assert "copied API URL" in read_parameters["properties"]["path"]["description"]
    assert read_parameters["properties"]["query"]["propertyNames"] == nonblank_property_names

    assert action["check_fn"] is action_enabled
    assert action["requires_env"] == ["TWEXAPI_KEY", "HERMES_XAPI_ENABLE_ACTIONS"]
    assert action["schema"]["name"] == "xapi_action"
    assert action["is_async"] is False
    action_parameters = action["schema"]["parameters"]
    assert action_parameters["required"] == ["path", "reason"]
    assert action_parameters["properties"]["path"]["minLength"] == len("/balance")
    assert action_parameters["properties"]["path"]["pattern"] == (
        "^(?:/(?:twitter|x|v2|dm)/|/balance$|https?://[^/]+/(?:twitter|x|v2|dm)/|https?://[^/]+/balance$)"
    )
    assert "copied API URL" in action_parameters["properties"]["path"]["description"]
    assert action_parameters["properties"]["query"]["propertyNames"] == nonblank_property_names
    assert action_parameters["properties"]["method"]["default"] == "POST"
    assert action_parameters["properties"]["reason"]["minLength"] == 1
    assert action_parameters["properties"]["reason"]["pattern"] == "\\S"


def test_registered_path_schema_allows_only_api_paths_and_urls() -> None:
    ctx = DummyContext()

    register(ctx)

    tools = {tool["name"]: tool for tool in ctx.tools}
    for tool_name in ("xapi_read", "xapi_action"):
        path_schema = tools[tool_name]["schema"]["parameters"]["properties"]["path"]
        pattern = re.compile(path_schema["pattern"])

        assert pattern.search("/twitter/elonmusk/about") is not None
        assert pattern.search("/x/article/123/markdown") is not None
        assert pattern.search("/v2/dm/status") is not None
        assert pattern.search("/balance") is not None
        assert pattern.search("https://api.twexapi.io/twitter/elonmusk/about") is not None
        assert pattern.search("https://api.twexapi.io/balance") is not None
        assert pattern.search("https://api.twexapi.io/legacy/account") is None
        assert pattern.search("https://api.twexapi.io/not-api/account") is None
        assert pattern.search("/not-api/account") is None


def test_registered_tool_handlers_accept_future_hermes_context_kwargs() -> None:
    ctx = DummyContext()

    register(ctx)

    for tool in ctx.tools:
        parameters = inspect.signature(tool["handler"]).parameters.values()
        assert any(parameter.kind is inspect.Parameter.VAR_KEYWORD for parameter in parameters)


def test_root_entrypoint_loads_as_hermes_directory_plugin() -> None:
    repo_root = Path(__file__).parents[1]
    previous_path = sys.path.copy()
    previous_hermes_xapi = sys.modules.pop("hermes_xapi", None)
    module_prefix = "hermes_plugins.hermes_xapi_probe"

    try:
        sys.path = [path for path in sys.path if Path(path or ".").resolve() != repo_root]

        parent = types.ModuleType("hermes_plugins")
        parent.__path__ = []
        parent.__package__ = "hermes_plugins"
        sys.modules["hermes_plugins"] = parent

        spec = importlib.util.spec_from_file_location(
            module_prefix,
            repo_root / "__init__.py",
            submodule_search_locations=[str(repo_root)],
        )
        assert spec is not None
        assert spec.loader is not None

        module = importlib.util.module_from_spec(spec)
        module.__package__ = module_prefix
        module.__path__ = [str(repo_root)]
        sys.modules[module_prefix] = module
        spec.loader.exec_module(module)

        assert callable(module.register)
    finally:
        sys.path = previous_path
        for module_name in list(sys.modules):
            if module_name == module_prefix or module_name.startswith(f"{module_prefix}."):
                del sys.modules[module_name]
        if previous_hermes_xapi is not None:
            sys.modules["hermes_xapi"] = previous_hermes_xapi
