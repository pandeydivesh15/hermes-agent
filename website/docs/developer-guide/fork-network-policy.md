# This fork blocks optional outbound network features

This fork retains upstream telemetry and relay code for rebases, but blocks
its network paths in source. Configuration and environment opt-ins cannot
re-enable those paths. The Python policy lives in
`hermes_cli/fork_network_policy.py`; Desktop's policy lives in
`apps/desktop/src/lib/fork-network-policy.ts`.

## Telemetry and relay cannot transmit

Shared-metrics uploads, OTLP exporter initialization, CUA driver telemetry,
browser-use, Vercel SDK, and bundled Photon SDK telemetry are disabled.
Local metrics collection
may still run if configured. Relay URL discovery, identity acquisition,
connector HTTP requests, WebSocket dialing, and media transfers are blocked.
Ordinary configured model-provider and messaging transports remain available.
External plugins execute with agent privileges and require separate review;
these source gates are not an OS network sandbox.

## Update checks require an explicit request

CLI and backend passive update checks stop before checkout or network probes.
Desktop startup, focus, periodic polling, and remote-profile switches do not
initiate update checks. Explicit update checks and source update commands
remain available. Updating the source still requires reviewing these fork
patches after a rebase.

## MCP startup checks local advisory verdicts

Starting an MCP server no longer queries OSV. It consults the local verdict
cache. Known malware verdicts remain blocking after expiry and restart;
expired clean verdicts do not establish current advisory coverage. A package
with no local verdict is allowed with a warning, matching the previous
fail-open behavior without disclosing package metadata automatically.

`hermes security audit` remains an explicit online operation. It sends
installed dependency names and versions to OSV and refreshes local malware
verdicts for the exact package versions it audits. A clean response can clear
a previous block. Unpinned package specifications may have no matching local
verdict. This is not a complete offline malware database.

## Credential-filter errors prevent child launches

Computer-use probes and permission commands propagate environment-filter
failures instead of launching a driver with inherited provider credentials.
A failed probe can therefore report unavailable rather than launch unsafely.

## Remote webhook payloads require HTTPS

Outbound hooks reject remote plaintext HTTP and URLs containing embedded
credentials. HTTP is retained only for literal `127.0.0.1`, `::1`, and
`localhost` hosts; those requests bypass environment-configured proxies.
Redirects remain disabled for all webhook deliveries.

TODO for @divesh: re-check these gates after each upstream rebase. New
network call sites need review even when the retained gates still apply.
