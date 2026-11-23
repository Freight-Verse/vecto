# CLAUDE.md — Claude Code in Vecto

@AGENTS.md

The rules in AGENTS.md (imported above) are hard rules. They win over this file and over any task brief;
if they conflict, stop and ask.

## Your job: implement task briefs
One brief in `docs/tasks/` → one branch `feat/NNNN-<slug>` from `develop` → one PR into `develop`.
1. Read the brief and every doc it links. No brief → ask for one; don't start.
2. **Plan first:** list the files you will touch, the service functions, the `vecto.api` methods and the
   tests. For anything touching more than one module, wait for Anupam's OK on the plan.
3. Implement only what the brief asks. Anything else goes under "Open questions" in the PR description.
4. Run the tests (commands below) and paste the summary in the PR.
5. Update the docs the brief names — usually the tool catalog in `docs/MCP_AND_CHAT.md`.
6. Open the PR with `.github/pull_request_template.md`. Don't merge, approve or request reviewers.

## Names and field specs
DocType names and field specs come from `docs/PHASE_SPEC.md`. Code uses the names in its
"Name Mapping" table (Load Order, Shipper, TMS Location, TMS Settings…), even where a task brief or issue
uses the older names (Load, Customer, Facility, Vecto Settings). Its "Known Gaps" list is the current
debt; don't widen it.

## Not your decisions
Don't edit `docs/ARCHITECTURE.md`, `docs/adr/`, `docs/tasks/`, `docs/PHASE_SPEC.md` or the rules in `docs/MCP_AND_CHAT.md`
(adding tool catalog rows is fine). If the brief leaves a design decision open, stop and ask —
leave the code path unimplemented rather than inventing behaviour (AGENTS.md §7).

## Authorship
- `.claude/settings.json` turns off commit and PR attribution. Don't re-enable it in local settings.
- Commit with the git identity already configured; never change git config.

## MCP
Vecto runs no MCP server; Frappe's built-in `/api/v2/mcp` serves it (ADR-0007). Vecto actions are
`@vecto_tool` methods in `vecto/api/`. If the dev site's MCP is connected to this session, use it to
try the methods you build.

## Reviews
Asked to review a PR? Use a fresh session (not the one that wrote the code) and follow
`docs/REVIEW_CHECKLIST.md`.

## Commands
Run from the bench root (`~/develop/frappe-v16/`); local site `localhost.v16`.
- Tests: `bench --site localhost.v16 run-tests --app vecto` (or `--module <module>`)
- Schema/data changes: `bench --site localhost.v16 migrate`
- Fixtures (roles, workspace only): `bench --site localhost.v16 export-fixtures --app vecto`
- Lint: `ruff check vecto && ruff format --check vecto`

## Scoped rules
`.claude/rules/` loads extra rules by path: backend (`vecto/**/*.py`), tools (`vecto/api`, `vecto/mcp`,
`vecto/services`), frontend (`frontend/`), tests.
