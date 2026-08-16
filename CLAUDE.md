# FinanceIQ

## Project identity

FinanceIQ is a multi-tenant bill-tracking app where a system of agents decides — case by case — how to parse, categorize, and audit each bill, asking the user directly whenever it isn't confident, instead of following one fixed script. It is **not** a fixed pipeline (`upload → parse → categorize → audit → store`, always in that order, always automatic).

Any change that removes a decision point and replaces it with hardcoded sequencing is a regression, regardless of whether tests pass.

## Non-negotiables

1. No database query runs without a `user_id` scope. Ever.
2. Every agent returns `{result, confidence, reasoning}` — never a bare result.
3. When confidence is low, retry with a *different* approach — not the same call again.
4. When still uncertain after retry, ask the user. Never guess silently, never fail silently.
5. Retries are capped at 2.

## Tech stack

Python 3.11+, `uv` for deps, FastAPI, SQLAlchemy 2.0 (async) + Alembic, Postgres with row-level security, pydantic-settings, structlog, pytest, ruff, Docker Compose.

## Conventions

- Formatting and linting is `ruff` — don't hand-format.
- Structured logging via `structlog`, never bare `print`.
- Config comes from `app/config.py` (pydantic-settings), never `os.getenv` scattered in code.
- Type hints required on all function signatures.
- Tests live in `/tests`, mirroring the `app/` structure.

## Vocabulary

- **Bill** — one uploaded document belonging to one user.
- **Decision point** — a place where an agent assesses confidence and branches.
- **Elicitation** — pausing to ask the user a question, then resuming.
- **Flagged** — surfaced for human attention, distinct from *pending* (awaiting an elicitation answer).

## Build phases

Full detail and Definition-of-Done for each phase lives in `roadmap.md` — this is just the map. Don't skip ahead: each phase's DoD must actually be true before the next one starts.

0. **Scaffolding** — runnable skeleton: `uv`, Docker Compose (api+db+adminer), ruff, pre-commit, CI, `/health` with a real DB check.
1. **Auth and data model** — `users`/`bills`/`categories`/`flags` schema, JWT auth, Postgres row-level security, automated cross-user isolation test.
2. **Upload and happy-path parse** — one clean bill in, structured data out. No decision-making yet — this is the baseline.
3. **Confidence scoring** — parser returns `{result, confidence, reasoning}`; labeled test set of 5-10 varied bills.
4. **Decision loop: retry branch** — parser becomes a real subagent; orchestrator branches on confidence and retries with a genuinely different approach, capped at 2.
5. **Elicitation: ask the user** — MCP server with elicitation; real pause/resume (no restart); `clarify.html` for pending questions. The branch that makes this agentic, not automated-with-a-fallback.
6. **Categorizer and auditor** — same loop reused for two more agents; decision loop refactored into one shared function called by all three.
7. **Dashboard and demo seeding** — recruiter-facing dashboard; seeded demo account with deliberately ambiguous bills so elicitation visibly triggers.
8. **Deploy and package** — hosted demo, case study, README reordered outcome-first.

Optional **Phase E — OpenRouter experiment**: time-boxed, only after phases 0-8 are done and working on Claude, on a separate branch.

**If time runs short: cut phase 7's chart or phase 8's polish before ever cutting phase 4 or 5.** Phases 0-3 produce a working but non-agentic app — it will feel like progress and tempt you to stop there. Phases 4 and 5 are the actual project.
