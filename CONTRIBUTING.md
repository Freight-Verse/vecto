# Contributing to Vecto

Thanks for helping build an open-source, MCP-first TMS on Frappe/ERPNext.

## Before you start
- Read `AGENTS.md` (rules for code — they apply to humans too) and `docs/ARCHITECTURE.md`.
- Pick an issue labelled `agent:ready` or `help wanted`, or open one with the Feature template first.
  Larger changes need a task brief in `docs/tasks/` and, for design changes, an ADR in `docs/adr/`.

## Making a change
1. Fork, then branch: `feat/<issue>-<slug>` or `fix/<issue>-<slug>`.
2. Keep PRs small (< 400 changed lines excluding generated DocType JSON).
3. Business logic in `vecto/services/`; MCP tools and REST endpoints stay thin.
4. Add tests (service + MCP tool contract) and update docs/tool catalog.
5. Open a PR using the template.

## Using AI coding tools
Welcome — with the same rules for everyone:
- You are the author and you are responsible for the code. Commit in your own git identity.
- No agent attribution: no `Co-authored-by:`, `Reviewed-by:`, `Made-with:` or similar trailers,
  and no tool links in PR bodies. Turn off your tool's commit/PR attribution setting. CI rejects them.
- Don't request reviewers; the maintainer handles review and merges with squash merge.

## Review
PRs get automated first-pass review comments, then a maintainer review against the checklist in
`CLAUDE.md`. Address comments with new commits on the same branch.

## Code of conduct
Participation is governed by `CODE_OF_CONDUCT.md`.
