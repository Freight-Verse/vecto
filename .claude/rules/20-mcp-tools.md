---
paths:
  - "vecto/mcp/**/*.py"
  - "vecto/api/**/*.py"
  - "vecto/services/**/*.py"
---
# Rules for MCP tools and the shared tool registry

- MCP is served by Frappe's built-in /api/v2/mcp (ADR-0007). Never add an MCP endpoint, transport or the frappe-mcp package.
- A tool = a function in vecto/api/<noun>.py named vecto.api.<noun>.<verb>, decorated with @vecto_tool from vecto/mcp/registry.py. Reads whitelisted for GET only, writes for POST only.
- Tool = thin adapter: validate input → call one service function → shape output. No rules inside.
- Chat tool name: vecto_<noun>_<verb>. Docstring first line starts READ: or WRITE:, then when to use, when not to, what the output means — external agents only see this.
- Typed params with Google-style docstring Args; enums for statuses/modes; ISO 8601 datetimes.
- Set read_only / destructive / idempotent annotations in @vecto_tool.
- Write tools: dry_run (default True) returns a preview; commit requires idempotency_key.
- Output: ids + key fields + url; paginate lists (limit ≤ 50, cursor).
- Errors: {code, message, hint}; no stack traces.
- Add a contract test and a row in docs/MCP_AND_CHAT.md tool catalog for every new tool.
