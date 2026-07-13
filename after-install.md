# Hermes XAPI Installed

Hermes XAPI is enabled as the `hermes-xapi` toolset.

If this plugin was installed without `--enable`, Hermes may show it as
`not enabled` until you run:

```bash
hermes plugins enable hermes-xapi
hermes plugins list
```

Set your TwexAPI API key before using read tools:

```bash
export TWEXAPI_KEY="twitterx_..."
```

For persistent Hermes sessions, add it to `~/.hermes/.env`:

```bash
TWEXAPI_KEY=twitterx_...
```

If Hermes is already running after you edit `~/.hermes/.env`, use `/reload` in
an interactive CLI session, or restart gateway and cron sessions before calling
`xapi_read`.
When `TWEXAPI_KEY` is missing, Hermes should expose only `xapi_explore` from
this plugin. Set the key, then reload the CLI or restart the gateway or cron
process before expecting `xapi_read`.

Keep actions disabled unless you are intentionally allowing account-changing
operations:

```bash
export HERMES_XAPI_ENABLE_ACTIONS=false
```

Quick smoke test:

```bash
hermes -z "Use xapi_explore, then read /twitter/elonmusk/about. Do not call xapi_action." --toolsets hermes-xapi
```

Use catalog-listed TwexAPI paths from `xapi_explore`. Copied endpoint
URLs are accepted only when they resolve to catalog-listed paths.

Expected behavior:

- `xapi_explore` loads without an API call.
- `xapi_read` works when `TWEXAPI_KEY` is set.
- `/xstatus` and `/xtrends` are registered slash commands.
- `xapi_action` stays hidden or returns a disabled error unless
  `HERMES_XAPI_ENABLE_ACTIONS=true`.

For Hermes v0.12.0, do not use `hermes -z "/xstatus"` as a slash-command smoke
test. One-shot `-z` treats that text as a model prompt. Verify slash commands in
an active CLI or gateway session, or through the plugin registry tests.
