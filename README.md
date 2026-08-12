# FinanceIQ

> Most expense trackers guess silently and get things wrong. This one knows when it doesn't know — and asks.

A multi-tenant web app where each user uploads their own bills, and a system of agents decides — case by case — how to parse, categorize and audit them, asking the user directly whenever it isn't confident, instead of following one fixed script.

**Status:** pre-implementation. This repo currently holds the [full project roadmap](./roadmap.md); no application code has been written yet. This README will be reordered to lead with a screenshot and live demo link once Phase 5 (elicitation) lands — see [Part 7 of the roadmap](./roadmap.md#part-7--portfolio-packaging).

**Working name:** BillSense (placeholder).

---

## Why this isn't just an ETL script

A fixed pipeline looks like this:

```
upload → parse → categorize → audit → store
```

Always the same order, always fully automatic, every exception hardcoded in advance. FinanceIQ replaces that with a **decision loop**, reused at three points (parsing, categorizing, auditing):

```
reach a decision point → agent assesses its own confidence
   ├─ high confidence  → act automatically
   ├─ low confidence   → retry with a DIFFERENT approach → reassess
   └─ still uncertain  → ask the user (elicitation) → pause → resume on reply
```

Example: an ambiguous charge like `SQ *MARKET77` doesn't get silently miscategorized — the system asks *"I see a $34 charge from 'SQ \*MARKET77' — is this groceries, or something else?"* and remembers the answer for that vendor going forward.

Full rationale, including the two objections this design resolves (privacy, "is it really agentic?"), is in [Part 1](./roadmap.md#part-1--what-this-is) and [Part 2](./roadmap.md#part-2--the-core-decision-loop-not-pipeline) of the roadmap.

---

## Tech stack

- **Backend:** Python 3.12+, FastAPI, SQLAlchemy + Alembic, `uv` for dependency management
- **Database:** Postgres with row-level security for per-user isolation
- **Agents:** Claude (Claude Code subagents + Agent SDK), MCP for tool access and elicitation
- **Tooling:** pytest, ruff, structlog, Docker Compose, GitHub Actions CI

Full technical decisions and reasoning are in [Part 3](./roadmap.md#part-3--technical-decisions-already-made) of the roadmap.

---

## Planned repo structure

```
├── .claude/            # CLAUDE.md hierarchy, agent definitions, skills
├── mcp-servers/        # finance-data-server — user-scoped tools, elicitation
├── sdk-app/            # the decision loop orchestrator, shared across all 3 agents
├── app/                # FastAPI backend (routers, models, schemas, services, repos)
├── tests/
├── frontend/           # upload, dashboard, and clarify (elicitation) views
├── demo/               # seeded demo account with deliberately ambiguous bills
└── docs/                # architecture notes, ADRs, exam notes
```

See [Part 4](./roadmap.md#part-4--repo-structure) for the full layout with per-file responsibilities.

---

## Non-negotiables

1. No database query runs without a `user_id` scope. Ever.
2. Every agent returns `{result, confidence, reasoning}` — never a bare result.
3. When confidence is low, retry with a *different* approach — not the same call again.
4. When still uncertain after retry, ask the user. Never guess silently, never fail silently.
5. Retries are capped at 2.

---

## Build plan

The project is built in 9 phases (0–8), plus an optional OpenRouter experiment (Phase E), totaling roughly 15–20 evenings of part-time work. The two phases that make this project *agentic* rather than "automated with a fallback error state" are:

- **Phase 4 — retry branch:** a bill that failed on first parse succeeds via a genuinely different retry strategy (e.g. OCR preprocessing), not a hand-tuned prompt.
- **Phase 5 — elicitation:** an ambiguous bill triggers a real question in the UI, the user answers, and the bill completes with no restart.

See [Part 5](./roadmap.md#part-5--build-phases) for the full phase-by-phase breakdown with definitions of done, and [Part 8](./roadmap.md#part-8--the-one-thing-not-to-lose) for why those two phases must never be cut.

---

## License

Apache 2.0 — see [LICENSE](./LICENSE).
