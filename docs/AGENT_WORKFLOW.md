# Agent development workflow

## Who does what

| Actor | Role | Author / reviewer of record? |
|---|---|---|
| **Maintainer** (@anupamvs) | Decides scope, accepts ADRs, merges. | Yes — the only one |
| **Contributors** | Humans opening PRs from forks or branches. | Author of their own commits only |
| **Claude** (maintainer's workspace) | Architect, planner, reviewer: ADRs, task briefs, PR review, fix prompts for Cursor. | Never |
| **Cursor** (Agent mode) | Implementer. One task brief → one branch → one PR. | Never — commits use the human's identity, attribution off |
| **Claude GitHub App** | Automated first-pass review *comments* + `@claude` Q&A. Read-only. | Never — comments only, no approvals |
| **CI** | Lint, tests, migrations check, attribution check. | — |

## The loop
1. **Issue** — The maintainer opens an issue (feature template) or asks Claude to draft one.
2. **Task brief** — Claude writes `docs/tasks/NNNN-slug.md` from `TEMPLATE.md`: scope, files,
   service signatures, tool contracts, acceptance criteria, tests, out-of-scope list.
   If it needs a design decision, Claude writes an ADR first and waits for the maintainer.
3. **Implement** — In Cursor: new branch `feat/NNNN-slug`, prompt:
   `Implement docs/tasks/NNNN-slug.md. Follow AGENTS.md. Plan first, then implement, then run tests.`
   Use Cursor's plan mode for anything touching more than one module.
4. **PR** — Cursor opens the PR using the template. CI runs.
5. **First-pass review** — Claude GitHub action reviews the PR automatically (inline comments).
6. **Architecture review** — The maintainer asks Claude: "Review PR #N". Claude reviews against the
   CLAUDE.md checklist and returns a verdict plus a "Fix prompt for Cursor".
7. **Fix** — Paste the fix prompt into Cursor on the same branch. Repeat 5–7 until READY TO MERGE.
8. **Merge** — The maintainer squash-merges.

Rule of thumb: Claude decides *what and why*, Cursor decides *how within the brief*, the maintainer decides *whether*.

## Authorship and reviewers — humans only
- **Git identity:** each human sets their own `user.name` / `user.email`. The maintainer's machine
  (where Cursor runs) uses the maintainer's identity, repo-level and global.
- **No agent attribution anywhere:** no `Co-authored-by:`, `Reviewed-by:`, `Made-with:`,
  `Generated-by:` trailers; no tool links in PR bodies.
- **Cursor:** Cursor Settings → Git & Pull Requests → turn **off** "Commit Attribution" and
  "PR Attribution". For Cursor CLI, set `attribution.attributeCommitsToAgent: false` in
  `~/.cursor/cli-config.json`. Cursor has acknowledged the trailer can still appear on some
  non-IDE paths, so two backstops:
  - **Local:** a `commit-msg` git hook that strips those trailers.
  - **CI:** a check that fails the PR if any commit carries an attribution trailer or a bot author.
- **No reviewers requested:** no CODEOWNERS file, no auto-assigned reviewers, no team review
  requests, no "required approvals" rule (the maintainer can't approve their own PR).
- **Claude GitHub App:** review workflow posts comments only (`contents: read`,
  `pull-requests: read` + inline-comment tool). Don't use `@claude` to push commits — those commits
  would be authored by the bot.
- **Squash merge only** so every commit on `main` is authored by the PR's human author and merged
  by the maintainer.

## GitHub setup checklist
- [x] Public repo `Freight-Verse/vecto` (open source).
- [ ] Squash merge only; auto-delete head branches.
- [ ] Branch protection on `main`: require PR, require status checks (CI + attribution check, once
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

## Cursor setup checklist
- [ ] Open the repo root in Cursor; it loads `AGENTS.md` and `.cursor/rules/*.mdc` automatically.
- [ ] Add the Frappe docs (frappeframework.com/docs, docs.erpnext.com) under Settings → Indexing & Docs.
- [ ] Connect the dev site's Vecto MCP server to Cursor once it exists, so Cursor can test tools live.
- [ ] Turn off commit/PR attribution (above).

## Cadence
- One PR per task brief; target 1–2 days of work each.
- Weekly: Claude reviews `docs/ARCHITECTURE.md` against what was merged and proposes ADR updates.
- Every phase end: Claude runs a full architecture and security review of `main`.
