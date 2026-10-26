# GitHub plan — Freight-Verse/vecto

This file is the source for everything created in GitHub: labels, milestones, the project board,
epics and issues. Each `###` item below becomes one GitHub issue. "Brief" means Claude writes
`docs/tasks/NNNN-*.md` before Cursor starts.

## Project board: "Vecto Roadmap" (GitHub Projects)
Columns (Status): Backlog → Needs brief → Ready for Cursor → In progress → In review → Done
Fields: Phase (P0–P3), Area, Size (S/M/L), Priority (High/Med/Low), Task brief (text)
Views: Board by Status · Table by Phase · Roadmap by Milestone

## Labels
- type: `type:epic` `type:feature` `type:bug` `type:chore` `type:adr` `type:docs`
- area: `area:core` `area:orders` `area:rating` `area:carriers` `area:tendering` `area:dispatch`
  `area:tracking` `area:documents` `area:billing` `area:portal` `area:edi` `area:integrations`
  `area:mcp` `area:chat` `area:ui` `area:devops`
- flow: `needs-adr` `needs-brief` `agent:ready` `agent:in-progress` `needs-review` `blocked`

## Milestones
| Milestone | Goal |
|---|---|
| M0 Foundation | Repo, CI, app skeleton, core data model, lifecycle, tool registry, MCP endpoint |
| M1 MVP broker flow | Quote → load → tender → dispatch → track → POD → invoice, via forms, chat and MCP |
| M2 Scale & automation | Portals, EDI, compliance, load boards, ELD tracking, freight audit, analytics |
| M3 Advanced | Specialist agents, LTL/intermodal, claims, large-scale migration imports |

---

## M0 Foundation

### [ADR] Accept ADR-0001..0004 (ERPNext base, MCP-first registry, confirm-before-write, frontend stack)
`type:adr` · decision by Anupam · blocks everything below

### Choose and add an open-source license
`type:chore` `area:devops` · S · decision by Anupam
- Must be compatible with ERPNext (GPL-3.0). Options: AGPL-3.0 (used by Frappe CRM/Helpdesk), GPL-3.0
- Add LICENSE file and SPDX headers policy

### Repo & CI setup
`type:chore` `area:devops` · S
- Squash-merge only, branch protection on main, no CODEOWNERS (avoids automatic review requests)
- CI: ruff, eslint/prettier, `bench run-tests --app vecto`, `bench migrate` on fresh site
- Attribution check (fails on bot authors or Co-authored-by/Reviewed-by/Made-with trailers)
- Claude GitHub review workflow (read-only)

### App skeleton `vecto` on ERPNext
`type:chore` `area:core` · S · brief 0000
- `bench new-app vecto`, required_apps erpnext, module folders per AGENTS.md, roles, Vecto Settings

### Load core data model
`type:feature` `area:core` · M · brief 0001
- Shipment Order, Load, Load Stop, Load Commodity, Load Charge, Facility, Equipment Type
- Time zone per facility, UOM on weight/dims, naming series

### Load lifecycle service
`type:feature` `area:core` · M · brief 0002
- State machine in services/load_lifecycle.py, Tracking Event per transition, illegal-transition tests

### Shared tool registry + MCP endpoint
`type:feature` `area:mcp` · M · brief 0003
- vecto/mcp/registry.py over frappe-mcp, OAuth2, Vecto Tool Call audit
- First tools (read-only): `vecto_load_search`, `vecto_load_get`; contract tests
- Verified from Claude Desktop

### Dry-run / idempotency framework for write tools
`type:feature` `area:mcp` · S · brief 0004

### Design system & SPA shell at /vecto
`type:feature` `area:ui` · M · brief 0005 · after ADR-0004
- Tokens, layout (nav · workspace · chat panel), auth, routing, empty/loading/error states

---

## M1 MVP broker flow

### [Epic] Chat assistant (Vecto Assistant)
`type:epic` `area:chat`
- Chat backend: session/message DocTypes, agent run on RQ, streaming via realtime, LLM provider adapter
- Chat panel UI + ⌘K, context of the open record, suggested prompts
- Result cards (Load, Carrier, Rate table, Timeline) and ConfirmCard for writes
- Usage limits and per-user budget in Vecto Settings

### [Epic] Rating & quotes
`type:epic` `area:rating`
- Lane, Rate Card (customer + carrier), Fuel Surcharge Table, accessorial Items
- `vecto_rate_lookup` service + tool
- Quote with margin, `vecto_quote_create`, `vecto_quote_convert` → Shipment Order/Load

### [Epic] Carriers
`type:epic` `area:carriers`
- Carrier (→ Supplier), lanes, preferred carriers, basic compliance fields with expiry
- `vecto_carrier_search` (by lane/equipment/history), `vecto_carrier_get`
- Block tender/dispatch to non-compliant carriers

### [Epic] Regional carrier compliance (FMCSA first)
`type:epic` `area:carriers` — see ADR-0005
- Compliance region, regulatory IDs, policy rules, provider interface
- FMCSA QCMobile adapter; FMCSA open-data (L&I, insurance) adapter
- Per-load regional gate for tender/dispatch; scheduled monitoring and change alerts
- MCP tools and onboarding pre-fill

### [Epic] Tendering
`type:epic` `area:tendering`
- Tender DocType (method, expiry, response), email tender + accept/reject link
- Waterfall tendering (next carrier on reject/expiry)
- `vecto_tender_send`, `vecto_tender_respond`

### [Epic] Dispatch
`type:epic` `area:dispatch`
- Assign carrier/driver/equipment, `vecto_load_assign`
- Rate confirmation print format + `vecto_ratecon_generate`, email to carrier
- Load board view (by status, date, dispatcher)

### [Epic] Tracking
`type:epic` `area:tracking`
- Check calls & manual status updates, ETA, exceptions (late, missed appointment)
- `vecto_tracking_add_event`, `vecto_load_timeline`
- Timeline UI + map view

### [Epic] Documents
`type:epic` `area:documents`
- Load Document (BOL, POD, rate con), required docs per customer before invoicing
- `vecto_document_attach`

### [Epic] Billing
`type:epic` `area:billing`
- Customer Sales Invoice from Load charges, `vecto_invoice_draft`
- Carrier Purchase Invoice from carrier charges
- Per-load margin report (Cost Center/Project)

### MVP end-to-end acceptance test
`type:chore` · after all M1 epics
- Full flow via forms, via chat, and via Claude Desktop MCP — recorded as a test script

---

## M2 Scale & automation (epics, split into issues when M1 is near done)
- [Epic] Customer portal — quote, book, track, documents
- [Epic] Carrier portal — accept tenders, status updates, POD upload
- [Epic] EDI X12 — partners, 204/990/214/210, message log
- [Epic] Regional compliance: more regions and providers — Canada provinces, Mexico, others; Highway/RMIS/Carrier Assure
- [Epic] Load boards — DAT/Truckstop posting
- [Epic] Visibility — ELD/GPS providers, project44/MacroPoint adapters, auto check calls
- [Epic] Document OCR — extract BOL/POD/freight bill fields
- [Epic] Freight bill audit — match carrier bills to agreed charges, variance workflow
- [Epic] Analytics — margin by customer/lane, on-time %, carrier scorecards
- [Epic] Salesforce-based TMS import — objects mapping, bulk import job

## M3 Advanced
- [Epic] Specialist background agents — dispatch, tracking, billing/audit, compliance
- [Epic] More modes — LTL rating API, intermodal, drayage
- [Epic] Claims (OS&D)
