from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from . import schemas
from .tools import (
    action_enabled,
    call_action,
    call_read,
    check_api_available,
    explore,
    xstatus,
    xtrends,
)

logger = logging.getLogger(__name__)

TOOLSET = "hermes-xapi"


def _register_bundled_skills(ctx: Any) -> None:
    skills_dir = Path(__file__).parent / "skills"
    for child in sorted(skills_dir.iterdir()):
        skill_md = child / "SKILL.md"
        if child.is_dir() and skill_md.exists():
            ctx.register_skill(child.name, skill_md)


def register(ctx: Any) -> None:
    ctx.register_tool(
        name="xapi_explore",
        toolset=TOOLSET,
        schema=schemas.XAPI_EXPLORE,
        handler=explore,
        is_async=False,
        description="Search the bundled TwexAPI endpoint catalog.",
        emoji="🔎",
    )

    ctx.register_tool(
        name="xapi_read",
        toolset=TOOLSET,
        schema=schemas.XAPI_READ,
        handler=call_read,
        check_fn=check_api_available,
        requires_env=["TWEXAPI_KEY"],
        is_async=False,
        description="Call catalog-listed read-only TwexAPI endpoints.",
        emoji="📖",
    )

    ctx.register_tool(
        name="xapi_action",
        toolset=TOOLSET,
        schema=schemas.XAPI_ACTION,
        handler=call_action,
        check_fn=action_enabled,
        requires_env=["TWEXAPI_KEY", "HERMES_XAPI_ENABLE_ACTIONS"],
        is_async=False,
        description="Call write-like or private TwexAPI endpoints.",
        emoji="✍️",
    )

    ctx.register_command(
        "xstatus",
        handler=xstatus,
        description="Show TwexAPI account and usage status",
    )
    ctx.register_command("xtrends", handler=xtrends, description="Show current X trends")

    _register_bundled_skills(ctx)
    logger.info(
        "Hermes XAPI loaded with actions=%s",
        os.getenv("HERMES_XAPI_ENABLE_ACTIONS", "false"),
    )


__all__ = ["register"]
