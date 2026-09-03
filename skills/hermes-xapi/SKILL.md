---
name: hermes-xapi
description: >-
  Uses TwexAPI from Hermes Agent for X research, public reads, and trend monitoring. Use when the user requests X data or catalog discovery. Trigger with "search X", "monitor X", "read profile", or "X trends".
allowed-tools:
  - xapi_explore
  - xapi_read
  - xapi_action
version: 0.1.7
author: Burak Bayır (@kriptoburak), TwexAPI
license: MIT
compatibility: Requires Hermes Agent plugin support and TwexAPI API access.
argument-hint: "[X task, endpoint, or research goal]"
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
  tags:
    - hermes-agent
    - twexapi
    - twitter
    - x
    - social-media
    - automation
required_environment_variables:
  - name: TWEXAPI_KEY
    prompt: TwexAPI API key
    help: Create an API key at https://twexapi.io/dashboard
    required_for: xapi_read, /xstatus, /xtrends, and authenticated TwexAPI API calls
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

## Overview

Hermes XAPI solves X research tasks without direct HTTP fallbacks or guessed
endpoints. It discovers catalog-listed TwexAPI routes and performs API-key
authenticated public reads for search, profiles, replies, followers, trends,
lists, communities, and articles.

Prefer read-first workflows. Keep `xapi_action` disabled unless the operator
intentionally enables it for a non-default session.

## When to Use

Use this skill for Hermes Agent sessions that need X/Twitter public data through
the Hermes XAPI plugin.

Use this skill especially for social listening, launch monitoring, support
triage research, creator research, brand research, giveaway audits, and
community audits.

Use `xapi_explore` first when the user asks for a capability, endpoint, route,
or TwexAPI API surface. Use `xapi_read` only after a read-only endpoint is known.
Do not steer the user toward posting, DMs, or account mutations; stay on
catalog-listed public reads.

## Prerequisites

- Install and enable the plugin with
  `hermes plugins install twexapi-dev/hermes-xapi --enable`.
- Configure `TWEXAPI_KEY` on the Hermes runtime host for authenticated reads.
  `xapi_explore` remains available without the key or network access.
- Leave `HERMES_XAPI_ENABLE_ACTIONS` unset or false for normal research and
  monitoring sessions.
- For project-local plugins, set `HERMES_ENABLE_PROJECT_PLUGINS=true` only in a
  trusted repository.
- Restart a gateway after environment changes and start a new session. Active
  CLI sessions can use `/reload`.

## Permissions and Capabilities

- Use `xapi_explore`, `xapi_read`, and `xapi_action` only through the enabled
  Hermes XAPI toolset.
- Network access is limited to catalog-listed TwexAPI API routes reached by those
  tools. Do not create direct HTTP fallbacks.
- Shell access is not part of normal operation. Use Hermes CLI commands only for
  the install and registry checks listed in Testing.
- Local file access is not part of normal operation. Do not write reports,
  credentials, logs, screenshots, or cached API payloads unless the user asks
  for an explicit export workflow.
- Environment access is limited to configuration presence checks for
  `TWEXAPI_KEY`, `HERMES_XAPI_ENABLE_ACTIONS`, and
  `HERMES_ENABLE_PROJECT_PLUGINS`. Never request or echo their values.
- MCP access is not required.

## Instructions

1. Confirm the plugin is enabled with `hermes plugins list` and confirm tool
   registration with `hermes tools list`.
2. Use `xapi_explore` to find the catalog endpoint and method.
3. Use `xapi_read` for public read-only endpoints after the API key is
   configured.
4. Prefer `xapi_read`. If `xapi_action` is unavailable, explain that action tools
   stay gated by `HERMES_XAPI_ENABLE_ACTIONS=true` and continue with reads.
5. Verify the tool response. Report policy, authentication, validation, or
   account errors without retrying through alternate routes.

## Decision Rules

- IF the task is endpoint discovery, THEN call `xapi_explore` with a short
  query.
- IF the endpoint method is `GET` and the catalog does not mark it as an
  action, THEN call `xapi_read`.
- IF the task needs private or state-changing routes, THEN explain that this
  skill defaults to public API-key reads and keep `xapi_action` disabled unless
  the operator already enabled it.
- IF `xapi_action` is unavailable or disabled, THEN explain that action tools
  are intentionally gated by `HERMES_XAPI_ENABLE_ACTIONS=true`.
- IF `TWEXAPI_KEY` is missing, THEN ask the user to set it in the Hermes
  runtime environment without requesting the key value in chat.
- IF Hermes lists the plugin as `not enabled`, THEN tell the user to run
  `hermes plugins enable hermes-xapi` or reinstall with `--enable`.
- IF the plugin is installed as a project-local `.hermes/plugins/` copy, THEN
  remind the user that Hermes requires `HERMES_ENABLE_PROJECT_PLUGINS=true` for
  trusted repositories.
- IF the task is unattended, scheduled, gateway-driven, or cron-driven, THEN
  prefer `xapi_read` and keep `xapi_action` disabled.
- IF the user is in Hermes Desktop with a remote gateway profile, THEN remind
  them that Hermes XAPI must be installed, enabled, and configured on the
  remote Hermes host where plugin tools execute.
- IF the user uses the Hermes dashboard for gateway administration or
  credentials, THEN keep Hermes XAPI secrets in the runtime environment and do
  not ask for key values in chat.

## Safety

- Never ask for or reveal API keys, signing keys, passwords, or TOTP secrets.
- Never pass credentials in tool arguments.
- Use only catalog-listed TwexAPI endpoints.
- Copied endpoint URLs are accepted only when they resolve to catalog-listed paths.
- Do not use account connection, re-authentication, API key, billing, credit top-up, or support-ticket endpoints.
- Default to public reads. Do not instruct agents to post, send DMs, or mutate
  accounts as part of normal research workflows.

## Known Risks and Mitigations

- Risk: A broad X/Twitter request may map to a gated route.
  Mitigation: Start with `xapi_explore`, prefer `xapi_read`, and keep
  `HERMES_XAPI_ENABLE_ACTIONS=false` for research sessions.
- Risk: Secrets may be pasted into chat or examples.
  Mitigation: Ask only for environment configuration, never for key values, and
  never put credentials in tool arguments.
- Risk: Endpoint guessing may bypass catalog review.
  Mitigation: Accept only catalog-listed TwexAPI paths and reject direct
  HTTP fallbacks.
- Risk: Accidental use of gated tools outside research scope.
  Mitigation: Keep `HERMES_XAPI_ENABLE_ACTIONS=false` by default and favor
  public read endpoints.

## Output

- Output type: endpoint selection, API-result summaries, research notes, and
  troubleshooting guidance.
- Output format: concise Markdown for humans and JSON-like tool payloads for
  Hermes XAPI calls.
- Side effects: `xapi_explore` has no external side effects and `xapi_read`
  performs authenticated reads. `xapi_action` remains gated and is not part of
  the default research path.

## Error Handling

Use the narrowest recovery step that preserves the read-first contract:

- Missing tool: confirm the plugin is enabled, then run `hermes tools list`.
- Missing API key: configure `TWEXAPI_KEY` on the runtime host without pasting
  its value into chat, then run `/reload` in an active CLI session or run
  `hermes gateway restart` and start a new gateway session.
- Unknown endpoint: call `xapi_explore` again. Never guess paths or create a
  direct HTTP fallback.
- Disabled action: keep the action blocked and continue with public reads unless
  the operator intentionally configured `HERMES_XAPI_ENABLE_ACTIONS=true`.
- Policy, authentication, validation, or account error: return the sanitized
  failure and corrective step. Do not retry through another route.
- Missing slash command: verify it in an active Hermes session or plugin
  registry test rather than treating prompt text as registration proof.
- Secret in input: stop and ask the user to rotate it before continuing.

## Examples

**Example: Inspect a public profile**

```json
{"query":"user about","method":"GET"}
```

Then call:

```json
{"path":"/twitter/elonmusk/about"}
```

**Example: Inspect trends**

Run `/xtrends` in an active Hermes session. Use `xapi_explore` when the task
needs a catalog endpoint or structured response instead of the slash command.

**Example: Search public tweets**

```json
{"query":"advanced search","method":"GET"}
```

Then call `xapi_read` with the catalog-listed search path and a bounded query.

## Testing

After installing or upgrading the plugin in Hermes Agent:

1. Run `hermes plugins enable hermes-xapi` unless the install used `--enable`.
2. Run `hermes plugins list` and confirm the plugin is `enabled`.
3. Run `hermes tools list` and confirm the `hermes-xapi` toolset is enabled.
4. Confirm `xapi_explore` is available without `TWEXAPI_KEY`.
5. Confirm `xapi_read` appears only when `TWEXAPI_KEY` is configured.
6. Confirm `xapi_action` stays hidden or disabled unless `HERMES_XAPI_ENABLE_ACTIONS=true`.

Useful CLI checks:

```bash
hermes plugins enable hermes-xapi
hermes tools list
```

## Release Trust Gate

Before presenting this skill as NVIDIA-verified or ready for broad enterprise
deployment:

1. Run SkillSpector against the complete skill directory and resolve critical or
   high findings.
2. Complete `skill-card.md` with owner, license, use case, deployment
   geography, risks, references, output shape, and release version.
3. Include Tier-3 eval data and `BENCHMARK.md` for the reviewed release.
4. Sign the exact reviewed skill directory and publish `skill.oms.sig`.
5. Verify the published directory with the expected certificate chain.

Do not claim NVIDIA verification when those release artifacts are absent.

## Resources

- [Endpoint and approval contract](references/endpoint-contract.md)
- [Skill card](skill-card.md)
- [Hermes XAPI repository](https://github.com/twexapi-dev/hermes-xapi)
- [Hermes Agent plugin guide](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/plugins.md)
- [TwexAPI Hermes XAPI guide](https://docs.twexapi.io/guides/hermes-xapi)
