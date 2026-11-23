# MCP and chat — contract and UX rules

## Part A — MCP

**Server:** Frappe's built-in MCP server (Frappe ≥ 16.54.0) at `https://<site>/api/v2/mcp`,
Streamable HTTP. Vecto runs no MCP server of its own (ADR-0007). Switch: *System Settings → AI Agents →
Enable MCP*.
**Auth:** Frappe OAuth (turn on Dynamic Client Registration in OAuth Settings) or API key/secret.
Desk users only; every call runs as that user with normal permissions.
**How agents reach Vecto:** through Frappe's 13 generic tools. Vecto actions are whitelisted methods
`vecto.api.<noun>.<verb>`: agents find them with `search_methods`, read arguments and docstring with
`get_method_schema`, and run them with `call_method`. Plain reads use `list_documents` / `get_document`.
**In-app chat:** calls the same functions in-process through `vecto/mcp/registry.py`, which presents them
to the model as named tools (`vecto.api.load.search` ↔ `vecto_load_search`).

### One definition, two doors
Each Vecto tool is one function in `vecto/api/<noun>.py` decorated with `@vecto_tool(...)` from
`vecto/mcp/registry.py`. The decorator:
- whitelists it — `methods=["GET"]` for reads (Frappe's MCP then runs it read-only and rolls back),
  `methods=["POST"]` for writes;
- registers it for the chat agent: name `vecto_<noun>_<verb>`, schema from type hints + docstring,
  annotations (read-only / destructive / idempotent);
- writes a Vecto Tool Call row (source `chat`; `mcp` when the request path is `/api/v2/mcp`; else `api`);
- turns `VectoError` into `{code, message, hint}`.

### Agent Instructions (default text)
Set on install only if *System Settings → AI Agents → Agent Instructions* is empty; never overwritten:

> Vecto (transport management) is installed. For loads, carriers, quotes, tenders, tracking and billing,
> use Vecto methods: `search_methods` with "vecto.api", then `get_method_schema`, then `call_method`.
> Vecto write methods return a preview by default (`dry_run=true`). Show the preview to the user and
> commit only after they confirm, by calling again with `dry_run=false` and a new `idempotency_key`.
> Never change Load status, Load charges or Tracking Events with `create_document`, `update_document`
> or `delete_document`.

### Guards below the tools
No door can bypass these (ADR-0007 §6): lifecycle-owned fields change only through their service;
Tracking Event, Vecto Tool Call, Compliance Snapshot/Event and EDI Message are insert-only; Load money
fields lock at the Billing category. Each guard has a test through `/api/v2/mcp`.

### Tool design rules
1. **Task-shaped, not CRUD.** A method exists for a TMS action with rules (`vecto.api.tender.send`), not
   to repeat `create_document`. Read methods only when they add joins, computed fields or summaries.
2. **Names:** method `vecto.api.<noun>.<verb>`, chat tool `vecto_<noun>_<verb>`; snake_case, stable.
   Renames keep the old name as an alias for one minor release.
3. **Docstrings are prompts.** First line starts with `READ:` or `WRITE:`, then when to use it, when NOT
   to, and what the output means. External agents see only this via `get_method_schema`. Reviewed like UI copy.
4. **Typed arguments** (type hints + Google-style docstring Args). Enums for statuses and modes as
   names validated by category. Dates ISO 8601 with time zone.
5. **Bounded output.** Lists paginate (`limit` ≤ 50, `cursor`). Return IDs + the 5–10 fields a human
   needs, plus a `url` to the record. Never dump whole documents.
6. **Annotations** set in `@vecto_tool` on every tool (used by the chat; external clients see
   `call_method` as destructive).
7. **Writes:** `dry_run: bool = True` → returns a preview (what will change, money impact, who gets
   notified). Commit repeats with `dry_run=False` and an `idempotency_key`.
8. **Errors:** structured `{code, message, hint}` — e.g. `CARRIER_NOT_COMPLIANT` with a hint about what
   fixes it. No stack traces to the client.
9. **Audit:** the decorator writes a Vecto Tool Call row for every call (secrets redacted).
10. **Tests:** each tool has a contract test: schema snapshot, permission denial, dry-run vs commit,
    idempotent replay, and one call through `/api/v2/mcp` `call_method`.

### Tool catalog
Maintained here as tools land.

| Method | Chat tool | R/W | Purpose | Service |
|---|---|---|---|---|
| _(empty — filled per PR)_ | | | | |

## Part B — In-app chat ("Vecto Assistant")

### Runtime
- User message → `vecto.api.chat.send` → enqueues agent run (RQ, `long` queue) → model loop with the
  in-process tool registry → streams tokens and tool events via `frappe.publish_realtime` to the user.
- LLM provider is pluggable (`integrations/llm/`): Anthropic, OpenAI, and any OpenAI-compatible
  endpoint; model chosen in Vecto Settings. Keys stored as Password fields.
- Context sent to the model: system prompt (role, company, user role, today's date and time zone),
  the page/record the user is on, and tool results — not raw database dumps.
- Limits: max tool calls per turn, max tokens per session, per-user daily budget (Settings).
- Safety: tools only within the user's permissions; write tools always preview first; prompt-injection
  hygiene — text from emails, documents and EDI is treated as data, never as instructions.

### UX rules
- **Layout:** left nav · centre workspace (lists, load board, map) · chat as a right-side panel that
  also opens full-screen; global `⌘K` / `Ctrl+K` to ask anything from any page.
- **Context-aware:** chat knows the open record ("tender this load to the usual carrier" works on a
  Load page).
- **Generative UI cards, not walls of text:** tool results render as Load card, Carrier card, Rate
  comparison table, Timeline, Map. Each card links to the record.
- **Confirmation cards for writes:** preview with diff and money impact, buttons Confirm / Edit / Cancel.
- **Show the work:** collapsible "Used 3 tools" row per answer; links to the Tool Call audit.
- **Suggested prompts** per page (e.g. on a Load: "Find 3 carriers for this lane", "Draft rate con").
- **Forms remain first-class.** Everything the chat does is possible by hand; chat is a faster path.
- **Design system:** one token set (colour, spacing, type) shared by SPA and portal; accessible
  contrast; dark mode; responsive down to tablet for dispatch floors and phone for carrier portal.
