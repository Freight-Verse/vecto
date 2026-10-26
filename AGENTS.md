# AGENTS.md — rules for every coding agent in this repo

These rules apply to Cursor, Claude and any other agent. If a task brief conflicts with this file,
stop and ask; do not guess.

## 1. Authorship and review (non-negotiable)
- Commits are authored by the human who drives the agent, in their own git identity. Agents are
  tools, not authors: they never appear as author, co-author or reviewer.
- Never add `Co-authored-by:`, `Reviewed-by:`, `Made-with:`, `Generated-by:` or any other
  attribution trailer to commits, PR titles or PR bodies. Never sign PRs with tool names or links.
- Never change `git config user.name` / `user.email`. Never request reviewers on a PR.
- Agents do not approve or merge. The maintainer (@anupamvs) merges with squash merge.

## 2. What we are building
- Frappe app name: `vecto`. Depends on `frappe` and `erpnext`. Target: **Frappe/ERPNext v16** only (no v15 support).
- Reuse ERPNext masters; do not duplicate them: Customer, Supplier, Address, Contact, Item, UOM,
  Currency, Sales Invoice, Purchase Invoice, Payment Entry, Company, Cost Center.
- Every business capability is exposed through **one service function** and then adapted to
  REST, MCP and UI. See `docs/ARCHITECTURE.md` → "Layers".

## 3. Where code goes
```
vecto/
  vecto/                # module: core TMS doctypes
  carrier/              # module: carrier management & compliance
  rating/               # module: rates, quotes, accessorials
  tracking/             # module: check calls, events, ETA
  billing/              # module: customer invoicing, carrier settlement, audit
  edi/                  # module: X12 204/990/214/210 and API connectors
  agent/                # module: chat, agent runs, tool-call audit
  services/             # business logic — the ONLY place rules live
  mcp/                  # MCP server + tool adapters (thin)
  api/                  # whitelisted REST adapters (thin)
  integrations/         # outbound clients (load boards, tracking, LLM providers)
frontend/               # Vue 3 SPA (workspace + chat), served at /vecto
```

## 4. Hard rules
- Business rules live in `services/`. DocType controllers only call services and validate shape.
  MCP tools and REST endpoints contain **no business logic** — parse input, call service, shape output.
- Every service function checks permissions with `frappe.has_permission` / `frappe.get_list`
  (never `ignore_permissions=True` without a comment explaining why and an ADR reference).
- No raw SQL string concatenation. Use Query Builder (`frappe.qb`) or parameterised `frappe.db.sql`.
- Money: `Currency` fields + explicit currency; never floats for totals in Python — use `flt(x, precision)`.
- Time: store datetimes in system time zone as Frappe does; every Stop carries the facility time zone;
  appointment windows are displayed in the facility's local time.
- Weight/dimensions: always store value + UOM.
- State changes on a Load go through `services/load_lifecycle.py` only (see ARCHITECTURE §4).
- **Never hard-code status names or other configurable vocabulary** (modes, event types, reasons…).
  Rules use the fixed status *category*; everything users can rename lives in a DocType (ADR-0006).
- Writes that come from the chat/MCP path must support `dry_run=True` and accept an `idempotency_key`.
- Secrets: never in code or fixtures. Use Password fields on a Settings DocType or site_config.
- New DocTypes: add `track_changes`, a naming series or meaningful autoname, and proper permissions
  per role (see roles in ARCHITECTURE).
- Patches for every schema/data change that existing sites need. Fixtures only for config, never data.

## 5. Every PR must include
- Link to the issue and the task brief in `docs/tasks/`.
- Tests: `bench --site test_site run-tests --app vecto --module <module>` for services;
  MCP tool contract test for every new or changed tool.
- Updated docs when behaviour, tools, or the data model change (`docs/MCP_AND_CHAT.md` tool catalog).
- Small scope: aim for < 400 changed lines excluding generated DocType JSON. Split otherwise.

## 6. Private material
- `private/` (and `docs/private/`, `*.private.md`) holds internal notes from a separate private
  repository. Never copy, quote, link or summarise anything from it into this repo, issues or PRs.

## 7. When unsure
Stop, write the question in the PR description under "Open questions", and leave the
code path unimplemented rather than inventing behaviour.
