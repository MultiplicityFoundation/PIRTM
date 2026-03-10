# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 0.2.x | Yes |
| 0.1.x | Security fixes only |
| < 0.1 | No |

## Reporting a Vulnerability

Report vulnerabilities privately via GitHub Security Advisories:

https://github.com/MultiplicityFoundation/PIRTM/security/advisories/new

Do not open public issues for security vulnerabilities.

## Scope

PIRTM is a numerical Python library. Relevant security concerns include:

- Numeric instability causing unsafe certificates or bounds.
- Pathological inputs causing denial of service.
- Supply-chain compromise of release artifacts.

## Response Targets

- Acknowledgement: 48 hours
- Initial triage: 7 days
- Critical fix target: 14 days
- Moderate fix target: 30 days

## Dependency Policy

Runtime dependencies are intentionally small to reduce attack surface.
