# ADR-0007: Use Frappe's built-in MCP server; no Vecto MCP endpoint
Status: **Accepted** (2026-11-07) · Proposed: 2026-11-07 · Decider: Anupam · Amends ADR-0002

**Context.**
Frappe v16.53.0 (2026-10-22) ships a built-in MCP server; v16.54.0 makes *System Settings → AI Agents
→ Enable MCP* its only switch. Read from the v16.54.0 source:
- Endpoint `/api/v2/mcp`, Streamable HTTP with JSON responses; MCP protocol 2025-11-25 and 2026-07-28.
  Auth: OAuth (dynamic client registration), API key/secret, session. **Desk users only.**
- 13 fixed generic tools: `search_doctypes`, `get_doctype_schema`, `search_methods`, `get_method_schema`,
  `list_document_methods`, `list_documents`, `get_document`, `count_documents`, `create_document`,
  `update_document`, `delete_document`, `call_method`, `call_document_method`. Apps cannot add tools.
- Any whitelisted method is reachable through `search_methods` → `get_method_schema` → `call_method`.
  A method whitelisted for GET only is run read-only (database writes rolled back).
- A site-wide *Agent Instructions* text is appended to the instructions sent to every client.

ADR-0002 chose the `frappe-mcp` library (v0.1.0, July 2025, Tools-only) for a Vecto endpoint.

**Decision.**
1. **Minimum Frappe 16.54.0** (ERPNext v16), pinned in `pyproject.toml` `[tool.bench.frappe-dependencies]`.
2. **MCP is served only by Frappe's built-in `/api/v2/mcp`.** Vecto runs no MCP endpoint and does not
   depend on `frappe-mcp`.
3. **Vecto actions are whitelisted methods** in `vecto/api/<noun>.py`, named `vecto.api.<noun>.<verb>`.
   Reads are whitelisted for GET only, writes for POST only. Each method is a thin adapter over one
   service function, with an LLM-quality docstring (it is what agents read via `get_method_schema`).
4. **One definition for both doors.** A `@vecto_tool(...)` decorator in `vecto/mcp/registry.py`
   whitelists the method, registers it for the in-app chat as a named tool (`vecto_<noun>_<verb>`, with
   schema and annotations), writes the Vecto Tool Call audit row, and maps errors to `{code, message, hint}`.
   The chat calls the registry in-process; external agents call the same functions via `call_method`.
5. **Plain reads use Frappe's generic tools** (`list_documents`, `get_document`). Vecto adds a read
   method only where it adds value (joins, computed fields, summaries such as a load timeline).
6. **Invariants are enforced below the tools**, so no path can bypass them:
   - Lifecycle-owned fields (`Load.status` and later others) change only through their service
     (controller flag pattern from task 0003).
   - Event and audit DocTypes — Tracking Event, Vecto Tool Call, Compliance Snapshot/Event, EDI Message —
     are insert-only (no write/delete permission for any role; corrections are new rows).
   - Money fields on a Load lock once it reaches the Billing category.
   - Tests prove `create_document` / `update_document` / `delete_document` through `/api/v2/mcp`
     are rejected for these.
7. **Agent Instructions.** On install (and by patch) Vecto sets a default text in System Settings if it
   is empty, never overwriting an admin's text. Wording lives in `docs/MCP_AND_CHAT.md`.
8. **Confirm-before-write (ADR-0003).** Write methods default to `dry_run=True` on every path. The chat
   shows a confirmation card; external clients get the preview and must call again with `dry_run=False`
   and an `idempotency_key`, behind their own approval prompt (`call_method` is marked destructive).
9. **Portal users** (Carrier, Customer) have no MCP access, because Frappe's server is Desk-only.
   Portals use the SPA and REST. Revisit in the M2 portal epic if needed.
10. **Revisit** if Frappe adds app-registered tools: the registry could then publish named `vecto_*`
    tools to `/api/v2/mcp` directly. Services and methods stay unchanged.

**Consequences.**
+ No MCP server or transport code to own; protocol upgrades come with Frappe.
+ ERPNext and Vecto are available to agents through one connection.
+ Guards in controllers also protect Desk and REST.
− External agents see Vecto actions through `call_method` (one generic, destructive-marked tool),
  so docstrings and Agent Instructions carry the guidance.
− No per-tool annotations for external clients; no MCP access for portal users.
