---
name: hermes-xapi
description: Search Twitter/X, read public profiles and trends, fetch replies and followers, and gate X actions through TwexAPI.
version: 0.1.7
author: TwexAPI
license: MIT
tags:
  - hermes-agent
  - twexapi
  - twitter
  - x
  - social-media
  - automation
metadata:
  version: 0.1.7
  author: TwexAPI
  repository: https://github.com/twexapi-dev/hermes-xapi
  plugin: hermes plugins install twexapi-dev/hermes-xapi --enable
capabilities:
  shell:
    required: false
    justification: Optional Hermes CLI checks are used only for installation and registry diagnostics.
  network:
    required: true
    justification: Hermes XAPI tools call TwexAPI API routes for X/Twitter public reads and research.
  files:
    required: false
    justification: Normal use does not require local file reads or writes.
  environment:
    required: true
    variables:
      - TWEXAPI_KEY
      - HERMES_XAPI_ENABLE_ACTIONS
      - HERMES_ENABLE_PROJECT_PLUGINS
    justification: Runtime configuration controls authenticated reads, gated tools, and trusted project-local plugin loading.
  mcp:
    required: false
    justification: No MCP server access is required.
  tools:
    - xapi_explore
    - xapi_read
    - xapi_action
---

# Hermes XAPI

Use this ASK-compatible wrapper when a Hermes Agent user needs the native Hermes
XAPI plugin for X/Twitter research and public reads through TwexAPI.

## Install

Install the native plugin in Hermes Agent:

```bash
hermes plugins install twexapi-dev/hermes-xapi --enable
hermes tools list
```

Set `TWEXAPI_KEY` in the Hermes runtime environment before using authenticated
read tools. Do not paste the key into chat.

## When to Use

Use Hermes XAPI for:

- scrape/search tweets or search Twitter/X
- read tweet replies and tweet details
- look up users and public profiles
- track trends, public profiles, and community/list context
- export followers and following lists
- research briefs built from public X signal

## Tool Flow

1. Use `xapi_explore` to find the catalog endpoint.
2. Use `xapi_read` for public read-only endpoints.
3. Keep `xapi_action` gated behind `HERMES_XAPI_ENABLE_ACTIONS=true`. Prefer
   public reads for research and monitoring.

## Safety

- Never ask for API keys, passwords, or TOTP secrets.
- Never pass credentials in tool arguments.
- Use only catalog-listed TwexAPI endpoints.
- Copied endpoint URLs are accepted only when they resolve to catalog-listed paths.
- Keep write-capable tools gated behind `HERMES_XAPI_ENABLE_ACTIONS=true`.
- Do not instruct agents to post, send DMs, or mutate accounts as the default
  workflow.

## Permissions and Trust

- Tool scope: use only `xapi_explore`, `xapi_read`, and `xapi_action` through
  the enabled Hermes XAPI toolset.
- Network scope: call only catalog-listed TwexAPI API routes through those tools.
  Do not create direct HTTP fallbacks.
- File scope: do not write files, logs, screenshots, cached payloads, or
  credentials unless the user asks for an explicit export workflow.
- Environment scope: check only whether `TWEXAPI_KEY`,
  `HERMES_XAPI_ENABLE_ACTIONS`, and `HERMES_ENABLE_PROJECT_PLUGINS` are
  configured. Never request or echo values.
- Output: return concise Markdown summaries or JSON-like tool payloads for
  public reads. Keep gated tools disabled for normal research sessions.
- Release gate: do not present this skill as NVIDIA-verified unless the release
  includes a clean SkillSpector review, `skill-card.md`, Tier-3 eval data,
  `BENCHMARK.md`, `skill.oms.sig`, and signature verification instructions.
