---
name: hermes-xapi
description: >-
  Uses TwexAPI from Hermes Agent for X research, monitoring, and approval-gated actions. Use when the user requests X data or an approved X action. Trigger with "search X", "monitor X", "post tweet", or "X trends".
allowed-tools:
  - xapi_explore
  - xapi_read
  - xapi_action
version: 0.1.6
author: Burak Bayır (@kriptoburak), TwexAPI
license: MIT
compatibility: Requires Hermes Agent plugin support and TwexAPI API access.
argument-hint: "[X task, endpoint, or approved action]"
tags:
  - hermes-agent
  - twexapi
  - twitter
  - x
  - social-media
  - automation
metadata:
  version: 0.1.6
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
    justification: Hermes XAPI tools call TwexAPI API routes for X/Twitter reads and approved actions.
  files:
    required: false
    justification: Normal use does not require local file reads or writes.
  environment:
    required: true
    variables:
      - TWEXAPI_KEY
      - HERMES_XAPI_ENABLE_ACTIONS
      - HERMES_ENABLE_PROJECT_PLUGINS
    justification: Runtime configuration controls authenticated reads, gated actions, and trusted project-local plugin loading.
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

Hermes XAPI solves X research and automation tasks without direct HTTP fallbacks
or guessed endpoints. It discovers catalog-listed TwexAPI routes, performs
authenticated reads, and keeps write-like or private operations behind an
explicit environment gate and user approval.

Use the skill for read-first workflows. Enable action tooling only for a named
operation whose endpoint, payload, account, and side effects the user approves.

## When to Use

Use this skill for Hermes Agent sessions that need X/Twitter data or controlled
X actions through the Hermes XAPI plugin.

Use this skill especially for social listening, launch monitoring, support
triage, creator research, brand research, giveaway audits, community audits,
and controlled publishing workflows.

Use `xapi_explore` first when the user asks for a capability, endpoint, route,
or TwexAPI API surface. Use `xapi_read` only after a read-only endpoint is known.
Use `xapi_action` only after the user requests a write, private read, monitor,
webhook, extraction job, giveaway draw, or media operation that requires action
permissions.

## Prerequisites

- Install and enable the plugin with
  `hermes plugins install twexapi-dev/hermes-xapi --enable`.
- Configure `TWEXAPI_KEY` on the Hermes runtime host for authenticated reads.
  `xapi_explore` remains available without the key or network access.
- Leave `HERMES_XAPI_ENABLE_ACTIONS` unset or false unless the workflow needs
  an approved write-like or private operation.
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
4. Before `xapi_action`, state the exact endpoint, payload, account, reason,
   and expected side effects, then get explicit approval.
5. Verify the tool response. Report policy, authentication, validation, or
   account errors without retrying through alternate routes.

## Decision Rules

- IF the task is endpoint discovery, THEN call `xapi_explore` with a short
  query.
- IF the endpoint method is `GET` and the catalog does not mark it as an
  action, THEN call `xapi_read`.
- IF the endpoint method is not `GET`, or the route touches private account
  state, THEN call `xapi_action` only when actions are enabled and the user has
  approved the operation.
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
  prefer `xapi_read` and keep `xapi_action` disabled unless the workflow has a
  clear approval step.
- IF the user is in Hermes Desktop with a remote gateway profile, THEN remind
  them that Hermes XAPI must be installed, enabled, and configured on the
  remote Hermes host where plugin tools execute.
- IF the user uses the Hermes dashboard for gateway administration or
  credentials, THEN keep Hermes XAPI secrets in the runtime environment and do
  not ask for key values in chat.

## Safety

- Never ask for or reveal API keys, signing keys, passwords, cookies, or TOTP secrets.
- Never pass credentials in tool arguments.
- Use only catalog-listed TwexAPI endpoints.
- Copied endpoint URLs are accepted only when they resolve to catalog-listed paths.
- Do not use account connection, re-authentication, API key, billing, credit top-up, or support-ticket endpoints.
- For posting, deleting, following, DMs, profile changes, likes, retweets,
  bookmarks, and article publishing, summarize the action before calling
  `xapi_action`.

## Known Risks and Mitigations

- Risk: A broad X/Twitter request may map to a write-capable route.
  Mitigation: Start with `xapi_explore`, prefer `xapi_read`, and require a
  user-approved endpoint plus payload before `xapi_action`.
- Risk: Secrets may be pasted into chat or examples.
  Mitigation: Ask only for environment configuration, never for key values, and
  never put credentials in tool arguments.
- Risk: Endpoint guessing may bypass catalog review.
  Mitigation: Accept only catalog-listed TwexAPI paths and reject direct
  HTTP fallbacks.
- Risk: Automated X/Twitter actions can affect real accounts.
  Mitigation: Keep `HERMES_XAPI_ENABLE_ACTIONS=false` by default and summarize
  side effects before any account-changing call.

## Output

- Output type: endpoint selection, API-result summaries, action previews, and
  troubleshooting guidance.
- Output format: concise Markdown for humans and JSON-like tool payloads for
  Hermes XAPI calls.
- Side effects: `xapi_explore` has no external side effects, `xapi_read`
  performs authenticated reads, and `xapi_action` may change account or
  workflow state only after explicit approval.

## Error Handling

Use the narrowest recovery step that preserves the read-first and action-gated
contract:

- Missing tool: confirm the plugin is enabled, then run `hermes tools list`.
- Missing API key: configure `TWEXAPI_KEY` on the runtime host without pasting
  its value into chat, then run `/reload` in an active CLI session or run
  `hermes gateway restart` and start a new gateway session.
- Unknown endpoint: call `xapi_explore` again. Never guess paths or create a
  direct HTTP fallback.
- Disabled action: keep the action blocked unless the user requested it and
  `HERMES_XAPI_ENABLE_ACTIONS=true` is intentionally configured.
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

**Example: Post a tweet**

```json
{"query":"post tweet","include_actions":true}
```

Then call `xapi_action` with:

```json
{"path":"/twitter/tweets/create","method":"POST","body":{"account":"@example","text":"Hello from Hermes XAPI"},"reason":"Post the user-approved tweet."}
```

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
