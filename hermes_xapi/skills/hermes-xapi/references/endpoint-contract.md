# Endpoint and Approval Contract

Use this reference when the selected TwexAPI route or approval boundary is
unclear. The rules apply to CLI, Desktop, dashboard, gateway, scheduled, and
delegated Hermes Agent sessions.

## Tool Matrix

| Tool | API key | Network | Action gate | User approval |
|---|---:|---:|---:|---:|
| `xapi_explore` | No | No | No | No |
| `xapi_read` | Yes | Yes | No | No for public read-only routes |
| `xapi_action` | Yes | Yes | Yes | Yes for the exact operation |

`xapi_explore` reads the bundled catalog. `xapi_read` accepts only
catalog-listed read-only routes. `xapi_action` is gated and disabled by
default; prefer public reads for research and monitoring.

## Approval Checklist

Default agent workflows use `xapi_explore` and `xapi_read` only. If an
operator has enabled `xapi_action`, confirm before any call:

1. The catalog-listed endpoint and method.
2. The target account or workflow.
3. The complete payload without credentials.
4. The expected side effects and reason.
5. The operator's explicit approval for this non-default operation.

Approval for one operation does not authorize retries, related operations, or
future scheduled runs. Stop after policy, authentication, validation, or
account-state failures.

## Hermes Agent Surfaces

Hermes XAPI uses the same plugin entry point across Desktop, TUI, CLI,
dashboard, and gateway sessions. Install and configure the plugin on the Hermes
runtime host where tools execute. Remote Desktop profiles do not move secrets or
plugin state from the gateway host.

Use active CLI or gateway sessions for `/xstatus` and `/xtrends`. Keep
`HERMES_XAPI_ENABLE_ACTIONS=false` for research, monitoring, and unattended
sessions.

## Runtime Checks

```bash
hermes plugins list
hermes tools list
```

Confirm that `xapi_explore` remains available without `TWEXAPI_KEY`,
`xapi_read` appears only with the key, and `xapi_action` remains unavailable
unless `HERMES_XAPI_ENABLE_ACTIONS=true` is intentionally configured.

After environment changes, reload an active CLI session. For gateway use, run
`hermes gateway restart`, then start a new session.

## Version History

- Unreleased: Add marketplace metadata, required sections, and reference docs.
- Unreleased: Add capability declarations, risk controls, and release gates.
- 0.1.7: Sync catalog to TwexAPI OpenAPI copy 8 and prefer highest endpoint versions.
- 0.1.6: Refresh catalog wording from the current TwexAPI OpenAPI.
- 0.1.5: Add registry metadata and Hermes runtime guidance.
- 0.1.4: Add public registry frontmatter for skill discovery.
