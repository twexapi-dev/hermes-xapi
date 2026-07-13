# Context7 Guide

Use this page as the compact Context7-facing guide for Hermes XAPI. It focuses
on install, auth, safe tool use, and smoke tests for coding agents.

## Install

Install from the public GitHub repository:

```bash
hermes plugins install twexapi-dev/hermes-xapi --enable
```

Hermes plugins are opt-in. If the plugin was installed without `--enable`, run:

```bash
hermes plugins enable hermes-xapi
hermes plugins list
```

Install the published Python package into the Hermes Python environment:

```bash
uv pip install --python ~/.hermes/hermes-agent/venv/bin/python hermes-xapi
hermes plugins enable hermes-xapi
```

Use the PyPI package name `hermes-xapi` and the Hermes toolset name
`hermes-xapi`.

Hermes Agent v0.16.0 includes Desktop and remote gateway profiles. For a remote
gateway profile, install and enable Hermes XAPI on the remote Hermes host and
set `TWEXAPI_KEY` there. The desktop app is only the client surface unless it
also runs the Hermes runtime locally.

## Configure

Create an API key in the TwexAPI dashboard and set it in the runtime environment:

```bash
export TWEXAPI_KEY="twitterx_..."
```

Optional settings:

```bash
export TWEXAPI_BASE_URL="https://api.twexapi.io"
export HERMES_XAPI_ENABLE_ACTIONS="false"
```

Hermes XAPI never accepts credentials through tool arguments. If
`TWEXAPI_KEY` is missing, Hermes should expose only `xapi_explore`. That is
expected safe gating.

## Tools

| Tool | Use |
| --- | --- |
| `xapi_explore` | Search the bundled TwexAPI endpoint catalog without an API call. |
| `xapi_read` | Call catalog-listed read-only TwexAPI API endpoints. |
| `xapi_action` | Call write-like or private endpoints when actions are enabled. |

Use `xapi_explore` first. Then call `xapi_read` with a concrete
TwexAPI path for public profile checks, trend lookup, account status,
community/list context, or article markdown reads.
Copied endpoint URLs are accepted only when they resolve to catalog-listed
paths.

## Hermes Agent Patterns

- Treat Hermes XAPI as the X context layer for Hermes Agent research,
  monitoring, support, launch, and content workflows.
- Use read-only routes for cron, gateway, and unattended sessions.
- Keep action routes for explicit user-approved posting, DMs, follows, likes,
  retweets, bookmarks, paid-bulk reads, and article publishing.
- Use `hermes plugins list` for enablement diagnostics because current Hermes
  Agent versions distinguish `enabled`, `disabled`, and `not enabled` plugins.
- Use project-local `.hermes/plugins/` copies only in trusted repositories and
  only with `HERMES_ENABLE_PROJECT_PLUGINS=true`.
- In Hermes Desktop, TUI, CLI, and gateway sessions, use `/xstatus` and
  `/xtrends` as interactive commands. Use `hermes -z` for tool-call probes.
- The Hermes dashboard can help administer gateway credentials, but
  Hermes XAPI still reads `TWEXAPI_KEY` and action gating from the runtime
  environment.

Keep `HERMES_XAPI_ENABLE_ACTIONS=false` for unattended sessions. Enable actions
only when the workflow intentionally allows posting, replies, likes, retweets,
follows, DMs, bookmarks, paid-bulk reads, article publishing, or other account
changes.

## Smoke Test

```bash
hermes tools list
hermes -z "Use xapi_explore, then read /twitter/elonmusk/about. Do not call xapi_action." --toolsets hermes-xapi
```

Expected result:

- `xapi_explore` finds endpoints without using the API key.
- `xapi_read` can read `/twitter/elonmusk/about` after `TWEXAPI_KEY` is set.
- `xapi_action` stays disabled unless `HERMES_XAPI_ENABLE_ACTIONS=true`.
- `/xstatus` and `/xtrends` are registered slash commands.

If you edit `~/.hermes/.env` during an active Hermes CLI session, run
`/reload`. Gateway and cron sessions need a restart or new session.

## Public Sources

- GitHub: <https://github.com/twexapi-dev/hermes-xapi>
- Repository guide: <https://github.com/twexapi-dev/hermes-xapi#readme>
- PyPI: <https://pypi.org/project/hermes-xapi/>
- DeepWiki: <https://deepwiki.com/twexapi-dev/hermes-xapi>
- Context7: <https://context7.com/twexapi-dev/hermes-xapi>
- Hermes Agent plugins guide: <https://hermes-agent.nousresearch.com/docs/user-guide/features/plugins/>
- Build a Hermes Plugin: <https://hermes-agent.nousresearch.com/docs/developer-guide/plugins>
