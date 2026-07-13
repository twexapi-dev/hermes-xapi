# Hermes XAPI Skill Card

Status: public self-assessment. Not NVIDIA-verified.

Do not present Hermes XAPI as NVIDIA-verified unless the release also includes
a clean SkillSpector scan report, Tier-3 eval data, `BENCHMARK.md`,
`skill.oms.sig`, and signature verification instructions for the exact reviewed
skill directory.

## Owner

- Publisher: TwexAPI
- Repository: https://github.com/twexapi-dev/hermes-xapi
- License: MIT
- Version: 0.1.6
- Primary skill file: `SKILL.md`

## Use Case

Hermes XAPI helps Hermes Agent users find X/Twitter endpoints, perform
authenticated X/Twitter reads, and run explicitly approved X/Twitter workflow
actions through the bundled Hermes XAPI tools.

Use it for:

- Searching tweets, reading tweet details, replies, and user profiles.
- Preparing action previews for posts, replies, follows, direct messages,
  likes, retweets, bookmarks, and article publishing.
- Keeping X/Twitter automation inside catalog-listed TwexAPI API routes.

Do not use it for account connection, re-authentication, billing, credit top-up,
support tickets, or direct HTTP fallback routes.

## Inputs and Configuration

- Required configuration: `TWEXAPI_KEY` must be configured in the runtime
  environment. Never request, echo, log, or store the value.
- Action gate: `HERMES_XAPI_ENABLE_ACTIONS=true` is required before
  write-capable tool calls.
- Project plugin gate: `HERMES_ENABLE_PROJECT_PLUGINS=true` is required for
  trusted local Hermes project plugin loading.
- User input: natural language requests, endpoint choices, and explicit action
  payload approval.

## Capabilities

- Tools: `xapi_explore`, `xapi_read`, `xapi_action`.
- Network: required only through catalog-listed TwexAPI API routes reached by
  those tools.
- Shell: not required for normal operation. Use Hermes CLI commands only for
  installation and registry diagnostics.
- Files: not required for normal operation. Do not write reports, credentials,
  logs, screenshots, or cached payloads unless the user asks for an explicit
  export workflow.
- MCP: not required.

## Outputs

- Endpoint recommendations from `xapi_explore`.
- Concise summaries of authenticated read results from `xapi_read`.
- Action previews, JSON-like payloads, and post-call summaries for
  user-approved `xapi_action` calls.
- Troubleshooting guidance for missing configuration or disabled action gates.

## Side Effects

- `xapi_explore` has no external side effects.
- `xapi_read` performs authenticated reads.
- `xapi_action` may change account or workflow state only after explicit user
  approval and only when the action gate is enabled.

## Known Risks and Mitigations

- Risk: a broad X/Twitter request may map to a write-capable route.
  Mitigation: start with `xapi_explore`, prefer `xapi_read`, and require a
  user-approved endpoint plus payload before `xapi_action`.
- Risk: secrets may appear in chat or examples.
  Mitigation: ask only for environment configuration, never key values, and
  never put credentials in tool arguments.
- Risk: endpoint guessing may bypass catalog review.
  Mitigation: accept only catalog-listed TwexAPI paths and reject direct
  HTTP fallbacks.
- Risk: automated X/Twitter actions can affect real accounts.
  Mitigation: keep `HERMES_XAPI_ENABLE_ACTIONS=false` by default and summarize
  side effects before any account-changing call.

## Release Trust Gate

Before broad enterprise release or any NVIDIA-verified claim:

1. Run SkillSpector against the complete skill directory.
2. Resolve critical or high findings.
3. Add Tier-3 eval data and `BENCHMARK.md` for the reviewed release.
4. Sign the exact reviewed skill directory and publish `skill.oms.sig`.
5. Verify the published directory with the expected certificate chain.

## References

- `SKILL.md`
- `README.md`
- `after-install.md`
- `SECURITY.md`
