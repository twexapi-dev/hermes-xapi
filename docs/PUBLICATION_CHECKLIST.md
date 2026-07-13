# Publication Checklist

Hermes XAPI is published as `hermes-xapi` on PyPI and currently released at
`0.1.6`.

## Before GitHub Publication

- [x] Set repository description from `docs/GITHUB_METADATA.md`.
- [x] Add recommended GitHub topics from `docs/GITHUB_METADATA.md`.
- [x] Enable issues, Actions, Dependabot alerts, and security updates.
- [x] Enable secret scanning and push protection.
- [x] Confirm branch protection requires CI.

## Before PyPI Publication

- [x] Add the PyPI trusted publisher for `twexapi-dev/hermes-xapi`.
- [x] Regenerate `hermes_xapi/catalog_data.json` from current TwexAPI OpenAPI.
- [x] Run the full quality gate from `AGENTS.md`.
- [x] Build from a clean working tree and run `twine check dist/*`.
- [x] Verify the wheel contains `plugin.yaml`, `catalog_data.json`, and the
  bundled Hermes skill.
- [x] Publish through GitHub Actions trusted publishing.
- [x] Verify PyPI metadata, README rendering, simple index visibility, and a
  fresh install.

## After Publication

- [x] Install from PyPI in a fresh environment.
- [x] Run `hermes plugins enable hermes-xapi`.
- [x] Confirm `xapi_explore`, `xapi_read`, `xapi_action`, `/xstatus`, and
  `/xtrends` load.
- [x] Confirm `xapi_action` is blocked unless
  `HERMES_XAPI_ENABLE_ACTIONS=true`.
- [x] Confirm PyPI, piwheels, ClawHub, first-party docs, Context7, DeepWiki,
  and accepted ecosystem listings show current public metadata.
- [x] Maintain accepted public ecosystem surfaces in `docs/ECOSYSTEM.md`.
- [x] Use `docs/SUBMISSION_READINESS.md` before public skill, plugin, catalog,
  registry, awesome-list, or integration submissions.
- [x] Keep Codex plugin metadata, root security policy, local icon, and scanner
  workflow ready for Codex catalog submissions.

## Release Gate

Run these checks before any new package release:

```bash
uv run --python 3.12 --extra dev ruff format --check .
uv run --python 3.12 --extra dev ruff check .
uv run --python 3.12 --extra dev basedpyright
uv run --python 3.12 --extra dev pytest --cov=hermes_xapi --cov=tests --cov-report=term-missing --cov-fail-under=100
uv run --python 3.12 --extra dev bandit -c pyproject.toml -r hermes_xapi scripts
uv run --python 3.12 --extra dev python scripts/check_public_safety.py
uv run --python 3.12 --extra dev pip-audit
uv run --python 3.12 --extra dev python scripts/check_public_links.py
uv run --python 3.12 --extra dev python scripts/check_hermes_agent_compat.py
uv run --python 3.12 --extra dev python -m build
uv run --python 3.12 --extra dev twine check dist/*
actionlint .github/workflows/*.yml
```

## Hermes Agent Compatibility Gate

Before changing plugin registration, manifests, install docs, or release
metadata, verify the current official Hermes Agent plugin docs and source:

- [Build a Hermes Plugin](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins)
- [Plugins feature guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/plugins/)
- [`hermes_cli/plugins.py`](https://github.com/NousResearch/hermes-agent/blob/main/hermes_cli/plugins.py)
- [`tools/registry.py`](https://github.com/NousResearch/hermes-agent/blob/main/tools/registry.py)
- [`hermes_cli/plugins_cmd.py`](https://github.com/NousResearch/hermes-agent/blob/main/hermes_cli/plugins_cmd.py)

Run the compatibility checker before release, outreach, or plugin-facing docs
updates:

```bash
uv run --python 3.12 --extra dev python scripts/check_hermes_agent_compat.py
```

If a locked Hermes Agent source SHA changes, review the official diff first,
then update Hermes XAPI runtime, docs, tests, and the checker lock together.

Latest reviewed locks from July 10, 2026: `hermes_cli/plugins.py`
`ea0b8ea2ffe1b6b5c3616f4bc005081a09141337`, `tools/registry.py`
`9b6611fb407dd17da5aa4ae2ba6a39498af830da`, and
`hermes_cli/plugins_cmd.py` `6a7c39f3e4e014f98201766e980d19c696e1c545`.

Keep the runtime contract aligned with those sources:

- `plugin.yaml` keeps the rich `TWEXAPI_KEY` `requires_env` installer prompt.
- `xapi_explore` stays ungated and makes no network call.
- `xapi_read` stays gated by `check_api_available` and `TWEXAPI_KEY`.
- `xapi_action` stays gated by `action_enabled`, `TWEXAPI_KEY`, and
  `HERMES_XAPI_ENABLE_ACTIONS`.
- Tool handlers accept future Hermes context keyword arguments, catch
  exceptions, and return JSON strings.
- Bundled skills continue to register through `ctx.register_skill`.
- Install docs explain that user and PyPI entry-point plugins are opt-in and
  need `--enable`, `hermes plugins enable hermes-xapi`, or an explicit
  `plugins.enabled` entry.
- Local project-plugin docs mention `HERMES_ENABLE_PROJECT_PLUGINS=true` only
  for trusted repositories.
- User-facing docs keep at least one concrete Hermes Agent workflow section for
  social listening, launch monitoring, support triage, research, audits, and
  controlled publishing.

## Runtime Smoke Test

Use a local secret store or ephemeral environment variable. Never paste an API
key into chat, commits, PRs, issues, or logs.

```bash
hermes tools list
hermes -z "Use xapi_explore, then read /twitter/elonmusk/about. Do not call xapi_action." --toolsets hermes-xapi
```

Expected result:

- `xapi_explore` loads without an API call.
- Copied endpoint URLs resolve only to catalog-listed TwexAPI paths.
- `xapi_read` works when `TWEXAPI_KEY` is configured.
- `xapi_action` stays hidden or returns a disabled error unless actions are
  explicitly enabled.
- `/xstatus` and `/xtrends` are registered slash commands.

## Manual Operator Actions

Keep optional signed-in submissions, local-secret smoke tests, pending outreach,
duplicate checks, and maintainer-blocked directory routes in private operator
notes. Do not commit those operational notes to the public repository. No
package release blocker remains after the `0.1.6` release.
