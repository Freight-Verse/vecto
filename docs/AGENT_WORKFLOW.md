# Agent development workflow

## Who does what

| Actor | Role | Author / reviewer of record? |
|---|---|---|
| **Maintainer** (@anupamvs) | Decides scope, accepts ADRs, merges. | Yes — the only one |
| **Contributors** | Humans opening PRs from forks or branches. | Author of their own commits only |
| **Claude** (maintainer's Claude project) | Architect, planner, reviewer: ADRs, task briefs, PR review, fix prompts. | Never |
| **Claude Code** (VS Code extension) | Implementer. One task brief → one branch → one PR. Reads `CLAUDE.md`, which imports `AGENTS.md`. | Never — commits use the human's identity, attribution off |
| **Cursor** (optional, contributors) | Implementer for contributors who prefer it; same rules via `AGENTS.md` + `.cursor/rules/`. | Never |
| **Claude GitHub App** | Automated first-pass review *comments* + `@claude` Q&A. Read-only. | Never — comments only, no approvals |
| **CI** | Lint, tests, migrations check, attribution check. | — |

## The loop
1. **Issue** — The maintainer opens an issue (feature template) or asks Claude to draft one.
2. **Task brief** — Claude writes `docs/tasks/NNNN-slug.md` from `TEMPLATE.md`: scope, files,
   service signatures, tool contracts, acceptance criteria, tests, out-of-scope list.
   If it needs a design decision, Claude writes an ADR first and waits for the maintainer.
3. **Implement** — In Claude Code (VS Code): new branch `feat/NNNN-slug` from `develop`, prompt:
   `Implement docs/tasks/NNNN-slug.md. Follow AGENTS.md. Plan first, then implement, then run tests.`
   Use plan mode for anything touching more than one module; approve the plan before it edits files.
4. **PR** — Claude Code opens the PR using the template (`gh pr create`). CI runs.
5. **First-pass review** — Claude GitHub action reviews the PR automatically (inline comments).
6. **Architecture review** — The maintainer asks Claude: "Review PR #N". Claude reviews against the
   `docs/REVIEW_CHECKLIST.md` and returns a verdict plus a "Fix prompt". The reviewing session is never the
   session that wrote the code.
7. **Fix** — Paste the fix prompt into Claude Code on the same branch. Repeat 5–7 until READY TO MERGE.
8. **Merge** — The maintainer squash-merges into `develop`.
9. **Release** — When a version is ready, the maintainer opens `develop` → `main` and merges it.

Rule of thumb: Claude decides *what and why*, Claude Code decides *how within the brief*, the maintainer decides *whether*.

## Authorship and reviewers — humans only
- **Git identity:** each human sets their own `user.name` / `user.email`. The maintainer's machine
  (where Claude Code runs) uses the maintainer's identity, repo-level and global.
- **No agent attribution anywhere:** no `Co-authored-by:`, `Reviewed-by:`, `Made-with:`,
  `Generated-by:` trailers; no tool links in PR bodies.
- **Claude Code:** the committed `.claude/settings.json` sets `"attribution": {"commit": "", "pr": "",
  "sessionUrl": false}`, which removes the `Co-Authored-By` trailer, the PR line and the session link.
  Don't override it in `.claude/settings.local.json` or `~/.claude/settings.json`.
- **Cursor** (contributors): Cursor Settings → Git & Pull Requests → turn **off** "Commit Attribution"
  and "PR Attribution"; for Cursor CLI set `attribution.attributeCommitsToAgent: false` in
  `~/.cursor/cli-config.json`.
- Settings can be missed, so two backstops:
  - **Local:** a `commit-msg` git hook that strips those trailers.
  - **CI:** a check that fails the PR if any commit carries an attribution trailer or a bot author.
- **No reviewers requested:** no CODEOWNERS file, no auto-assigned reviewers, no team review
  requests, no "required approvals" rule (the maintainer can't approve their own PR).
- **Claude GitHub App:** review workflow posts comments only (`contents: read`,
  `pull-requests: read` + inline-comment tool). Don't use `@claude` to push commits — those commits
  would be authored by the bot.
- **Squash merge only** into `develop`, so every commit there is authored by the PR's human author and merged
  by the maintainer.

## GitHub setup checklist
- [x] Public repo `Freight-Verse/vecto` (open source).
- [ ] Default branch: `develop` (Settings → General → Default branch).
- [ ] Squash merge only; auto-delete head branches.
- [ ] Branch protection on `develop` and `main`: require PR, require status checks (CI + attribution check, once
      CI exists), require linear history, block force-push, approvals not required.
- [ ] Claude GitHub App installed on the org; add the review workflow (`anthropics/claude-code-action@v1`
      with the `code-review` plugin) and secret `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN`.
      Public-repo note: GitHub withholds secrets from fork PRs, so automated review runs on
      same-repo branches; fork PRs get the maintainer's manual Claude review.
- [ ] Only users with write access can trigger `@claude` (the action enforces this).
- [ ] CI workflow: ruff + eslint/prettier, `bench run-tests --app vecto`, `bench migrate` on a
      fresh site, attribution check.
- [x] Labels, milestones and seed issues (from `docs/GITHUB_PLAN.md`).
- [ ] Project board "Vecto Roadmap" (create in GitHub UI: Projects → New → Board; add repo issues).

## Claude Code setup checklist (VS Code)
- [ ] Install the Claude Code extension; open the repo root (the bench app folder) as the workspace.
  It loads `CLAUDE.md` (which imports `AGENTS.md`), `.claude/settings.json` and `.claude/rules/`.
- [ ] Check attribution is off: make a test commit on a scratch branch and confirm no trailer.
- [ ] Install the `commit-msg` hook backstop.
- [ ] Connect the dev site's Frappe MCP server in **local** scope (never committed):
      `claude mcp add --transport http vecto-dev https://<dev-site>/api/v2/mcp`, then authenticate via
      OAuth from `/mcp`, or add `--header "Authorization: token <api_key>:<api_secret>"`.
- [ ] `gh` CLI logged in as the maintainer, so PRs are opened in their name.

Contributors using Cursor: open the repo; Cursor reads `AGENTS.md` and `.cursor/rules/`. Keep
`.cursor/rules/` in sync with `.claude/rules/` (the canonical copy).

## Cadence
- One PR per task brief; target 1–2 days of work each.
- Weekly: Claude reviews `docs/ARCHITECTURE.md` against what was merged and proposes ADR updates.
- Every phase end: Claude runs a full architecture and security review of `develop`.
