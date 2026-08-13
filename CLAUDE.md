# Backend conventions

## Tech stack

Python 3.12+, `uv`, FastAPI, SQLAlchemy 2.0 (async) + Alembic, Postgres, pydantic-settings, structlog, pytest, ruff, Docker Compose.

## Layering

Requests flow in one direction only:

```
routers -> services -> repos -> database
```

- `routers` — HTTP only. Request/response validation and delegation to services. No business logic.
- `services` — business logic. Never touch the database directly; call repos instead.
- `repos` — the only layer that talks to the database.
- `models` — SQLAlchemy ORM classes.
- `schemas` — pydantic request/response models.

## Configuration

All configuration goes through `app/config.py` (pydantic-settings). Never scatter `os.getenv` calls elsewhere in the codebase.

## Logging

Structured logging via `structlog` only. Never use bare `print`.

## Type hints

Type hints are required on all function signatures.

## Tests

Tests live in `/tests`, mirroring the `app/` structure.
