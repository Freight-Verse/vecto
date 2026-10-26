# MCP and chat — contract and UX rules

## Part A — MCP server

**Endpoint:** `/api/method/vecto.mcp.handle_mcp` (Streamable HTTP).
**Library:** `frappe-mcp` (official, Frappe org). It is marked experimental and supports Tools only
(no Resources/Prompts yet) — so all our tools go through `vecto/mcp/registry.py`, a thin wrapper we
own. If the library breaks, only the wrapper changes. See ADR-0002.
**Auth:** Frappe OAuth2 (needs a Frappe version with the OAuth2 update for MCP clients); API key/secret
for server-to-server. Never `allow_guest` in production. Tools run as the authenticated user.

### Tool design rules
1. **Task-shaped, not CRUD.** `vecto_tender_send(load, carrier, rate)` beats generic
   `create_doc("Tender", …)`. Generic `vecto_search` / `vecto_get` are allowed for reads only.
2. **Names:** `vecto_<noun>_<verb>`, snake_case, stable. Renames need a deprecation alias.
3. **Descriptions are prompts.** The docstring says when to use the tool, when NOT to, and what
   the output means. Reviewed like UI copy.
4. **Typed input schema** (type hints + Google-style docstrings → generated schema). Enums for
   statuses and modes. Dates ISO 8601 with time zone.
5. **Bounded output.** Lists paginate (`limit` ≤ 50, `cursor`). Return IDs + the 5–10 fields a
   human needs, plus a `url` to the record. Never dump whole documents.
6. **Annotations:** set `readOnlyHint`, `destructiveHint`, `idempotentHint` on every tool.
7. **Writes:** `dry_run: bool = True` by default from chat → returns a preview (what will change,
   money impact, who gets notified). Commit call repeats with `dry_run=False` and an
   `idempotency_key`.
8. **Errors:** structured `{code, message, hint}` — e.g. `CARRIER_NOT_COMPLIANT` with a hint
   about what fixes it. No stack traces to the client.
9. **Audit:** the registry writes a Vecto Tool Call row for every call (args redacted for secrets).
10. **Tests:** each tool has a contract test: schema snapshot, permission denial, dry-run vs commit,
    idempotent replay.

### Tool catalog
Maintained here as tools land. Format: `name` — R/W — one-line purpose — service function.

| Tool | R/W | Purpose | Service |
|---|---|---|---|
| _(empty — filled per PR)_ | | | |

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
