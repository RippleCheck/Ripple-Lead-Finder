# Security Policy

## Reporting a vulnerability

Please report security issues **privately** — do not open a public issue, and please
don't disclose the problem publicly until it has been resolved.

The preferred channel is GitHub's built-in private vulnerability reporting:

1. Go to the repository's **[Security tab](https://github.com/RippleCheck/Ripple-Lead-Finder/security)**.
2. Click **Report a vulnerability**.
3. Describe the issue with enough detail to reproduce it.

That opens a private advisory visible only to the maintainers. If you can't use that
channel, reach the maintainer through their GitHub profile:
**[@agrajeet-builds](https://github.com/agrajeet-builds)**.

Where you can, please include:

- what the issue is and its impact,
- steps to reproduce or a proof of concept,
- the affected version or commit.

## Scope & context

Ripple Lead Finder is a **local desktop tool**: it runs on `127.0.0.1` on your own
machine, with no hosted service behind it. There is no server for the maintainers to
patch on your behalf — fixes ship as new releases you download. The most relevant
areas are local file-permission handling, request handling in the bundled local
server, and output escaping in the dashboard.

## Supported versions

The latest release on the `main` branch receives security fixes.
