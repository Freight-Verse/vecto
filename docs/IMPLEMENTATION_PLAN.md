# Vecto implementation plan

Status: Proposed (2026-11-07). The **order** of work. `docs/GITHUB_PLAN.md` lists the issues; this file
says what is built in which sequence. One row = one task brief in `docs/tasks/` = one PR.

**Re-cut needed (2026-11-23):** `develop` already holds Phase 1–2 code under the names in
`docs/PHASE_SPEC.md`, so briefs 0001–0003 overlap it. Next briefs start from the "Known Gaps" list there
(status category + lifecycle service + guards first), then continue with 0004–0008 below.

**Open decision that blocks work:** ADR-0004 (frontend stack). MCP: Frappe's built-in server only (ADR-0007, accepted).

## M0 Foundation

| Brief | Title | Depends on | Delivers | Brief status |
|---|---|---|---|---|
| 0001 | App skeleton, roles, settings, base masters | — | `vecto` installs on Frappe ≥ 16.54 + ERPNext v16 | written |
| 0002 | Load data model + configurable statuses | 0001 | Shipment Order, Load, stops, commodities, charges | written |
| 0003 | Configurable load lifecycle | 0002 | `services/load_lifecycle.py`, transitions, Tracking Event | written |
| 0004 | CI and repo guardrails | 0001 | ruff, eslint, `run-tests`, `migrate` on fresh site, attribution check | to write |
| 0005 | Tool registry + first Vecto methods | 0002 | `@vecto_tool` decorator, Vecto Tool Call audit, `vecto.api.load.search` / `.get`, contract tests incl. via `/api/v2/mcp` | to write |
| 0006 | Write-tool framework | 0003, 0005 | `dry_run` previews, idempotency key store, first write method `vecto.api.load.transition` | to write |
| 0007 | Built-in MCP guards and agent setup | 0005 | Agent Instructions default, insert-only event/audit DocTypes, bypass tests through `/api/v2/mcp`, "Connect an AI client" doc | to write |
| 0008 | SPA shell + design system at `/vecto` | ADR-0004 | tokens, layout (nav · workspace · chat panel), auth, routing | to write |

0004 can run in parallel with 0002–0003. 0008 can run in parallel with 0005–0007 once ADR-0004 is accepted.

**M0 exit check.** In Claude Desktop connected to the site's `/api/v2/mcp`: find and call Vecto methods
(search, get); move a load with preview → confirm; a direct `update_document` on `Load.status` is rejected;
every Vecto call has an audit row.

## M1 MVP broker flow — build order

Each epic follows the same recipe: **service → `@vecto_tool` method in `vecto/api/` → Desk/SPA screen →
tests → tool catalog row** in `docs/MCP_AND_CHAT.md`.

1. **Chat backend** — sessions, agent run on RQ, LLM provider adapter, streaming. Starts after 0006 and
   runs alongside the domain epics; each new tool is available in chat the day it lands.
2. **Carriers + regional compliance (FMCSA)** — first, because tendering and dispatch gate on it.
3. **Rating & quotes** — lanes, rate cards, FSC, quote → order.
4. **Tendering** — email tender, accept/reject, expiry, waterfall; compliance gate.
5. **Dispatch** — assign carrier/driver/equipment, rate confirmation, load board view.
6. **Tracking** — check calls, ETA, exceptions, timeline.
7. **Documents** — BOL/POD, required documents per customer.
8. **Billing** — Sales Invoice, Purchase Invoice, per-load margin.
9. **Chat UI** — panel, ⌘K, result cards, ConfirmCard; grows with each epic once 0008 lands.
10. **End-to-end acceptance** — full broker flow via forms, via chat, and via Claude Desktop on
    `/api/v2/mcp`, plus the bypass checks.

## Notes
- Brief numbers here and in `docs/GITHUB_PLAN.md` match (renumbered 2026-11-07).
- If task 0001 is already implemented, remove the `enable_mcp` field from Vecto Settings in task 0005 (Frappe's switch replaces it).
