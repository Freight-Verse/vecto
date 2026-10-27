# ADR-0003: Dry-run preview and confirmation for agent writes
Status: **Accepted** (2026-10-28) · Proposed: 2026-10-26 · Decider: Anupam

**Decision.** Write tools default to `dry_run=True` from chat; the UI shows a confirmation card;
commit requires `dry_run=False` + `idempotency_key`. Background agents may auto-commit only actions
listed in an allow-list in Vecto Settings (e.g. "log check call from ELD ping").

**Consequences.** + Safe by default, auditable. − One extra round trip on writes.
