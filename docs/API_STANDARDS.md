# API standards

Benchmark: the best public developer platforms in logistics and fleet software. Rule: **no capability exists without an API, and no API is paywalled.**

1. **Three surfaces, one service layer:** REST (`/api/v1/vecto/...` versioned resources on top of
   Frappe's REST), MCP tools, and webhooks — all calling the same `services/` functions.
2. **OpenAPI 3.1 spec** generated from the service signatures; published docs site + Postman collection.
3. **Auth:** OAuth2 (Frappe) for apps and MCP clients; API key/secret for server-to-server;
   **scoped tokens** (e.g. `loads:read`, `tenders:write`) mapped to Frappe roles.
4. **Consistency:** JSON envelope `{data, pagination: {next_cursor, has_more}}`, cursor pagination,
   ISO 8601 datetimes with zone, money as `{amount, currency}`, weights as `{value, uom}`.
5. **Writes:** `Idempotency-Key` header; `dry_run` on every write; structured errors `{code, message, hint}`.
6. **Webhooks:** event catalog (`load.status_changed`, `tender.accepted`, `tracking.event_added`,
   `compliance.changed`, `invoice.created`…), HMAC-signed payloads, retries with backoff, delivery log,
   replay from the UI.
7. **Rate limits** documented and returned in headers; per-token quotas configurable by the site owner.
8. **Versioning:** additive changes in place; breaking changes only in a new version with a deprecation
   window; public changelog.
9. **Sandbox:** demo site with sample data and test credentials for integrators.
10. **SDKs:** TypeScript and Python clients generated from the OpenAPI spec.
11. **Bulk:** import/export jobs (CSV/JSON) with status and error reports; full data export always available.
12. **Standards:** EDI X12 (204/990/214/210) for North America and EDIFACT for Europe, mapped to the same events.
13. **Role-specific API views:** the same API, documented separately for the operating company, its customers and its carriers/subcontractors, each limited by role.
