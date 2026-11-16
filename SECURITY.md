# Security Policy

## Reporting a vulnerability

Please do not disclose security vulnerabilities in public issues.

Report suspected vulnerabilities privately to the repository maintainer through the contact method listed on the maintainer's GitHub profile. Include the affected component, impact, reproduction steps, and any suggested mitigation. Avoid including real secrets or personal data in the report.

## Deployment guidance

This project is an early-stage starter and is not yet hardened for public production use.

- Do not expose the API publicly without authentication and authorisation.
- Use unique, strong credentials and keep the local `.env` file out of version control.
- Restrict direct network access to Redis and PostgreSQL.
- Keep base images and Python dependencies updated.
- Do not place credentials, patient information, or other sensitive data in task payloads.
