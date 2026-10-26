# Vecto architecture

Status: Proposed (v0.1, 2026-10-26). Changes go through ADRs in `docs/adr/`.

## 1. Principles
1. **MCP-first.** Every capability is designed first as a tool contract (name, input schema,
   output schema, read/write, permissions). Forms, REST, the chat agent and external MCP clients
   (Claude, Cursor, ChatGPT, n8n) all use the same service function behind that contract.
2. **One brain, many faces.** Business rules live once, in `services/`. Adapters are thin.
3. **ERPNext is the ledger.** Customers, suppliers (carriers), items (accessorials), invoices and
   payments stay in ERPNext. Vecto owns the transportation domain.
4. **Human in the loop for writes.** The AI can draft anything; it commits money-, carrier- or
   customer-facing actions only after the user confirms (or a rule explicitly allows auto-commit).
5. **Everything is an event.** Every load status change, tender response, check call and tool call
   is an immutable row. Status fields are projections of events, which gives audit and replay.

## 2. Layers
```
            ┌───────────── Users ─────────────┐   ┌──── External agents ────┐
            │ Vue SPA (/vecto)   Frappe Desk   │   │ Claude / Cursor / n8n   │
            │  ├ Workspace views               │   │ ChatGPT / custom        │
            │  └ Chat prompt ──► Vecto Agent   │   └───────────┬─────────────┘
            └──────┬───────────────────┬───────┘               │ MCP (Streamable HTTP + OAuth2)
                   │ REST              │ in-process tool calls  │
            ┌──────▼──────┐     ┌──────▼──────────────────────▼──┐
            │ api/ (thin) │     │ mcp/ tool adapters (thin)       │
            └──────┬──────┘     └──────────────┬──────────────────┘
                   └──────────────┬────────────┘
                          ┌───────▼────────┐
                          │   services/    │  rules, permissions, lifecycle, idempotency
                          └───────┬────────┘
             ┌────────────────────┼─────────────────────┐
     ┌───────▼───────┐    ┌───────▼───────┐     ┌───────▼────────┐
     │ Vecto DocTypes │    │ ERPNext masters│     │ integrations/  │ load boards, tracking,
     │ Load, Stop ... │    │ & accounting   │     │ EDI, LLM, OCR  │ ELD/GPS, email
     └────────────────┘    └────────────────┘     └────────────────┘
       Background: RQ workers (long, short, default) · Realtime: socket.io · Scheduler
```

The chat agent calls the **same tool registry in-process** that the MCP server exposes over HTTP,
so a tool that works in Claude Desktop works in the in-app chat, and vice versa.

## 3. Core data model (first cut)

| DocType | Purpose | Key links |
|---|---|---|
| Vecto Settings | Single: defaults, LLM provider, feature flags, integration secrets | — |
| Load Status / Load Status Transition | Configurable statuses (with fixed category) and allowed transitions (ADR-0006) | Mode, Customer |
| Vocabulary masters | Mode, Stop Type, Reference Type, Tracking Event Type, Exception Type, Reason Code, Document Type + requirements | — |
| Shipment Order | Customer's request (what, from, to, when). Can produce 1..n Loads | Customer |
| Load | The unit of execution (one truck/move). Owns status | Shipment Order, Carrier, Driver, Equipment Type |
| Load Stop (child) | Ordered pick/drop stops: facility, appointment window, time zone, refs | Facility |
| Load Commodity (child) | Pieces, weight+UOM, dims, class (LTL), hazmat, value | UOM |
| Load Charge (child) | Customer-side and carrier-side charge lines, linehaul/fuel/accessorial | Item |
| Facility | Shipper/consignee location with hours, time zone, dock notes | Address, Contact |
| Carrier | Transport provider profile: MC/DOT/SCAC, modes, lanes, compliance status | Supplier |
| Carrier Regulatory ID (child) | Per-region identifiers: USDOT, MC, NSC/CVOR, SICT… | Compliance Region |
| Compliance Region / Policy | Regions the company operates in, provider adapter, block/warn rules | — |
| Compliance Snapshot / Event | Normalised check result per region; detected changes | Carrier |
| Driver / Equipment / Equipment Type | Asset-side records (for carriers and private fleets) | Carrier |
| Lane | Origin→destination pattern (zip3/city/state/region) | — |
| Rate Card / Rate Card Line | Contract rates (customer or carrier side), by lane, mode, equipment, weight break | Customer/Carrier, Lane |
| Fuel Surcharge Table | FSC by fuel index range | — |
| Quote | Customer quote with margin; converts to Shipment Order | Customer, Lane |
| Tender | Offer of a Load to a carrier: method (email/EDI/API/portal), expiry, response | Load, Carrier |
| Tracking Event | Check calls, ELD/GPS pings, EDI 214 statuses, ETA, exceptions | Load, Load Stop |
| Load Document | Rate confirmation, BOL, POD, lumper receipts; OCR extract | Load |
| Freight Bill | Carrier invoice received; audit vs. agreed charges → Purchase Invoice | Load, Carrier |
| Claim | OS&D / damage claims | Load |
| EDI Partner / EDI Message | Trading partner config; raw + parsed X12 with status | Customer/Carrier |
| Vecto Agent Session / Message | Chat threads per user | User |
| Vecto Tool Call | Audit of every tool call: tool, args, result, user, source (chat/MCP), latency | Session |

Customer billing creates ERPNext **Sales Invoice**; carrier settlement creates **Purchase Invoice**;
both carry the Load as a reference and use Cost Center/Project for per-load margin reporting.

## 4. Load lifecycle — configurable (ADR-0006; single entry point `services/load_lifecycle.py`)
Statuses and transitions are **data**, editable per company (and per mode or customer). Code depends
only on these fixed **categories**:
```
Draft → Planning → Tendering → Covered → Dispatched → In Transit → Delivered → Billing → Closed
                                   (any category before In Transit) → Cancelled
```
Default statuses shipped per category (rename, add, hide, reorder freely):
Draft: Draft · Planning: Planned · Tendering: Tendered · Covered: Covered/Booked ·
Dispatched: Dispatched, At Pickup · In Transit: Loaded, In Transit, At Delivery ·
Delivered: Delivered, POD Received · Billing: Invoiced, Settled · Closed: Closed ·
Cancelled: Cancelled, TONU.

Each transition row defines allowed roles, required fields/documents, a condition and auto-actions.
The service enforces those rows plus fixed category guards, writes a Tracking Event, and fires hooks
(notifications, EDI 214 out, portal update). Transitions are tools too (`vecto_load_transition`,
takes a status name, always with `dry_run`). Each status has internal, customer and carrier labels.

## 5. Roles
Vecto Admin · Dispatcher / Carrier Sales · Customer Sales / Account Manager · Billing / AP-AR ·
Tracking Rep · Carrier (portal user) · Customer (portal user) · Vecto Agent (service role for
automation, never broader than the human role it acts for).

## 6. Agents inside the product
Phase 1: one **Vecto Assistant** with the full tool catalog, scoped by the user's permissions.
Phase 2+: specialist agents that share the same tools but different instructions and tool subsets:
- Dispatch agent — build loads, find and tender carriers, chase acceptance.
- Tracking agent — watch ETAs, raise exceptions, request check calls.
- Billing/audit agent — match freight bills to agreed rates, flag variances, draft invoices.
- Carrier compliance agent — monitor expiring insurance/authority, block non-compliant carriers.
Specialists run as background jobs on schedules or events and post results to the chat inbox
for human confirmation. Each run is a Vecto Agent Session with full tool-call audit.

## 7. Integrations (adapter per vendor, behind an interface in `integrations/`)
Load boards (DAT, Truckstop) · Visibility (ELD/GPS providers, project44, MacroPoint, Trucker Tools) ·
Regional carrier compliance (FMCSA first, then Canada/Mexico/other regions; optional Highway, RMIS, Carrier Assure — see ADR-0005) · LTL rating (SMC3 or carrier APIs) ·
EDI X12 204/990/214/210 via VAN or AS2 · Email-in (tenders, PODs) · OCR for documents ·
Salesforce-based TMS migration import (one-time and sync).
All outbound calls: timeout, retry with backoff, idempotency, request log, per-tenant rate limit.

## 8. Non-functional
- Multi-tenant via Frappe sites (one site per company; works with self-hosted bench or Frappe Press).
- Background jobs for anything > 2 s; realtime updates to the SPA via `frappe.publish_realtime`.
- Observability: Vecto Tool Call + Integration Request logs; error log alerts.
- Performance budget: list views < 300 ms server time for 10k loads; chat first token < 2 s.
