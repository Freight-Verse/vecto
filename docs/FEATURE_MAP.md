# Feature map

Scope: a complete TMS — order management, dispatch, tendering, rating, tracking and billing for
shippers, brokers, carriers and 3PLs. New rows are added through a `type:feature` issue.

Legend: P1 = MVP, P2 = next, P3 = later. "MCP" = tool(s) that must exist for the feature.

| Area | Feature | Phase | MCP tools (indicative) |
|---|---|---|---|
| Orders | Shipment orders, multi-stop loads, commodities, refs | P1 | `vecto_order_create`, `vecto_load_create`, `vecto_load_get`, `vecto_load_search` |
| Orders | Templates / recurring loads, load copy | P2 | `vecto_load_clone` |
| Modes | FTL, LTL, partial; intermodal, drayage, air/ocean later | P1 / P3 | — |
| Rating | Customer & carrier rate cards, lanes, FSC, accessorials | P1 | `vecto_rate_lookup` |
| Rating | Spot quotes with margin, quote → order | P1 | `vecto_quote_create`, `vecto_quote_convert` |
| Rating | LTL rating API, market rate benchmarks | P3 | `vecto_rate_benchmark` |
| Carriers | Carrier profiles, lanes, preferred carriers | P1 | `vecto_carrier_search`, `vecto_carrier_get` |
| Carriers | Regional compliance framework + FMCSA (US): registry lookup, tender/dispatch gate, monitoring | P1 | `vecto_carrier_registry_lookup`, `vecto_carrier_compliance_check`, `vecto_carrier_compliance_status` |
| Carriers | More regions (Canada provinces, Mexico, others) + commercial providers | P2 | same tools |
| Tendering | Tender by email/portal, accept/reject, expiry, waterfall | P1 | `vecto_tender_send`, `vecto_tender_respond` |
| Tendering | EDI 204/990; load board posting | P2 | `vecto_loadboard_post` |
| Dispatch | Assign carrier/driver/equipment, rate confirmation PDF | P1 | `vecto_load_assign`, `vecto_ratecon_generate` |
| Tracking | Check calls, status updates, ETA, exceptions | P1 | `vecto_tracking_add_event`, `vecto_load_timeline` |
| Tracking | ELD/GPS providers, EDI 214, visibility providers | P2 | `vecto_tracking_subscribe` |
| Documents | BOL, POD, upload + OCR extract, doc requirements per customer | P1 / P2 | `vecto_document_attach`, `vecto_document_extract` |
| Billing | Customer invoicing → Sales Invoice, EDI 210 | P1 / P2 | `vecto_invoice_draft` |
| Billing | Carrier freight bill audit → Purchase Invoice, quick pay | P2 | `vecto_freightbill_audit` |
| Claims | OS&D claims | P3 | `vecto_claim_create` |
| Portals | Customer portal (quote, book, track, docs) | P2 | (same tools, portal role) |
| Portals | Carrier portal (accept tenders, update status, upload POD) | P2 | (same tools, carrier role) |
| Analytics | Margin per load/customer/lane, on-time %, carrier scorecard | P2 | `vecto_report_run` |
| AI | Chat prompt in app; MCP server; agent audit | P1 | all |
| AI | Specialist background agents (dispatch, tracking, billing, compliance) | P2–P3 | — |
| API | Versioned REST, OpenAPI docs, scoped tokens, webhooks, sandbox, SDKs (`docs/API_STANDARDS.md`) | P1 / P2 | — |
| AI | Email intake: quote requests and carrier emails → drafts in the TMS | P2 | `vecto_email_parse`, `vecto_quote_create` |
| Mobile | Driver/carrier mobile app (PWA): accept tender, status, POD photo, location | P2 | (same tools, carrier role) |
| Onboarding | Setup wizard, demo data, spreadsheet import | P1 | `vecto_import_job` |
| Rating | Market-rate quoting with markup rules; store source rate per quote | P2 | `vecto_rate_market` |
| Capacity | Carrier truck availability posts matched to open loads | P2 | `vecto_capacity_post`, `vecto_capacity_match` |
| Dispatch | Appointment scheduling with facilities/customers (request, confirm, propose, batch) | P2 | `vecto_appointment_request` |
| Core | Load locking / concurrent-edit control | P1 | — |
| Migration | Import from Salesforce-based TMS orgs | P2 | `vecto_import_job` |

## Phase 1 (MVP) definition of done
A broker user can, from either forms or chat: quote a lane → convert to order/load → find and tender
a carrier → record acceptance → dispatch with rate confirmation → log check calls to delivery →
attach POD → draft the customer Sales Invoice and the carrier Purchase Invoice → see load margin.
The same flow works from Claude Desktop through the MCP server.
