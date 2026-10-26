# Vecto

Vecto is an open-source Transportation Management System built as a Frappe app (`vecto`) on top of
ERPNext, for brokers, shippers, carriers and 3PLs. It is **MCP-first**: every capability is an MCP
tool, and a built-in **chat prompt** lets users run the TMS by conversation as well as by forms.

Status: design phase — see the [milestones](../../milestones) and `docs/FEATURE_MAP.md`.
Vecto is built by FreightVerse. Maintainer: Anupam Kumar (@anupamvs). Contributions welcome — see `CONTRIBUTING.md`.

## Read in this order

| File | What it is | Who reads it |
|---|---|---|
| `AGENTS.md` | Hard rules for every coding agent | Cursor, Claude, GitHub reviewer |
| `CLAUDE.md` | Claude's role: architect + reviewer, review checklist | Claude |
| `.cursor/rules/*.mdc` | Scoped rules Cursor loads by file type | Cursor |
| `docs/ARCHITECTURE.md` | System design, layers, data model | Everyone |
| `docs/FEATURE_MAP.md` | Feature scope + phased roadmap | Everyone |
| `docs/GITHUB_PLAN.md` | Labels, milestones, board and seed issues | Maintainer |
| `docs/MCP_AND_CHAT.md` | MCP tool contract rules + chat UI spec | Everyone |
| `docs/AGENT_WORKFLOW.md` | How Claude, Cursor and GitHub review work together | Maintainer |
| `docs/integrations/` | Integration specs (carrier compliance, …) | Everyone |
| `docs/API_STANDARDS.md` | REST, MCP, webhook rules | Everyone |
| `docs/COMMUNITY.md` | How we grow contributors and users | Everyone |
| `docs/BRAND.md` | FreightVerse and Vecto brand, light/dark design tokens | Everyone |
| `docs/adr/` | Architecture decisions (why, not just what) | Everyone |
| `docs/tasks/` | Task briefs Claude writes for Cursor, one per PR | Cursor |

## The loop in one line

Issue → task brief → implementation on a branch → CI → automated first-pass review comments
→ architecture review → fixes → maintainer squash-merges.

## Contributing, security, license
- `CONTRIBUTING.md` — how to propose and build features (with or without AI agents)
- `SECURITY.md` — report vulnerabilities privately
- License: to be chosen before the first code release (tracked in an M0 issue)
