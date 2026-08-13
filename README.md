# Hermes XAPI

> **TwexAPI is an independent third-party service.** Not affiliated with X Corp.
> "Twitter" and "X" are trademarks of X Corp.

[![CI](https://github.com/twexapi-dev/hermes-xapi/actions/workflows/ci.yml/badge.svg)](https://github.com/twexapi-dev/hermes-xapi/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-README-blue.svg)](https://github.com/twexapi-dev/hermes-xapi#readme)
[![Ask DeepWiki](https://deepwiki.com/badge.svg?url=https%3A%2F%2Fgithub.com%2Ftwexapi-dev%2Fhermes-xapi)](https://deepwiki.com/twexapi-dev/hermes-xapi)
[![Agentic Ready](https://nothumansearch.ai/badge/twexapi.io.svg)](https://nothumansearch.ai/site/twexapi.io)
[![PyPI](https://img.shields.io/pypi/v/hermes-xapi.svg)](https://pypi.org/project/hermes-xapi/)
[![Python](https://img.shields.io/pypi/pyversions/hermes-xapi.svg)](https://pypi.org/project/hermes-xapi/)
[![PyPI Status](https://img.shields.io/pypi/status/hermes-xapi.svg)](https://pypi.org/project/hermes-xapi/)
[![Wheel](https://img.shields.io/pypi/wheel/hermes-xapi.svg)](https://pypi.org/project/hermes-xapi/#files)
![skills.sh](https://skills.sh/b/twexapi-dev/hermes-xapi)
[![Apify Actor](https://apify.com/actor-badge?actor=fastcrawler/tweet-x-twitter-scraper-0-05-1k-pay-per-result-v2)](https://apify.com/fastcrawler/tweet-x-twitter-scraper-0-05-1k-pay-per-result-v2)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Native [Hermes Agent](https://github.com/NousResearch/hermes-agent) plugin for
X automation through [TwexAPI](https://twexapi.io).

Hermes XAPI brings X search, account reads, profile lookups, trends, followers,
replies, articles, DMs, tweet posting, likes, retweets, follows, and account
status checks into Hermes as structured tools.

Use it when you need a Hermes Agent Twitter plugin, Hermes X automation, social
media automation for agents, or a native Hermes toolset for X/Twitter.

## Highlights

- Published Python package with a native Hermes plugin entry point.
- Installable from PyPI as `hermes-xapi`.
- Discoverable as a public agent skill through `skills.sh` and `npx skills`.
- 87 agent-callable TwexAPI endpoints generated from TwexAPI OpenAPI docs.
- Risk-classified endpoint catalog with read, private-read, paid-bulk, and write
  routes.
- Read and action tools are split for least-privilege operation.
- Action endpoints are disabled by default.
- Bundled Hermes skill for agent-facing usage guidance.
- Slash commands for account status and trends.
- Current guidance for Hermes Agent v0.16.0 Desktop, remote gateway, and
  dashboard credential workflows.
- Strict CI with formatting, linting, type checking, tests, coverage, security
  scan, dependency audit, and package build checks.

## Install

Install the public Agent Skill first when you want `skills.sh` discovery and
install telemetry to count Hermes XAPI:

```bash
npx skills add twexapi-dev/hermes-xapi --skill hermes-xapi
```

Recommended Hermes plugin install:

```bash
hermes plugins install twexapi-dev/hermes-xapi --enable
```

Hermes Agent treats third-party plugins as opt-in. Without `--enable`, the
installer can discover Hermes XAPI, but it may leave the plugin in the
`not enabled` state until you run `hermes plugins enable hermes-xapi` or toggle
it in the interactive `hermes plugins` UI. Use `hermes plugins list` when a
fresh install does not show the `hermes-xapi` toolset.

The `npx skills add` command installs the reusable agent instructions from
[`skills/hermes-xapi/SKILL.md`](skills/hermes-xapi/SKILL.md). The
`hermes plugins install` command enables the Hermes plugin tools
(`xapi_explore`, `xapi_read`, and gated `xapi_action`). Use both commands when
you want Hermes runtime tools and `skills.sh` catalog visibility.

Verify the skills CLI can discover the repository before sharing a release:

```bash
npx skills add twexapi-dev/hermes-xapi --skill hermes-xapi --list
```

After real installs have been ingested by `skills.sh`, confirm catalog indexing
with:

```bash
npx skills find hermes-xapi --owner twexapi-dev
```

Hermes will prompt for `TWEXAPI_KEY` during an interactive install and save it
to `~/.hermes/.env`. In non-interactive installs the prompt is skipped; set the
key through the environment or `~/.hermes/.env` before running `xapi_read`.
If you edit `~/.hermes/.env` while Hermes is already running, use `/reload` in
an interactive CLI session, or restart gateway and cron sessions before calling
`xapi_read`.
When `TWEXAPI_KEY` is not configured, Hermes should expose only the no-network
`xapi_explore` tool from this plugin. That is expected safe gating, not an
install failure.

Install the published Python package from PyPI into the Hermes Python
environment:

```bash
uv pip install --python ~/.hermes/hermes-agent/venv/bin/python hermes-xapi
hermes plugins enable hermes-xapi
```

If your Hermes venv includes `pip`, this path is also valid:

```bash
~/.hermes/hermes-agent/venv/bin/python -m pip install hermes-xapi
hermes plugins enable hermes-xapi
```

From a local checkout:

```bash
hermes plugins install file:///absolute/path/to/hermes-xapi --force --enable
```

If you are testing from a project-local `.hermes/plugins/` directory instead of
installing the plugin into `~/.hermes/plugins/` or through the PyPI entry point,
start Hermes with `HERMES_ENABLE_PROJECT_PLUGINS=true` only for trusted
repositories.

Hermes Agent v0.16.0 adds a native desktop app and remote gateway profiles.
For a remote gateway profile, install and enable Hermes XAPI on the remote
Hermes host because that is where plugin code executes and where
`TWEXAPI_KEY` must be available. The desktop app is the chat surface; it
should not receive or store the key unless it is also running the Hermes
runtime locally.

## Python Package

| Field | Value |
| --- | --- |
| PyPI | [`hermes-xapi`](https://pypi.org/project/hermes-xapi/) |
| Repository guide | [`github.com/twexapi-dev/hermes-xapi#readme`](https://github.com/twexapi-dev/hermes-xapi#readme) |
| skills.sh install | `npx skills add twexapi-dev/hermes-xapi --skill hermes-xapi` |
| Context7 | [`context7.com/twexapi-dev/hermes-xapi`](https://context7.com/twexapi-dev/hermes-xapi) |
| piwheels | [`hermes-xapi`](https://piwheels.org/project/hermes-xapi/) |
| Latest release | [`v0.1.7`](https://github.com/twexapi-dev/hermes-xapi/releases/tag/v0.1.7) |
| Supported Python | `>=3.11` |
| Package format | Wheel and source distribution |
| Hermes entry point | `hermes-xapi = hermes_xapi` |
| Entry point group | `hermes_agent.plugins` |
| Included assets | `plugin.yaml`, `catalog_data.json`, bundled Hermes skill, Codex/Claude manifests |
| Claude plugin manifest | [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) |
| Codex plugin manifest | [`.codex-plugin/plugin.json`](.codex-plugin/plugin.json) |
| Registry skill path | [`skills/hermes-xapi/SKILL.md`](skills/hermes-xapi/SKILL.md) |
| Context7 guide | [`docs/CONTEXT7.md`](docs/CONTEXT7.md) |
| Hermes surface guide | [`docs/HERMES_SURFACES.md`](docs/HERMES_SURFACES.md) |
| Integration patterns | [`docs/INTEGRATION_PATTERNS.md`](docs/INTEGRATION_PATTERNS.md) |
| Submission readiness | [`docs/SUBMISSION_READINESS.md`](docs/SUBMISSION_READINESS.md) |
| Merge enablement | [`docs/MERGE_ENABLEMENT.md`](docs/MERGE_ENABLEMENT.md) |

Hermes XAPI also ships source-native `.codex-plugin` metadata, a root
security policy, a local composer icon, and a HOL Plugin Scanner workflow for
Codex plugin catalogs that require local validation evidence before listing.

## Configure

Create an API key in the TwexAPI dashboard, then set:

```bash
export TWEXAPI_KEY="twitterx_..."
```

Optional settings:

```bash
export TWEXAPI_BASE_URL="https://api.twexapi.io"
export HERMES_XAPI_ENABLE_ACTIONS="false"
```

Action endpoints are disabled unless `HERMES_XAPI_ENABLE_ACTIONS=true`.
If you configure keys through `~/.hermes/.env` during an active Hermes session,
use `/reload` in the interactive CLI, or restart gateway and cron sessions so
they pick up the new values.

## Security Model

Hermes XAPI never accepts credentials through tool arguments. Auth is read from
environment variables and injected by the plugin at request time.

The plugin blocks cookie/token helper routes, engagement-purchase routes,
auto-cookie posting, profile mutation, list creation, and sentiment routes from
the agent catalog. Private reads, paid-bulk endpoints, and write-like endpoints
go through `xapi_action`, which is hidden unless
`HERMES_XAPI_ENABLE_ACTIONS=true`.

## Tools

| Tool | Purpose |
| --- | --- |
| `xapi_explore` | Search the bundled TwexAPI endpoint catalog. No API call. |
| `xapi_read` | Call catalog-listed read-only endpoints. |
| `xapi_action` | Call write-like or private endpoints. Disabled by default. |

Use `xapi_explore` first, then call `xapi_read` or `xapi_action` with a
concrete TwexAPI path.
Copied endpoint URLs are accepted, but Hermes XAPI matches only catalog-listed
paths.

## Hermes Agent Workflows

Hermes XAPI is best used as the X context layer for Hermes Agent workflows that
need current public signal, authenticated account context, or approval-gated
account actions:

| Workflow | Recommended Path |
| --- | --- |
| Social listening | Use `xapi_explore` to find profile, trend, topic, search, and reply routes; use `xapi_read` only for no-approval reads. |
| Launch monitoring | Keep `xapi_action` disabled, schedule Hermes cron sessions around read-only trend, topic, profile, and status checks. |
| Support triage | Read public mentions and user timelines, summarize issues in Hermes, then hand off account-changing responses for explicit approval. |
| Creator or brand research | Combine X search, user profile, follower, article, and trend reads before drafting content or campaign briefs. |
| Community audits | Use read routes for tweet, reply, follower, list, community, and article evidence before any action route. |
| Controlled publishing | Enable `HERMES_XAPI_ENABLE_ACTIONS=true` only in sessions that require posting, DMs, follows, likes, retweets, bookmarks, or article publishing. |
| Desktop operator sessions | Use Hermes Desktop for interactive review, then keep action calls explicit and approval-gated. |
| Remote gateway teams | Install Hermes XAPI and set `TWEXAPI_KEY` on the remote gateway host, then connect Desktop profiles to that host. |
| Dashboard-administered agents | Use the dashboard for gateway and credential operations, but keep Hermes XAPI secrets in the runtime environment. |

For marketing or user education, position Hermes XAPI as a native Hermes Agent
plugin, not a generic API wrapper: it ships a PyPI entry point, a `plugin.yaml`
manifest with interactive secret prompts, slash commands for quick diagnostics,
and a bundled skill registered through Hermes' plugin skill system.

## Hermes Runtime Fit

Hermes XAPI registers a dedicated `hermes-xapi` plugin toolset. Hermes can
show and manage those tools through its normal `hermes tools` and platform
toolset flows, so teams can keep X automation available only where it belongs.
Current Hermes Agent releases discover third-party plugins but do not execute
them until they are enabled in `plugins.enabled`, through `hermes plugins enable`,
or by installing with `--enable`. This is expected safety behavior for user and
PyPI entry-point plugins.

Hermes Agent v0.16.0 expands the surfaces where the same toolset can appear:
the native Desktop app, remote gateway profiles, the web dashboard, the TUI,
and the CLI can all route work to the enabled runtime. Hermes XAPI does not
need a different plugin entry point for those surfaces. It needs the same
enabled plugin, the same runtime environment, and the same read/action split.

The v0.16.0 Desktop command palette surfaces skills and quick-command slash
commands. Treat `/xstatus` and `/xtrends` as interactive runtime commands for
active CLI, TUI, Desktop, or gateway sessions; keep `hermes -z` for tool-call
smoke tests.

The v0.16.0 dashboard added broader administration and credential-management
surfaces. Those are useful for gateway operations, but Hermes XAPI still reads
`TWEXAPI_KEY` and `HERMES_XAPI_ENABLE_ACTIONS` from the runtime environment.
Do not paste API keys into prompts, issue bodies, PR comments, or tool inputs.

For non-interactive smoke tests and CI-style diagnostics, use
`hermes tools list`; bare `hermes tools` opens the interactive tool UI and
requires a TTY. In current Hermes Agent releases, `hermes tools list` reports plugin toolsets,
not every individual plugin tool name.

Use the read-only path for social listening, trend research, public profile
checks, community audits, and draft planning. Keep `HERMES_XAPI_ENABLE_ACTIONS=false`
for unattended cron or gateway sessions unless the workflow has an explicit
approval step for posting, DMs, follows, likes, retweets, bookmarks, article
publishing, or other account actions.

Runtime smoke test:

```bash
hermes -z "Use xapi_explore, then read /twitter/elonmusk/about. Do not call xapi_action." --toolsets hermes-xapi
```

Expected results:

- `xapi_explore` discovers catalog endpoints without using the API key.
- Without `TWEXAPI_KEY`, a non-mutating Hermes probe exposes `xapi_explore`
  only.
- After `TWEXAPI_KEY` is configured and the CLI is reloaded, or the gateway
  or cron process is restarted, `xapi_read` can read `/twitter/elonmusk/about`.
- `xapi_action` stays hidden or disabled unless `HERMES_XAPI_ENABLE_ACTIONS=true`.
- `/xstatus` and `/xtrends` appear in the Hermes plugin command registry.

Hermes one-shot `hermes -z "/xstatus"` can run as a model prompt, not as the
interactive slash-command dispatcher. Verify slash commands in an active CLI,
TUI, Desktop, or gateway session, or through the plugin registry tests, and use
`hermes -z` for tool-call probes.

If `hermes plugins install` runs without a TTY, Hermes cannot safely prompt for
secrets and will skip API-key storage. This is expected; set `TWEXAPI_KEY`
in the process environment or `~/.hermes/.env`.

## Slash Commands

| Command | Purpose |
| --- | --- |
| `/xstatus` | Show TwexAPI account, subscription, and usage status. |
| `/xtrends` | Show current X trends. |

## Development

Generate the bundled catalog from TwexAPI OpenAPI:

```bash
python scripts/build_catalog.py ../twexapi/openapi.yaml
```

Run checks:

```bash
uv run --python 3.12 --extra dev ruff format --check .
uv run --python 3.12 --extra dev ruff check .
uv run --python 3.12 --extra dev basedpyright
uv run --python 3.12 --extra dev pytest --cov=hermes_xapi --cov=tests --cov-report=term-missing --cov-fail-under=100
uv run --python 3.12 --extra dev bandit -c pyproject.toml -r hermes_xapi scripts
uv run --python 3.12 --extra dev pip-audit
uv run --python 3.12 --extra dev python -m build
uv run --python 3.12 --extra dev twine check dist/*
```

For a single local quality gate:

```bash
uv run --python 3.12 --extra dev ruff format --check . && \
uv run --python 3.12 --extra dev ruff check . && \
uv run --python 3.12 --extra dev basedpyright && \
uv run --python 3.12 --extra dev pytest --cov=hermes_xapi --cov=tests --cov-report=term-missing --cov-fail-under=100 && \
uv run --python 3.12 --extra dev bandit -c pyproject.toml -r hermes_xapi scripts && \
uv run --python 3.12 --extra dev pip-audit && \
uv run --python 3.12 --extra dev python -m build && \
uv run --python 3.12 --extra dev twine check dist/*
```

## Relationship To TweetClaw

TweetClaw is the OpenClaw-native npm plugin. Hermes XAPI is the Hermes-native
Python plugin. Both use the same TwexAPI API contract.

## Public Repo Metadata

Recommended GitHub description:

> Native Hermes Agent plugin for X/Twitter automation through TwexAPI. Not affiliated with X Corp.

Recommended topics:

`hermes-agent`, `hermes-plugin`, `hermes`, `twitter`, `x-api`,
`x-automation`, `twexapi`, `tweet`, `automation`, `social-media`,
`social-media-automation`, `ai-agent`, `mcp`, `agent-tools`, `twitter-api`,
`twitter-automation`, `x-twitter`, `social-media-api`, `agent-skill`, `python`
