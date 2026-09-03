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
- Version: 0.1.7
- Primary skill file: `SKILL.md`

## Use Case

Hermes XAPI helps Hermes Agent users find X/Twitter endpoints and perform
API-key authenticated public X/Twitter reads through the bundled Hermes XAPI
tools.

Use it for:

- Searching tweets, reading tweet details, replies, and user profiles.
- Checking trends, followers, lists, communities, and articles for research.
- Keeping X/Twitter research inside catalog-listed TwexAPI API routes.

Do not use it for account connection, re-authentication, billing, credit top-up,
support tickets, or direct HTTP fallback routes. Do not treat posting, DMs, or
cookie workflows as the default skill path.

## Inputs and Configuration

- Required configuration: `TWEXAPI_KEY` must be configured in the runtime
  environment. Never request, echo, log, or store the value.
- Action gate: `HERMES_XAPI_ENABLE_ACTIONS=true` is required before gated
  non-read tool calls. Leave it disabled for normal research.
- Project plugin gate: `HERMES_ENABLE_PROJECT_PLUGINS=true` is required for
  trusted local Hermes project plugin loading.
- User input: natural language research requests and endpoint choices.

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
- Troubleshooting guidance for missing configuration or disabled action gates.

## Side Effects

- `xapi_explore` has no external side effects.
- `xapi_read` performs authenticated reads.
- `xapi_action` stays gated and is not part of the default research path.

## Known Risks and Mitigations

- Risk: a broad X/Twitter request may map to a gated route.
  Mitigation: start with `xapi_explore`, prefer `xapi_read`, and keep
  `HERMES_XAPI_ENABLE_ACTIONS=false` for research sessions.
- Risk: secrets may appear in chat or examples.
  Mitigation: ask only for environment configuration, never key values, and
  never put credentials in tool arguments.
- Risk: endpoint guessing may bypass catalog review.
  Mitigation: accept only catalog-listed TwexAPI paths and reject direct
  HTTP fallbacks.
- Risk: accidental use of gated tools outside research scope.
  Mitigation: keep `HERMES_XAPI_ENABLE_ACTIONS=false` by default and favor
  public read endpoints.

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
