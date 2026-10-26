# ADR-0002: MCP-first with one shared tool registry
Status: Proposed · Date: 2026-10-26 · Decider: Anupam

**Context.** Users should run the TMS through an in-app chat and from external AI clients.
Two tool definitions (one for chat, one for MCP) would drift.

**Decision.** `vecto/mcp/registry.py` defines every tool once (schema, annotations, handler →
service). The MCP endpoint (via `frappe-mcp`, Streamable HTTP, OAuth2) and the in-app agent both
read from it. We wrap `frappe-mcp` because it is experimental and Tools-only today.

**Consequences.** + One contract, tested once. + External agents get exactly what the chat gets.
− Must keep the wrapper thin and track upstream changes.
