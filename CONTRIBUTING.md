# Contributing

Thank you for considering a contribution.

## Before you start

- Search existing issues and pull requests to avoid duplicate work.
- For substantial changes, open an issue first to discuss the proposed approach.
- Never include credentials, access tokens, personal data, or production data in commits or test fixtures.

## Development setup

1. Fork and clone the repository.
2. Create and activate a Python 3.11 virtual environment.
3. Install dependencies with `python -m pip install -r requirements.txt`.
4. Run the unit tests from the repository root with `python -m pytest -q`.

## Pull requests

- Keep changes focused and explain the problem they solve.
- Add or update tests for behaviour changes.
- Update documentation when commands, configuration, or API behaviour changes.
- Confirm tests pass locally before opening a pull request.
- Include a concise summary and any relevant limitations.

## Code expectations

- Prefer small, readable functions.
- Validate task input and return JSON-serialisable results.
- Keep pure task logic separate from database and Celery integration.
- Do not introduce breaking API changes without documenting them.
