# ADR-0006: Configurable statuses, transitions and master data
Status: Proposed · Date: 2026-10-26 · Decider: Anupam

**Context.** Every broker, carrier and shipper names and orders their load stages differently, and
needs different required steps. Hard-coded statuses force forks. Frappe CRM (Deal Status with a fixed
`type`) and Helpdesk (Ticket Status with a fixed `category` and separate agent/customer labels) solve
this the same way: users own the labels; code depends only on a small fixed set of categories.

**Decision.**
1. **Status = data.** `Load Status` DocType: label, color, order, enabled, **category** (fixed list,
   below), customer-facing label, carrier-facing label, optional EDI 214 code, probability/progress %.
2. **Code only knows categories**, never status names:
   `Draft · Planning · Tendering · Covered · Dispatched · In Transit · Delivered · Billing · Closed · Cancelled`.
   Business rules (e.g. "can't invoice before Delivered", "compliance gate before Covered") are written
   against categories. Each category ships with default statuses; companies rename, add, hide and reorder.
3. **Transitions = data.** `Load Status Transition`: from status → to status, allowed roles, required
   fields, required documents, condition (safe expression), auto-actions (notify, EDI out, tracking event).
   The lifecycle service validates against these rows plus fixed category-order guards (no skipping
   from Draft to Billing). A default transition set ships with the app.
4. **Scope.** Statuses and transitions can vary by **mode** (FTL, LTL, drayage…) and optionally by
   customer; resolution order: customer → mode → default.
5. **Same pattern for the rest of the domain vocabulary** (all DocTypes, editable in the Settings UI):
   modes, equipment types, stop types, reference types (PO, PRO, BOL…), accessorials (ERPNext Items),
   tracking event types, exception types and reason codes, cancel/reject/TONU reasons, document types
   and per-customer document requirements, tender methods and expiry defaults, compliance policies
   (ADR-0005), naming series, notification rules, list/kanban saved views, form field layouts
   (like Frappe CRM's layout editor), chat suggested prompts.
6. **Custom fields** use Frappe's Customize Form / Custom Field; the SPA renders them via field layouts,
   and MCP tools return them in a `custom` object, so customisation reaches chat and MCP too.

**Consequences.** + Fits each company's process without code. + Chat/MCP stay stable because tools
take status *names* but validate via categories. − More configuration to test: every rule needs tests
per category, and settings changes are audited (`track_changes`) and exportable as fixtures.
