# Security Policy

## Reporting a vulnerability

Please do not disclose security vulnerabilities in public issues. Report suspected vulnerabilities privately through the contact method on the repository maintainer's GitHub profile. Include the affected component, impact, reproduction steps, and suggested mitigation. Do not include real secrets or personal data.

## Deployment guidance

This is an early-stage API/worker starter. Before public use:

- Set a unique API key of at least 32 random characters and rotate it if exposed.
- Use unique database credentials and store all secrets outside Git.
- Put the API behind HTTPS/TLS and rate limiting.
- Restrict Redis and PostgreSQL to the private application network.
- Back up PostgreSQL and test restoration.
- Keep Docker base images and Python dependencies updated.
- Do not submit credentials, patient information, or other sensitive data as task payloads.
- Remember that worker redelivery may execute a task more than once; make side-effecting handlers idempotent.
