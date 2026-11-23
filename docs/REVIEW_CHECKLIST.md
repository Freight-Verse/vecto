# PR review checklist

Used for every architecture review before Anupam merges. Run it in a **fresh** session — never in the
session that wrote the code. On GitHub, post review *comments* only: never submit an "Approve" or
"Request changes" state and never request reviewers (AGENTS.md §1).

## Blocking (apply in order; stop at the first blocking failure)
- [ ] Matches the task brief scope; no unrequested features or refactors.
- [ ] Business logic only in `services/`; whitelisted methods, `@vecto_tool` functions and controllers are thin.
- [ ] Permissions enforced in services; no unexplained `ignore_permissions`.
- [ ] Load status changes only through the lifecycle service; illegal transitions rejected.
- [ ] No hard-coded status names or configurable vocabulary; rules use status categories (ADR-0006).
- [ ] Money, time zone and UOM rules from AGENTS.md followed.
- [ ] Write methods support `dry_run` (default True) and `idempotency_key`; reads whitelisted for GET only.
- [ ] Guards hold through Frappe's `/api/v2/mcp` generic tools (ADR-0007 §6).
- [ ] No MCP endpoint, transport or `frappe-mcp` dependency added (ADR-0007).
- [ ] No secrets, no raw string SQL, no N+1 queries in list endpoints.
- [ ] Tests exist and cover the failure paths, not only the happy path.
- [ ] Patches present for schema/data changes.
- [ ] No agent attribution trailers in commits or PR body; commit author is a human.

## Non-blocking (comment, don't hold the PR)
- Naming, readability; docstrings on tools (they are what agents read through `get_method_schema`).
- UI consistency with the design rules in `docs/MCP_AND_CHAT.md`.
- Opportunities to delete code.

## Output format
- Verdict: `READY TO MERGE` / `CHANGES NEEDED` / `NEEDS DECISION` (escalate to Anupam).
- Findings: file:line — problem — concrete fix. Most severe first.
- A short "Fix prompt" block Anupam can paste into the Claude Code session on the PR branch.
