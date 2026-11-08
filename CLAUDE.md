# Vecto — TMS on Frappe v16

**App name:** `vecto`  
**Publisher:** Freightverse (`tech@freightverse.io`)  
**Framework:** Frappe v16 (**requires ERPNext** — `required_apps = ["erpnext"]`)  
**Description:** A modern Transportation Management System covering freight brokerage, asset carrier operations, and 3PL logistics.  
**Branch convention:** `develop` is the primary working branch.

**License:** AGPL-3.0 (decided in #2)  
**Target:** Frappe/ERPNext **v16 only** (ADR-0001) — no v15 support.

> **ERPNext name collisions:** ERPNext already defines `Driver`, `Vehicle`, and `Location`. Vecto uses **`TMS Driver`**, **`TMS Vehicle`**, and **`TMS Location`** instead. All Link fields in this spec must point at those TMS names.

---

## Sources of Truth

This file merges two plans:

1. **This file**: the phase-by-phase field specs that the code on `develop` is built from.
2. **GitHub `Freight-Verse/vecto` on `main`**: `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/MCP_AND_CHAT.md`, `docs/API_STANDARDS.md`, ADRs `docs/adr/0001–0006`, task briefs in `docs/tasks/`, and issues #1–#81.

**Precedence:** an accepted ADR wins over this file. This file wins over a task brief where they disagree on **names** (see the Name Mapping below). For anything else, stop and ask Anupam.

> `develop` and `main` currently have **no common git history**. Read docs on main with `git show origin/main:<path>`. Do not merge either branch into the other without Anupam's decision.

---

## Claude's Role & Authorship

**Role**
1. **Architect**: proposes changes as ADRs (`docs/adr/`). Anupam accepts or rejects them.
2. **Planner**: turns an issue into a task brief (`docs/tasks/`, using `TEMPLATE.md`). The brief must be precise enough that Cursor can implement it without making design decisions.
3. **Reviewer**: reviews every PR before Anupam merges it. Claude does not write feature code unless Anupam asks.

**Authorship (non-negotiable; applies to Claude, Cursor and every other agent)**
- Commits are authored by Anupam in his own git identity. Agents are never the author, a co-author or the reviewer of record.
- **Never** add `Co-authored-by:`, `Reviewed-by:`, `Made-with:`, `Generated-by:` or any other attribution trailer to commits, PR titles or PR bodies. Never add "Generated with …" lines or tool links. This includes Cursor's automatic `Co-authored-by: Cursor` trailer, which must be turned off.
- Never change `git config user.name` / `user.email`. Never request reviewers.
- On GitHub, post review **comments** only. Never submit an "Approve" or "Request changes" review state. Agents do not merge; Anupam squash-merges.

**Review checklist** (in order; stop at the first blocking failure)

*Blocking*
- [ ] Matches the task brief / phase spec scope; no features or refactors that weren't asked for.
- [ ] Business logic lives in `services/`; controllers, `api/v1/` and MCP tools are thin.
- [ ] Permissions are enforced in services; no `ignore_permissions` without a comment explaining why.
- [ ] Load status changes go only through the lifecycle service; illegal transitions are rejected.
- [ ] No hard-coded status names or other configurable vocabulary; rules use status **categories**.
- [ ] Money, time zone and UOM rules are followed.
- [ ] Write endpoints/tools support `dry_run` and `idempotency_key`; destructive ones are flagged.
- [ ] No secrets, no raw string SQL, no N+1 queries in list endpoints.
- [ ] Tests cover the failure paths, not only the happy path.
- [ ] Patches exist for every schema/data change that existing sites need.
- [ ] No attribution trailers; the commit author is a human.

*Non-blocking* (comment, don't hold the PR): naming, readability, docstrings (they become LLM-facing tool descriptions), UI consistency, chances to delete code.

**Review output:** Verdict `READY TO MERGE` / `CHANGES NEEDED` / `NEEDS DECISION` → findings as `file:line — problem — concrete fix`, most severe first → a short "Fix prompt for Cursor" block.

---

## Name Mapping (main plan ↔ this repo)

Issues and task briefs on `main` use the names on the left. **Code on `develop` uses the names on the right, and those stay canonical.** Read every brief through this table.

| main / issues | develop (canonical) | Notes |
|---|---|---|
| Load | Load Order | One doc = one move. A separate Shipment Order (1..n loads) is deferred until a customer needs it. |
| Load Stop / Load Charge | Load Stop Detail / Load Accessorial Detail + rate fields | Child suffix stays `Detail`. |
| Customer (ERPNext) | Shipper → `erpnext_customer` | Shipper is the TMS profile; ERPNext Customer stays the ledger party. |
| Facility | TMS Location | Add `time_zone` (IANA) when appointments land (#79). |
| Vecto Settings | TMS Settings | |
| Carrier → Supplier | Carrier → `erpnext_supplier` | Same pattern. |
| Driver / Equipment | TMS Driver / TMS Vehicle | |
| Tracking Event | Load Event (Phase 6) + Load Status Log | Status changes write a Load Status Log row now and a Load Event once Phase 6 lands. |
| `vecto/services/` | `vecto/services/` | **Adopted.** `vecto/utils/` is legacy; move its contents into services. |
| Vecto Admin | TMS Admin | Roles: see the Roles table. |
| Billing | TMS Finance | |

---

## Architecture Rules (from AGENTS.md / ARCHITECTURE.md)

- **MCP-first, one brain:** each capability is **one service function** in `vecto/services/`. Desk controllers, `api/v1/` endpoints, MCP tools (`vecto/mcp/`, #7) and the Vue SPA (#9) are thin adapters over it.
- **ERPNext is the ledger:** reuse Customer, Supplier, Address, Contact, Item, UOM, Currency, Sales/Purchase Invoice, Payment Entry, Company, Cost Center. Don't duplicate them.
- **Human in the loop:** writes coming from chat/MCP default to `dry_run=True` and accept an `idempotency_key` (ADR-0003, #8). Errors are structured as `{code, message, hint}` (e.g. `TRANSITION_NOT_ALLOWED`, `CARRIER_NOT_COMPLIANT`).
- **Everything is an event:** status changes, tender responses and check calls are immutable rows; status fields are projections of them.
- **Configurable vocabulary (ADR-0006):** anything a user might rename (statuses, modes, equipment types, stop types, reasons, document types) is a DocType, and code never compares its names. Defaults are inserted by `install.py`, and by a patch for existing sites. Insert only if missing; never overwrite user edits; **never ship them as fixtures**. Fixtures are for config only (roles, workspace, print formats).
- **Money:** `Currency` fields plus an explicit currency; use `flt(x, precision)` for totals in Python.
- **Time & UOM:** datetimes are stored in system time as Frappe does; stops carry the location's time zone; weight/dimensions are always stored as value + UOM.
- **Secrets:** Password fields on TMS Settings or `site_config`; never in code or fixtures.
- **SQL:** `frappe.qb` or parameterised `frappe.db.sql`; never string concatenation.
- **Integrations** (`vecto/integrations/`): one adapter per vendor behind an interface; timeout, retry with backoff, idempotency, request log. Tests never touch the real network.
- **Background:** anything over 2 s runs on RQ; realtime updates use `frappe.publish_realtime`.

---

## Load Lifecycle — Status Categories (ADR-0006)

`Load Status` rows are user data; **code only knows the fixed category list** (constant `STATUS_CATEGORIES` in `vecto/services/status.py`):

```
Draft → Planning → Tendering → Covered → Dispatched → In Transit → Delivered → Billing → Closed
                       (any category before In Transit) → Cancelled
```

Fixed guards (enforced even when a transition row allows otherwise):
1. A forward move may skip at most one category. Billing is reachable only from Delivered (or from Cancelled for a `billable_cancellation` status such as TONU); Closed is reachable only from Billing.
2. Backward moves are allowed only Tendering → Planning (tender rejected/expired) and Covered → Planning (carrier fell off).
3. Cancelled is reachable only before In Transit; nothing leaves Cancelled except to Billing via TONU.
4. A move within the same category is allowed if a transition row exists.

All status changes go through `vecto/services/load_lifecycle.py`: `allowed_transitions(load)` and `transition(load, to_status, *, reason=None, dry_run=False, idempotency_key=None, source="User")`. Transition rows (`Load Status Transition`: from/to, allowed roles, required fields, requires reason, condition, scoped by mode → customer) come with #6. Until then the service enforces the category guards alone. Business rules say "category is Delivered", never `status == "Delivered"`.

---

## Product Thesis

Vecto is the **open-source broker + asset + 3PL TMS** on Frappe v16 + ERPNext. Win on a complete load file, honest sell/buy/margin, ERPNext money (Customer/Supplier/GL), and a versioned API. Do not clone Salesforce (Revenova) or Qargo’s AI stack in core.

| Capability | Commercial bar | Vecto |
|---|---|---|
| Load file, stops, status | Every TMS | Phase 2 — `status` is Link **Load Status** |
| Tender / capacity offer | Revenova, Aljex, McLeod | Phase 2 `tender_load` — **not** on Load Order submit |
| Trip / driver–vehicle | Qargo fleet, McLeod | Phase 2 Trip |
| Dispatch board | McLeod Visual Planner | Phase 2 Kanban `/vecto/dispatch` (drag-drop planner later) |
| Quote / FSC / accessorials | RateIQ, Qargo rate cards | Phase 3 |
| Carrier certs / scorecards | LaneIQ, Aljex | Phase 4 |
| Invoice + settlement | Revenova / Qargo finance | Phase 5 + ERPNext SI/PI |
| Track, POD, GPS | All vendors | Phase 6 |
| Shipper / carrier portals | Revenova board, Qargo | Phase 7 |
| EDI, DAT, Truckstop | McLeod, Aljex | Phase 8 |
| CRM / relationship history | Revenova-on-Salesforce | Use ERPNext Customer/Supplier + Shipper/Carrier links |
| AI email/PDF intake, mileage, ELD, SMS, driver app | Artimus, Qi, PC*Miler | **Backlog** — addons, not Phase 2 |

---

## Implementation Model

This project is built through a combination of three modes — understand which tool owns which task:

| Task | Owner |
|---|---|
| Doctype JSON schema (fields, permissions, naming) | **Manual** (Frappe Desk UI → export) or **Cursor** |
| Controller logic (`doctype/<name>/<name>.py`) | **Cursor** |
| Client scripts (`doctype/<name>/<name>.js`) | **Cursor** |
| API endpoints (`api/v1/*.py`) | **Cursor** |
| Business logic (`services/*.py`) | **Cursor** |
| Bench commands (migrate, export-fixtures, install) | **Manual** (terminal) |
| Workspace / Dashboard JSON | **Manual** (Frappe Desk UI → export) |
| Print Format HTML/Jinja | **Cursor** |
| Test files (`tests/test_*.py`) | **Cursor** |
| Architecture decisions (ADRs), task briefs, phase specs, code review | **Claude**: see Claude's Role above |

**Cursor context tip:** When starting a new file in Cursor, paste the relevant Phase Requirements section from this file as a comment block at the top — it gives Cursor the full field spec, naming conventions, and business rules without re-explaining them.

**Frappe doctype / fixture workflow:**
1. **DocType JSON** — create under `vecto/vecto/doctype/<name>/` (Cursor) **or** in Desk with Developer Mode on; Frappe writes/updates the JSON on save. Do **not** use `export-fixtures` for DocType schema.
2. **Fixtures** (Roles, Workspace, Print Formats, etc.) — list them in `hooks.py` `fixtures`, then run `bench --site <site> export-fixtures --app vecto`.
3. Open the JSON + `<name>.py` in Cursor and implement the controller / client script.
4. `bench --site <site> migrate` after any schema change.

---

## Project Architecture

```
vecto/
├── vecto/
│   ├── hooks.py                   # App hooks (events, scheduled tasks, overrides)
│   ├── modules.txt                # Module list
│   ├── vecto/                     # "Vecto" module
│   │   ├── doctype/               # All doctypes live here
│   │   ├── report/                # Reports
│   │   ├── page/                  # Custom pages (dispatch board, etc.)
│   │   ├── workspace/             # Workspace JSON
│   │   └── dashboard/             # Dashboard charts
│   ├── api/
│   │   └── v1/                    # All public API endpoints (versioned)
│   │       ├── __init__.py
│   │       ├── loads.py           # Load Order endpoints
│   │       ├── tracking.py        # GPS / event endpoints
│   │       ├── carriers.py        # Carrier-facing endpoints
│   │       ├── quotes.py          # Quote / rating endpoints
│   │       └── billing.py         # Invoice / settlement endpoints
│   ├── services/                  # Business rules: the ONLY place rules live (returns dict/list)
│   ├── utils/                     # Legacy; move contents into services/ (no new code here)
│   ├── mcp/                       # MCP tool registry + adapters, thin (#7)
│   ├── integrations/              # Outbound vendor adapters (FMCSA, DAT, ELD, LLM…)
│   ├── patches/                   # Data/schema patches for existing sites
│   └── templates/                 # Jinja / web templates
├── frontend/                      # Vue 3 + TypeScript + Frappe UI SPA at /vecto (ADR-0004, #9)
└── pyproject.toml
```

Later modules from the main plan (`carrier/`, `rating/`, `tracking/`, `billing/`, `edi/`, `agent/`) are added when their phase starts. Until then everything stays in the `Vecto` module.

---

## Coding Rules

### Python
- Use tabs for indentation (Frappe convention — enforced by ruff).
- Line length ≤ 110 characters.
- Controllers implement `validate` / `on_*` / `before_*` only. **Never** put `@frappe.whitelist()` on a doctype controller.
- All server-side API functions exposed to the client live in `vecto/api/v1/` and must be decorated with `@frappe.whitelist()`.
- Business logic lives in `vecto/services/` and returns plain `dict` / `list`, not Document objects. Services check permissions (`frappe.has_permission` / `frappe.get_list`).
- Never use bare `except:`; always catch specific exceptions or at minimum `except Exception as e`.
- Use `frappe.db.get_value` / `frappe.db.get_all` / `frappe.db.set_value` for single-field reads/writes instead of loading the full document.
- Use `frappe.get_doc` only when you need to trigger controller methods or validations.
- All monetary values stored as `Currency` field type, never as `Float`.
- Dates stored as `Date`, datetimes as `Datetime`. Never store as string.
- Use `frappe._()` for all user-facing strings (i18n).
- Do not hard-code company name; always read from `frappe.defaults.get_global_default("company")` or pass as parameter.
- `ignore_permissions` is allowed only in install/seed/migrate helpers, or with a comment explaining why.
- Never hard-code status names or other configurable vocabulary outside `install.py`; use status categories.

### API Design
- All public endpoints live under `vecto/api/v1/`. Never place whitelisted functions directly in doctype controllers or utils — they go in `api/v1/<resource>.py`.
- Every file in `api/v1/` is a resource module named after the entity it serves (e.g., `loads.py`, `carriers.py`).
- All functions in `api/v1/` must be decorated with `@frappe.whitelist()`.
- The callable path for any endpoint follows: `vecto.api.v1.<module>.<function>` — e.g., `vecto.api.v1.loads.create_load`.
- Future breaking changes introduce a new directory (`api/v2/`) — never change an existing v1 signature in a way that breaks callers; deprecate and add to v2 instead.
- Every API function must validate its inputs explicitly (required fields, types) and raise `frappe.ValidationError` with a clear message on bad input — never let a KeyError or AttributeError bubble up to the caller.
- Return value must always be a plain `dict` or `list`. Never return a Frappe document object directly.
- Endpoints are thin: parse input → call one `services/` function → shape output. No business logic.
- Write endpoints accept `dry_run` (returns a preview and writes nothing) and `idempotency_key` (a replay returns the first result). Errors that callers act on are `{code, message, hint}`.
- Later (#63): versioned REST resources under `/api/v1/vecto/...` with a JSON envelope, cursor pagination and a generated OpenAPI 3.1 spec, built on the same services. The `vecto.api.v1.<module>.<fn>` method endpoints stay supported.
- API functions that are public (no login required) must also pass `allow_guest=True` to `@frappe.whitelist()` and must authenticate via an API key header (`X-Vecto-Key`), checked with a helper in `vecto/api/v1/__init__.py`.

**Endpoint naming convention:**

| Action | Method pattern |
|---|---|
| Create a resource | `create_<resource>` |
| Fetch a resource | `get_<resource>` |
| Update a resource | `update_<resource>` |
| List resources | `list_<resources>` |
| Perform an action | `<verb>_<resource>` (e.g., `tender_load`, `accept_tender`) |

**Example skeleton** (`api/v1/loads.py`):
```python
import frappe
from vecto.api.v1 import require_api_key  # for guest endpoints


@frappe.whitelist()
def create_load(shipper, origin, destination, load_type, weight=None, commodity=None):
	"""Create a Load Order from an external system."""
	# validate
	if not shipper or not origin or not destination:
		frappe.throw(frappe._("shipper, origin, and destination are required"), frappe.ValidationError)
	doc = frappe.get_doc({
		"doctype": "Load Order",
		"shipper": shipper,
		"origin": origin,
		"destination": destination,
		"load_type": load_type,
		"weight": weight,
		"commodity": commodity,
	})
	doc.insert(ignore_permissions=False)
	return {"load": doc.name, "status": doc.status}


@frappe.whitelist()
def get_load_status(load):
	"""Return current status and last event for a Load Order."""
	if not frappe.db.exists("Load Order", load):
		frappe.throw(frappe._("Load Order {0} not found").format(load), frappe.DoesNotExistError)
	status = frappe.db.get_value("Load Order", load, ["status", "assigned_carrier", "assigned_driver"], as_dict=True)
	last_event = frappe.db.get_value(
		"Load Event", {"load_order": load}, ["event_type", "timestamp", "notes"], order_by="timestamp desc", as_dict=True
	)
	return {"load": load, **status, "last_event": last_event}
```

### JavaScript (Desk)
- All client scripts go in `doctype/<name>/<name>.js`.
- Use `frappe.call` (not raw fetch) for all server calls.
- Use `cur_frm.add_custom_button` for action buttons; group related buttons under a label.
- Trigger `frm.refresh_field()` after programmatically setting field values.
- Never commit directly to `frappe.db` from client-side JS — always call a whitelisted Python method.

### Doctype Design
- Every non-Single, non-child doctype must have a `naming_series` field **or** use `autoname = "field:..."`.
- Phase 1 masters use `autoname = "field:<title_field>"`. Transactional doctypes (Phase 2+) use naming series (`autoname = "naming_series:"`, `set_only_once` on the series field).
- Naming series convention: `LOAD-.YYYY.-.#####` (prefix varies by doctype — see per-doctype rules below).
- All submittable doctypes set `is_submittable: 1` and have an `amended_from` Link.
- Use `Link` fields (not `Data`) for all foreign-key references. `fetch_from` is for display copies only.
- Never reuse reserved fieldnames: `name`, `owner`, `creation`, `modified`, `modified_by`, `parent`, `parenttype`, `parentfield`, `docstatus`, `idx`.
- Child tables use the suffix `Detail`; set `istable: 1`, `editable_grid: 1`, empty `permissions`.
- Set `title_field`, `search_fields`, `in_list_view: 1` on 3–5 fields, and `in_standard_filter: 1` on dispatcher filters.
- `track_changes: 1` on transactional doctypes.
- Currency for money; Date / Datetime not strings; Check defaults `"0"` / `"1"`; Select `options` newline-separated.
- Computed money fields (`total_sell`, `total_buy`, `margin`, `margin_pct`) are `read_only`. Status log child is `read_only`.
- `allow_on_submit` only where post-submit edits are required (Load Order `status`).
- `depends_on` / `mandatory_depends_on` for conditional fields.
- Permissions live on the **parent** DocType JSON (roles from fixtures). Children inherit.
- Filter Link queries in client JS (e.g. `assigned_driver` / `assigned_vehicle` by carrier).

### Labels (Title Case)
- Field, Section Break, Tab, Button, Workspace shortcut, and Print Format labels use **Title Case**: `Pickup Date`, `Assigned Carrier`, `Sell Rate`.
- Not sentence case (`Pickup date`) and not SCREAMING (`PICKUP DATE`).
- Abbreviations stay as operators say them: `MC #`, `DOT #`, `FSC`, `PO Number`, `VIN`, `ZIP`.
- `fieldname` is always snake_case. DocType **name** is Title Case (`Load Status Log`).

### Git
- Commit message format: `feat(module): description` / `fix(module): description` / `docs(module):` / `chore:` / `test(module):`.
- **No attribution trailers of any kind** (see Claude's Role & Authorship). CI will fail on them (#3).
- PRs link the issue and the task brief, and aim for < 400 changed lines excluding generated DocType JSON.
- **Commit after every feature.** Schema JSON and controller logic are **separate** commits.
- Never commit compiled `__pycache__` or `.pyc` files (already in `.gitignore`).
- Commit doctype JSON from the app tree after migrate / Desk save; use `export-fixtures` only for hooked fixtures.
- Do not push unless explicitly asked.

---

## Roles & Permissions

| Role | Access |
|---|---|
| `TMS Admin` | Full access to all TMS doctypes |
| `Dispatcher` | Load Order, Trip, Tender; read/write masters (Shipper, TMS Location, Commodity); Carrier/TMS Driver/TMS Vehicle (read) |
| `Carrier Manager` | Carrier, TMS Driver, TMS Vehicle, Carrier Certificate |
| `TMS Finance` | Freight Invoice, Carrier Settlement, Rate Sheet, Shipper (credit) |
| `TMS Customer` | Portal-only: their own Load Orders and invoices (`desk_access=0`) |
| `TMS Carrier Portal` | Portal-only: available loads, their own settlements (`desk_access=0`) |
| `Account Manager` | *To add.* Customer sales: Shipper, Quote, Load Order (create/write) |
| `Tracking Rep` | *To add.* Load Order read + stop actual times; Load Event (Phase 6) |
| `Vecto Agent` | *To add with MCP (#7).* Service role for automation; never broader than the human it acts for |

Main-plan role names map to these: Vecto Admin → `TMS Admin`, Billing → `TMS Finance`, Carrier (portal) → `TMS Carrier Portal`, Customer (portal) → `TMS Customer`, Dispatcher / Carrier Sales → `Dispatcher`.

Define permissions on each doctype JSON — do not use `frappe.set_user_permissions` dynamically unless unavoidable.

---

## Naming Series

| Doctype | Series |
|---|---|
| Load Order | `LOAD-.YYYY.-.#####` |
| Trip | `TRIP-.YYYY.-.#####` |
| Tender | `TNDR-.YYYY.-.#####` |
| Quote | `QT-.YYYY.-.#####` |
| Freight Invoice | `FINV-.YYYY.-.#####` |
| Carrier Settlement | `CSTL-.YYYY.-.#####` |
| Rate Sheet | `RS-.YYYY.-.#####` |

---

## Phase Requirements

**Phase ↔ GitHub issues**

| Phase | Issues |
|---|---|
| 1 Foundation & masters | #4, part of #61 |
| 2 Load management & dispatch | #5, #6, #23–#28, #30, #78 |
| 3 Rating & quoting | #15–#18, #81 |
| 4 Carrier compliance | #19–#22, #54–#60 (FMCSA first), #80 |
| 5 Billing | #36–#39, #48, #53 |
| 6 Track & trace, documents | #31–#35, #46, #47, #79 |
| 7 Portals | #41, #42, #77 |
| 8 Analytics, API, EDI, load boards | #43, #45, #49, #62–#67, #75 |
| 9 More compliance regions | #44, #73 |
| Track A: MCP + assistant (runs alongside phases 2–5) | #7, #8, #10–#14, #51, #76 |
| Track B: SPA (blocked) | #9 |
| Track C: DevOps & community | #3, #40, #50, #52, #68–#72, #74 |

Before implementing an issue, it needs a task brief in `docs/tasks/` (`needs-brief` label). Issues labelled `agent:ready` already have one.

### Phase 1 — Foundation & Master Data
**Goal:** Installable app with all master data forms, roles, and navigation.

**ERPNext dependency:** `required_apps = ["erpnext"]` in `hooks.py`. Links to Company, Account, Payment Terms, UOM, Customer, and Supplier require ERPNext.

**Carrier** (`carrier`) — autoname: `field:carrier_name`
| fieldname | fieldtype | label | options / notes |
|---|---|---|---|
| carrier_name | Data | Carrier Name | required, title_field, unique |
| mc_number | Data | MC # | |
| dot_number | Data | DOT # | |
| status | Select | Status | Active\nInactive\nDo Not Use | default Active |
| address_line_1 | Data | Address Line 1 | |
| address_line_2 | Data | Address Line 2 | |
| city | Data | City | |
| state | Data | State | |
| zip_code | Data | ZIP | |
| phone | Phone | Phone | |
| email | Data | Email | options: Email |
| contact_name | Data | Primary Contact | |
| equipment_types | Table | Equipment Types | child: Carrier Equipment Type Detail |
| — child: equipment_type | Select | Equipment Type | Dry Van\nReefer\nFlatbed\nStep Deck\nLTL\nContainer\nRGN |
| portal_user | Link | User | carrier portal login linking (Phase 7) |
| erpnext_supplier | Link | Supplier | optional; filled/created in Phase 5 settlements |
| notes | Text | Notes | |

**TMS Driver** (`tms_driver`) — autoname: `field:driver_name`  
*(named TMS Driver to avoid collision with ERPNext `Driver`)*
| fieldname | fieldtype | options / notes |
|---|---|---|
| driver_name | Data | required, title_field, unique |
| carrier | Link | Carrier |
| phone | Phone | |
| email | Data | Email |
| license_number | Data | CDL number |
| license_state | Data | |
| license_expiry | Date | client/server alert if &lt; 30 days |
| cdl_class | Select | A\nB\nC |
| hazmat_endorsement | Check | |
| status | Select | Active\nInactive\nTerminated | default Active |

**TMS Vehicle** (`tms_vehicle`) — autoname: `field:plate_number`  
*(named TMS Vehicle to avoid collision with ERPNext `Vehicle`)*
| fieldname | fieldtype | options / notes |
|---|---|---|
| plate_number | Data | title_field, required, unique |
| carrier | Link | Carrier |
| vin | Data | |
| vehicle_type | Select | Dry Van\nReefer\nFlatbed\nStep Deck\nLTL Trailer\nTruck |
| year | Int | |
| make | Data | |
| model | Data | |
| status | Select | Active\nInactive\nIn Repair | default Active |

**Shipper** (`shipper`) — autoname: `field:shipper_name`
| fieldname | fieldtype | options / notes |
|---|---|---|
| shipper_name | Data | title_field, required, unique |
| customer_code | Data | short code for reference |
| phone | Phone | |
| email | Data | Email |
| billing_address | Section Break | |
| billing_address_line_1 | Data | |
| billing_city | Data | |
| billing_state | Data | |
| billing_zip | Data | |
| contacts | Table | child: Shipper Contact Detail |
| — child fields | Data | contact_name, phone, email, role |
| shipping_addresses | Table | child: Shipper Address Detail |
| — child fields | Data | label, address_line_1, city, state, zip, is_default (Check) |
| portal_user | Link | User | for portal login linking |
| erpnext_customer | Link | Customer | optional; filled/created in Phase 5 invoicing |
| credit_limit | Currency | |
| payment_terms | Link | Payment Terms Template | ERPNext doctype |

**TMS Location** (`tms_location`) — autoname: `field:location_name`  
*(named TMS Location to avoid collision with ERPNext `Location`)*
| fieldname | fieldtype | options / notes |
|---|---|---|
| location_name | Data | title_field, required, unique |
| location_type | Select | Terminal\nWarehouse\nPort\nCustomer\nResidential |
| address_line_1 | Data | |
| city | Data | |
| state | Data | |
| zip_code | Data | |
| latitude | Float | |
| longitude | Float | |
| contact_name | Data | |
| phone | Phone | |
| operating_hours | Data | e.g. "06:00–18:00 Mon–Fri" |
| notes | Small Text | |

**Commodity** (`commodity`) — autoname: `field:commodity_name`
| fieldname | fieldtype | options / notes |
|---|---|---|
| commodity_name | Data | title_field, required, unique |
| nmfc_code | Data | |
| freight_class | Select | 50\n55\n60\n65\n70\n77.5\n85\n92.5\n100\n110\n125\n150\n175\n200\n250\n300\n400\n500 |
| is_hazmat | Check | |
| hazmat_un_number | Data | shown if is_hazmat |
| requires_temp_control | Check | |
| temp_min | Float | shown if requires_temp_control |
| temp_max | Float | shown if requires_temp_control |
| default_uom | Link | UOM | |
| notes | Small Text | |

**TMS Settings** (`tms_settings`) — Single doctype
| fieldname | fieldtype | options / notes |
|---|---|---|
| default_company | Link | Company | ERPNext Company |
| default_currency | Link | Currency | |
| load_number_prefix | Data | default: LOAD |
| auto_invoice_on_delivery | Check | Phase 5 — when set, Load Order entering the **Delivered category** triggers `create_freight_invoice` |
| fsc_update_frequency | Select | Daily\nWeekly\nManual |
| default_freight_income_account | Link | Account | |
| default_carrier_cost_account | Link | Account | |
| dat_api_key | Password | Phase 8 |
| truckstop_api_key | Password | Phase 8 |
| vecto_api_key | Password | used for X-Vecto-Key validation |

**Roles:** create on `after_install` / `after_migrate`: `TMS Admin`, `Dispatcher`, `Carrier Manager`, `TMS Finance`, `TMS Customer`, `TMS Carrier Portal`.

**Workspace:** Create a "Vecto" workspace with shortcuts to all master doctypes (including **Load Status**) and a getting-started section.

**Deliverable check:** `bench --site localhost.v16 install-app vecto` completes without errors; all master doctypes are accessible from the workspace; roles are assignable from User master; default Load Status rows are seeded.

---

### Phase 2 — Load Management & Dispatch
**Goal:** Full load lifecycle from creation through delivery; Kanban dispatch board.

**Load Status** (`load_status`) — master; autoname: `field:status_name`  
Used as the **Link** target for `Load Order.status` (and `Load Status Log.status`). Seeded on install; operators can add custom statuses.

| fieldname | fieldtype | options / notes |
|---|---|---|
| status_name | Data | required, title_field, unique; user-editable |
| category | Select | Draft\nPlanning\nTendering\nCovered\nDispatched\nIn Transit\nDelivered\nBilling\nClosed\nCancelled. Required, fixed list (ADR-0006) |
| is_default_for_category | Check | at most one per category; lifecycle moves use it to pick a status |
| sequence | Int | required; dispatch board / workflow column order |
| is_active | Check | default 1; inactive statuses hidden from new loads; the last active status of a category can't be disabled |
| color | Select | Blue\nCyan\nGreen\nYellow\nOrange\nRed\nPink\nPurple\nGray | badge color |
| customer_label | Data | shown on the customer portal; defaults to status_name |
| carrier_label | Data | shown on the carrier portal; defaults to status_name |
| billable_cancellation | Check | e.g. TONU; allows Cancelled → Billing |
| edi_214_code | Data | optional, max 2 chars (Phase 8) |
| description | Small Text | |

**Default seeded statuses (sequence → category):** Draft (10 → Draft), Quoting (20 → Planning), Tendered (30 → Tendering), Confirmed (40 → Covered), In Transit (50 → In Transit), Delivered (60 → Delivered), Invoiced (70 → Billing), Cancelled (90 → Cancelled). Each is the default for its category. Dispatched, Closed and TONU defaults are added with #6. Seed through `install.py` plus a patch, not fixtures.

**Load Order** (`load_order`) — submittable, naming: `LOAD-.YYYY.-.#####`
| fieldname | fieldtype | options / notes |
|---|---|---|
| naming_series | Series | LOAD-.YYYY.-.##### |
| status | Link | Load Status | required; default Draft |
| shipper | Link | Shipper | required |
| load_type | Select | FTL\nLTL\nPartial |
| commodity | Link | Commodity | |
| weight | Float | lbs |
| pieces | Int | |
| po_number | Data | Customer PO / Reference |
| origin | Link | TMS Location | required |
| destination | Link | TMS Location | required |
| stops | Table | Load Stop Detail | child table |
| assigned_carrier | Link | Carrier | |
| assigned_driver | Link | TMS Driver | filter by carrier |
| assigned_vehicle | Link | TMS Vehicle | filter by carrier |
| sell_rate | Currency | Customer charges (linehaul) |
| buy_rate | Currency | Carrier cost (linehaul) |
| fsc_sell | Currency | FSC billed to customer |
| fsc_buy | Currency | FSC paid to carrier |
| accessorials | Table | Load Accessorial Detail | schema reserved in Phase 2; logic in Phase 3 |
| total_sell | Currency | computed: sell_rate + fsc_sell + customer accessorials |
| total_buy | Currency | computed: buy_rate + fsc_buy + carrier accessorials |
| margin | Currency | total_sell − total_buy |
| margin_pct | Percent | margin / total_sell |
| rate_override | Check | if checked: skip auto-rating via `get_rate()` **and** skip total/margin recompute (dispatcher owns all rate fields) |
| dispatcher | Link | User | assigned dispatcher |
| pickup_date | Date | |
| delivery_date | Date | |
| pod_signature | Attach | schema reserved in Phase 2; used in Phase 6 |
| notes | Text | |
| status_log | Table | Load Status Log | child, read-only |
| amended_from | Link | Load Order | required for submittable |

**Load Stop Detail** (child of Load Order)
| fieldname | fieldtype | options |
|---|---|---|
| sequence | Int | display order |
| location | Link | TMS Location |
| stop_type | Select | Pickup\nDelivery\nStop |
| scheduled_datetime | Datetime | |
| actual_datetime | Datetime | |
| contact_name | Data | |
| contact_phone | Phone | |
| instructions | Small Text | |

**Load Status Log** (child of Load Order, read-only, auto-appended)
| fieldname | fieldtype |
|---|---|
| timestamp | Datetime |
| status | Link / Load Status |
| updated_by | Link / User |
| notes | Small Text |

**Tender** (`tender`) — naming: `TNDR-.YYYY.-.#####`
| fieldname | fieldtype | options / notes |
|---|---|---|
| naming_series | Series | TNDR-.YYYY.-.##### |
| load_order | Link | Load Order | required |
| carrier | Link | Carrier | required |
| offered_rate | Currency | buy rate offered to carrier |
| status | Select | Pending\nAccepted\nRejected\nExpired\nCancelled |
| expiry_datetime | Datetime | auto-set: now + 2 hours |
| response_datetime | Datetime | when carrier responded |
| responded_by | Data | carrier contact name |
| notes | Text | |

**Trip** (`trip`) — naming: `TRIP-.YYYY.-.#####`
| fieldname | fieldtype | options / notes |
|---|---|---|
| naming_series | Series | TRIP-.YYYY.-.##### |
| driver | Link | TMS Driver | required |
| vehicle | Link | TMS Vehicle | required |
| trip_date | Date | required |
| status | Select | Planned\nIn Progress\nCompleted |
| loads | Table | Trip Sheet Detail | |
| total_miles | Float | sum of child miles |
| notes | Text | |

**Trip Sheet Detail** (child of Trip)
| fieldname | fieldtype |
|---|---|
| load_order | Link / Load Order |
| origin | Link / TMS Location |
| destination | Link / TMS Location |
| miles | Float |
| sequence | Int |

**Status workflow for Load Order:** the default statuses follow the category order in *Load Lifecycle — Status Categories* above. **Never compare status names in code.** Read the category (`frappe.db.get_value("Load Status", status, "category")`, or a fetched `status_category` field), and pick target statuses with `is_default_for_category`.

**Controller logic** (`load_order.py` → calls `services/load.py` and `services/load_lifecycle.py`):
- `validate()`: compute `total_sell`, `total_buy`, `margin`, `margin_pct` unless `rate_override` is set.
- `on_update_after_submit()`: append a `Load Status Log` entry whenever `status` changes.
- `before_submit()`: require at least one stop; require `shipper` and `origin` and `destination`.
- Status changes on a saved load must come through the lifecycle service (`load.flags.via_lifecycle`). Setting `status` directly is rejected once #6 lands.

**Tender creation:** Do **not** auto-create a Tender on Load Order `on_submit`. Submit only validates and moves the load into the workflow (the status stays in the Draft/Planning category until a dispatcher acts). Create tenders through the Desk action or the API `tender_load(load_order, carrier, offered_rate)` when the dispatcher selects a carrier; this moves the load to the default **Tendering** status. When a Tender is Accepted, move the load to the default **Covered** status through the lifecycle service and copy the carrier and buy rate onto the load. On reject or expiry, move it back to **Planning**.

**Dispatch Board:** Custom page (`/vecto/dispatch`) rendering Load Orders grouped by status in Kanban columns. Filter bar: date range, dispatcher, carrier, load type. Each card shows: load name, shipper, origin → destination, carrier, status badge.

**Hooks to add to `hooks.py`:**
```python
doc_events = {
    "Tender": {
        "on_update": "vecto.vecto.doctype.tender.tender.sync_load_order_status",
    },
}
scheduler_events = {
    "hourly": ["vecto.tasks.expire_pending_tenders"],  # Pending → Expired when past expiry_datetime
}
```

**Deliverable check:** Create a load, tender it to a carrier, mark accepted, dispatch to driver, update status to Delivered — all steps reachable from the dispatch board.

---

### Phase 3 — Rate Engine & Quoting
**Goal:** Auto-calculate customer sell rate and carrier buy rate when a load is created or quoted.

**Rate Sheet** (`rate_sheet`) — naming: `RS-.YYYY.-.#####`
| fieldname | fieldtype | options / notes |
|---|---|---|
| naming_series | Series | RS-.YYYY.-.##### |
| rate_sheet_name | Data | title_field |
| party_type | Select | Customer\nCarrier |
| shipper | Link | Shipper | shown if party_type = Customer |
| carrier | Link | Carrier | shown if party_type = Carrier |
| rate_type | Select | Customer Sell\nCarrier Buy |
| effective_date | Date | required |
| expiry_date | Date | |
| is_active | Check | default 1 |
| lines | Table | Rate Line Detail | |

**Rate Line Detail** (child of Rate Sheet)
| fieldname | fieldtype | options |
|---|---|---|
| origin_type | Select | Zip\nState\nZone |
| origin_value | Data | zip / state abbrev / zone name |
| destination_type | Select | Zip\nState\nZone |
| destination_value | Data | |
| equipment_type | Select | Dry Van\nReefer\nFlatbed\nStep Deck\nLTL |
| mode | Select | FTL\nLTL\nPartial |
| base_rate | Currency | |
| rate_unit | Select | Per Mile\nFlat\nPer CWT\nPer Hundredweight |
| min_charge | Currency | floor charge |

**FSC Table** (`fsc_table`)
| fieldname | fieldtype | options / notes |
|---|---|---|
| table_name | Data | title_field |
| effective_date | Date | |
| is_active | Check | only one active FSC Table at a time — `validate()` deactivates others or throws |
| lines | Table | FSC Line Detail | |

**FSC Line Detail** (child of FSC Table)
| fieldname | fieldtype | notes |
|---|---|---|
| diesel_price_low | Currency | $/gallon lower bound |
| diesel_price_high | Currency | $/gallon upper bound |
| surcharge_rate | Percent | % of linehaul |

**Accessorial** (`accessorial`)
| fieldname | fieldtype | options |
|---|---|---|
| accessorial_name | Data | title_field |
| charge_type | Select | Flat\nPer Unit\nPercent of Linehaul |
| default_amount | Currency | |
| billable_to | Select | Customer\nCarrier\nBoth |
| description | Small Text | |

**Load Accessorial Detail** (child of Load Order — add to Phase 2 schema)
| fieldname | fieldtype | options |
|---|---|---|
| accessorial | Link | Accessorial |
| description | Data | auto-filled from Accessorial |
| quantity | Float | default 1 |
| rate | Currency | |
| total | Currency | qty × rate |
| billable_to | Select | Customer\nCarrier\nBoth |

**Quote** (`quote`) — naming: `QT-.YYYY.-.#####`
| fieldname | fieldtype | options / notes |
|---|---|---|
| naming_series | Series | QT-.YYYY.-.##### |
| shipper | Link | Shipper | required |
| origin | Link | TMS Location | |
| destination | Link | TMS Location | |
| equipment_type | Select | Dry Van\nReefer\nFlatbed\nStep Deck\nLTL |
| commodity | Link | Commodity | |
| weight | Float | lbs |
| pieces | Int | |
| quoted_sell_rate | Currency | |
| quoted_buy_rate | Currency | |
| fsc_sell | Currency | |
| fsc_buy | Currency | |
| total_sell | Currency | |
| total_buy | Currency | |
| margin | Currency | |
| margin_pct | Percent | |
| status | Select | Draft\nSent\nWon\nLost\nExpired |
| expiry_date | Date | |
| load_order | Link | Load Order | filled when Won → Load Order created |
| notes | Text | |

**Rating engine** (`vecto/services/rating.py`) — key function signature:
```python
def get_rate(origin_zip, origin_state, destination_zip, destination_state,
             equipment_type, mode, weight=None, shipper=None, carrier=None):
    """
    Returns dict:
    {
        "sell_rate": float, "buy_rate": float,
        "fsc_sell": float, "fsc_buy": float,
        "total_sell": float, "total_buy": float,
        "margin": float, "margin_pct": float,
        "rate_sheet_sell": str, "rate_sheet_buy": str,  # names of matched sheets
    }
    Match priority: zip (exact) > state > zone.
    If no rate found, returns zeros (do not raise — let dispatcher fill manually).
    """
```

**API endpoint** (`api/v1/quotes.py`):
```python
@frappe.whitelist()
def get_rate(origin, destination, equipment_type, mode="FTL", weight=None, shipper=None):
    """Instant rate lookup for a lane.
    origin/destination = TMS Location names.
    Resolves zip/state from each location, then calls vecto.services.rating.get_rate(...).
    """
```

The service function takes zip/state; the API takes TMS Location names and adapts.
**Quote → Load Order:** Custom button "Create Load Order" on Quote (status = Won) → creates Load Order with all rate fields pre-filled, links back to quote.

**Deliverable check:** Create a Rate Sheet with a lane, set an FSC table, create a Load Order on that lane — system populates sell/buy/margin automatically.

---

### Phase 4 — Carrier Compliance & Scorecards
**Goal:** Track carrier compliance documents, block non-compliant carriers from being tendered loads, and auto-update performance scorecards.

**Carrier Certificate** (`carrier_certificate`)
| fieldname | fieldtype | options / notes |
|---|---|---|
| carrier | Link | Carrier | required |
| certificate_type | Select | General Liability\nCargo\nW9\nAuthority\nOperating Agreement |
| insurer | Data | |
| policy_number | Data | |
| issue_date | Date | |
| expiry_date | Date | required |
| status | Select | Valid\nExpiring\nExpired | auto-set by scheduled task |
| attachment | Attach | |
| notes | Small Text | |

Status auto-logic: `Valid` if expiry > today+30; `Expiring` if today < expiry ≤ today+30; `Expired` if expiry ≤ today.

**Carrier Packet** (`carrier_packet`)
| fieldname | fieldtype | options |
|---|---|---|
| carrier | Link | Carrier | required |
| status | Select | Requested\nSubmitted\nApproved\nRejected |
| submission_date | Date | |
| reviewed_by | Link | User | |
| review_date | Date | |
| checklist | Table | Carrier Packet Item Detail | |
| notes | Text | |

**Carrier Packet Item Detail** (child of Carrier Packet)
| fieldname | fieldtype |
|---|---|
| document_type | Data |
| is_required | Check |
| is_submitted | Check |
| attachment | Attach |
| notes | Small Text |

**Carrier Lane** (`carrier_lane`)
| fieldname | fieldtype | options |
|---|---|---|
| carrier | Link | Carrier | required |
| origin_type | Select | Zip\nState\nZone |
| origin_value | Data | |
| destination_type | Select | Zip\nState\nZone |
| destination_value | Data | |
| equipment_type | Select | Dry Van\nReefer\nFlatbed\nStep Deck\nLTL |
| capacity_per_week | Int | loads/week available |
| preferred_buy_rate | Currency | |

**Scorecard fields to add to Carrier doctype** (Phase 4 addition):
| fieldname | fieldtype | notes |
|---|---|---|
| on_time_pickup_pct | Percent | read-only, updated by scheduler |
| on_time_delivery_pct | Percent | read-only |
| loads_completed | Int | last 90 days |
| claims_count | Int | last 90 days |
| carrier_score | Percent | 50% OTD delivery + 30% OTD pickup + 20% (1−claims_rate) |
| scorecard_updated_on | Datetime | |

**Regional compliance (ADR-0005, #54–#60):** in addition to certificates, carriers are verified against the regulator of every region a load touches. That means Compliance Region, Carrier Regulatory ID (child of Carrier), Compliance Policy, Compliance Snapshot, and Compliance Event, with one adapter per provider in `vecto/integrations/compliance/` (`lookup`, `check`, `changes_since`). FMCSA (QCMobile + open data) is the first region. Each carrier gets a per-region status: Compliant / Warning / Blocked / Unverified. The gate runs on tender **and** dispatch, raises `CARRIER_NOT_COMPLIANT` with the failing rules as the hint, and allows an audited admin override per load.

**Certificate gate** — implement in `services/compliance.py` and call it from `tender.py` → `validate()`:
```python
required_cert_types = ["General Liability", "Cargo", "Authority"]
expired = frappe.db.get_all(
    "Carrier Certificate",
    filters={"carrier": self.carrier, "certificate_type": ["in", required_cert_types], "status": "Expired"},
    fields=["certificate_type"],
)
if expired:
    types = ", ".join(c.certificate_type for c in expired)
    frappe.throw(frappe._("Carrier has expired certificates: {0}").format(types))
```

**Scheduled task (daily)** — add to `hooks.py`:
```python
scheduler_events = {
    "daily": ["vecto.tasks.refresh_carrier_scorecards"],
}
```
Implement in `vecto/tasks.py`: update all carrier scores + set certificate statuses + email alerts for expiring certs.

**Deliverable check:** Expire a carrier's insurance cert — system blocks tendering a load to them. Scorecard updates after load is marked Delivered.

---

### Phase 5 — Billing, Invoicing & Settlements
**Goal:** One-click invoice generation from a delivered load; carrier settlements create ERPNext Purchase Invoices.

**Freight Invoice** (`freight_invoice`) — submittable, naming: `FINV-.YYYY.-.#####`
| fieldname | fieldtype | options / notes |
|---|---|---|
| naming_series | Series | FINV-.YYYY.-.##### |
| load_order | Link | Load Order | required |
| shipper | Link | Shipper | auto-filled from Load Order |
| invoice_date | Date | default: today |
| due_date | Date | based on payment terms |
| payment_terms | Link | Payment Terms Template | from Shipper / TMS Settings |
| status | Select | Draft\nSubmitted\nPaid\nCancelled |
| lines | Table | Freight Invoice Line Detail | |
| subtotal | Currency | sum of lines |
| tax_amount | Currency | |
| total | Currency | subtotal + tax |
| erpnext_sales_invoice | Link | Sales Invoice | filled on submit |
| notes | Text | |
| amended_from | Link | Freight Invoice | |

**Freight Invoice Line Detail** (child of Freight Invoice)
| fieldname | fieldtype | options |
|---|---|---|
| charge_type | Select | Linehaul\nFSC\nAccessorial\nOther |
| description | Data | |
| qty | Float | default 1 |
| rate | Currency | |
| amount | Currency | qty × rate, read-only |

**Carrier Settlement** (`carrier_settlement`) — submittable, naming: `CSTL-.YYYY.-.#####`
| fieldname | fieldtype | options / notes |
|---|---|---|
| naming_series | Series | CSTL-.YYYY.-.##### |
| load_order | Link | Load Order | required |
| carrier | Link | Carrier | auto-filled |
| settlement_date | Date | default: today |
| status | Select | Draft\nSubmitted\nPaid\nCancelled |
| lines | Table | Carrier Settlement Line Detail | |
| total | Currency | sum of lines |
| erpnext_purchase_invoice | Link | Purchase Invoice | filled on submit |
| amended_from | Link | Carrier Settlement | |

**Carrier Settlement Line Detail** (child)
| fieldname | fieldtype | options |
|---|---|---|
| charge_type | Select | Linehaul\nFSC\nAccessorial\nOther |
| description | Data | |
| qty | Float | |
| rate | Currency | |
| amount | Currency | |

**Invoice generation** (`api/v1/billing.py`):
```python
@frappe.whitelist()
def create_freight_invoice(load_order):
    """Build and save (not submit) a Freight Invoice from a delivered Load Order."""

@frappe.whitelist()
def create_carrier_settlement(load_order):
    """Build and save a Carrier Settlement from a delivered Load Order."""

@frappe.whitelist()
def get_invoice(load):
    """Return Freight Invoice summary for a Load Order (or None)."""
```

**On submit hooks** — add to `hooks.py`:
```python
doc_events = {
    ...
    "Freight Invoice": {"on_submit": "vecto.vecto.doctype.freight_invoice.freight_invoice.create_erpnext_sales_invoice"},
    "Carrier Settlement": {"on_submit": "vecto.vecto.doctype.carrier_settlement.carrier_settlement.create_erpnext_purchase_invoice"},
    "Load Order": {
        "on_update_after_submit": "vecto.vecto.doctype.load_order.load_order.maybe_auto_invoice_on_delivery",
    },
}
```

The ERPNext Sales Invoice / Purchase Invoice creation functions map: Shipper → Customer via `Shipper.erpnext_customer` (create Customer if missing and store the link), Carrier → Supplier via `Carrier.erpnext_supplier` (same pattern), lines → Sales/Purchase Invoice Items, default accounts from TMS Settings.

**Deliverable check:** Mark a load Delivered → create and submit Freight Invoice → GL entry appears in ERPNext Chart of Accounts under freight revenue.

---

### Phase 6 — Track & Trace & Document Management
**Goal:** Live event timeline on each load; auto-notify customers; digital POD with e-signature.

**Load Event** (`load_event`)
| fieldname | fieldtype | options / notes |
|---|---|---|
| load_order | Link | Load Order | required |
| event_type | Select | Pickup\nDelivery\nCheck Call\nDelay\nException\nCustom |
| timestamp | Datetime | default: now |
| location_text | Data | free-text location description |
| latitude | Float | |
| longitude | Float | |
| notes | Text | |
| notified | Check | set after sending customer notification |

> Do **not** add a custom `created_by` field — use Frappe's standard `owner` (and `modified_by`) instead.

**GPS Log** (`gps_log`) — high-volume; do not use List View
| fieldname | fieldtype |
|---|---|
| load_order | Link / Load Order |
| driver | Link / TMS Driver |
| timestamp | Datetime |
| latitude | Float |
| longitude | Float |
| speed_mph | Float |
| heading | Int |

**Shipment Document** (`shipment_document`)
| fieldname | fieldtype | options |
|---|---|---|
| load_order | Link | Load Order |
| document_type | Select | BOL\nPOD\nRate Confirmation\nFreight Invoice\nOther |
| file | Attach | required |
| uploaded_by | Link | User | auto-set |
| upload_date | Date | default: today |
| is_verified | Check | |
| notes | Small Text | |

**Print Formats** (implement as Frappe Jinja HTML print formats):
- `Vecto BOL` — on Load Order: shipper, carrier, origin/destination, stops table, commodity, weight, pieces, special instructions, signature line
- `Vecto Rate Confirmation` — on Tender: carrier details, load details, offered rate, accessorials, payment terms, acceptance signature line
- `Vecto POD` — on Load Order: all stops with actual datetimes, receiver name, signature (image from `pod_signature` field)

**Notifications** — add to `hooks.py`:
```python
doc_events = {
    ...
    "Load Event": {"after_insert": "vecto.vecto.doctype.load_event.load_event.send_notifications"},
}
```
`send_notifications`: if event_type = Pickup → `frappe.sendmail` to shipper contacts; if Delivery → email with link to POD print format.

**API** (`api/v1/tracking.py`):
```python
@frappe.whitelist(allow_guest=True)
def log_position(load_order, latitude, longitude, speed_mph=None, heading=None):
    """Telematics webhook. Validates X-Vecto-Key header before inserting GPS Log."""

@frappe.whitelist()
def add_load_event(load_order, event_type, notes=None, latitude=None, longitude=None):
    """Add a Load Event from desk or driver mobile app."""
```

**Deliverable check:** Add a Pickup event to a load → customer gets an email notification → Delivery event → POD print format renders with all stops and signature line.

---

### Phase 7 — Customer & Carrier Portals
**Goal:** External-facing portals for customers and carriers using Frappe Web Portal — no separate frontend required.

**Customer Portal pages:**
- `/shipments` — list of their Load Orders (filtered by customer = portal user's linked customer)
- `/shipments/<load_order_name>` — detail view: status, stops, events timeline, documents
- `/quotes/new` — web form to request a new quote (creates Quote with status Draft)
- `/invoices` — their Freight Invoices with download link

**Carrier Portal pages:**
- `/available-loads` — Load Orders in the `Tendering` status category with no carrier accepted yet (public load board)
- `/my-loads` — their accepted and in-progress loads
- `/settlements` — their Carrier Settlements
- `/onboarding` — Carrier Packet web form for self-service onboarding

**Portal user linking:**
- `TMS Customer` portal user → `Shipper.portal_user`
- `TMS Carrier Portal` portal user → `Carrier.portal_user`

**Permission query conditions:** Each portal page must filter using `get_permission_query_conditions` so users only see their own records — never expose all records to portal users.

**Deliverable check:** Log in as a portal customer → see only their shipments → request a quote → quote appears in desk for dispatcher.

---

### Phase 8 — Analytics, Reporting & Integrations
**Goal:** Executive dashboards, EDI support, load board API integration, and REST API for external systems.

**Reports to create** (Script Reports or Query Reports):
- `Revenue & Margin Summary` — by customer, lane, date range; columns: loads, revenue, cost, margin $, margin %
- `On-Time Performance` — by carrier; OTD pickup %, OTD delivery %, total loads
- `Lane Profitability` — origin/destination pair; avg sell, avg buy, avg margin, load count
- `Carrier Aging Payables` — outstanding Carrier Settlements by age bucket
- `Customer Aging Receivables` — outstanding Freight Invoices by age bucket
- `Load Volume Trend` — loads per week/month, filterable by customer / carrier / equipment type

**Dashboards:**
- `TMS Operations Dashboard` — active loads by status (donut), loads this week vs. last week (bar), top 5 carriers by volume
- `Finance Dashboard` — revenue MTD, cost MTD, margin MTD, aging receivables total

**EDI (Phase 8 later):**
- 204 (Load Tender) inbound → create Load Order
- 990 (Response to Tender) outbound → send when Tender accepted/rejected
- 214 (Shipment Status) outbound → send on each Load Event
- 210 (Freight Invoice) outbound → send on Freight Invoice submit
- Parser lives in `vecto/edi/` — each transaction set has its own module.

**Load Board API integration:**
- DAT API: post available loads (status category `Tendering`, not yet covered), pull spot rates for lane benchmarking
- Truckstop API: same pattern
- Configured in TMS Settings with API key fields

**REST API (public, token-auth via `X-Vecto-Key` header where noted):**
All custom endpoints are versioned under `vecto.api.v1.*`:

| Method | Endpoint | Module |
|---|---|---|
| GET | `/api/method/vecto.api.v1.loads.get_load_status?load=<name>` | `loads.py` |
| POST | `/api/method/vecto.api.v1.loads.create_load` | `loads.py` |
| GET | `/api/method/vecto.api.v1.loads.list_loads` | `loads.py` |
| POST | `/api/method/vecto.api.v1.loads.tender_load` | `loads.py` |
| POST | `/api/method/vecto.api.v1.tracking.log_position` | `tracking.py` (guest + X-Vecto-Key) |
| POST | `/api/method/vecto.api.v1.tracking.add_load_event` | `tracking.py` |
| GET | `/api/method/vecto.api.v1.quotes.get_rate?origin=&destination=&equipment_type=` | `quotes.py` |
| GET | `/api/method/vecto.api.v1.carriers.list_carriers` | `carriers.py` |
| GET | `/api/method/vecto.api.v1.billing.get_invoice?load=<name>` | `billing.py` |
| POST | `/api/method/vecto.api.v1.billing.create_freight_invoice` | `billing.py` |
| POST | `/api/method/vecto.api.v1.billing.create_carrier_settlement` | `billing.py` |

Standard Frappe resource API (`/api/resource/Load Order/<name>`) remains available for authenticated desk users but must not be used from external integrations — use the versioned endpoints instead.

**Deliverable check:** Revenue & Margin Summary report runs for a date range and exports to Excel; a Load Order created via the REST API appears in the dispatch board.

---

### Phase 9 (Future) — Regional Compliance App
**Reconciled with ADR-0005:** the compliance **framework and the US/FMCSA adapter live in core** (Phase 4). Further regions (#44: Canada, Mexico, India, Europe/UK, in that order) and operational rules (IFTA, HOS, permits, tachograph) go in the separate `vecto_regional` app or per-region integration apps (#73), plugging into the core adapter interface.

**Goal:** Separate Frappe app (`vecto_regional`) that extends Vecto with jurisdiction-specific compliance rules, without polluting the core app.

**Why a separate app:** Regional rules vary widely and change frequently. Keeping them in a dedicated app means the core `vecto` app stays clean and region-agnostic — operators in different countries install only what applies to them.

**App structure:**
```
vecto_regional/
├── vecto_regional/
│   ├── overrides/          # extend_doctype_class entries
│   ├── fixtures/           # region-specific master data (permit types, tax codes)
│   ├── us/                 # US-specific modules
│   │   ├── ifta.py         # IFTA fuel tax reporting
│   │   ├── hos.py          # Hours of Service validation
│   │   └── ucr.py          # UCR registration tracking
│   ├── ca/                 # Canada
│   └── eu/                 # EU / CMR
└── pyproject.toml
```

**Compliance areas to cover per region:**

*United States (FMCSA / DOT):*
- IFTA fuel tax: miles by jurisdiction per quarter → quarterly IFTA report
- HOS (Hours of Service): driver hours validation against 11-hour / 14-hour / 70-hour rules; warn dispatcher before assigning a trip that would violate
- UCR (Unified Carrier Registration): annual renewal tracking on Carrier
- State permits: oversized/overweight load permits — permit number, issuing state, expiry, linked Load Order
- FMCSA SaferWatch API integration: pull carrier safety rating and OOS % automatically

*Canada:*
- IFTA (same structure, different jurisdictions)
- Bilingual BOL / POD (English + French)
- Province-specific weight limits

*EU / International:*
- CMR consignment note (replaces BOL)
- Tachograph / digital tacho compliance for drivers
- Cabotage rule tracking (max 3 operations in 7 days)
- GDPR: data retention rules on Load Event / GPS Log (auto-purge after configurable days)

**Integration with core `vecto`:**
- `required_apps = ["vecto"]` in `vecto_regional/hooks.py`
- Extend `Carrier` doctype via `extend_doctype_class` to add regional compliance fields (no schema change to core)
- Add scheduled tasks to `vecto_regional/tasks.py` (IFTA aggregation, HOS checks)
- Regional fields stored in child doctypes linked to core doctypes — never patch core doctype JSON

**When to build:** After Phase 6 is complete and the operator's jurisdiction(s) are confirmed. Build only the regions needed; the app is designed to be installed optionally.

---

## Known Gaps: develop vs this file

The current code doesn't yet match the merged rules. Fix these in small PRs, each with a brief:

- `hooks.py`: `app_license = "mit"` → `"agpl-3.0"`; add a `LICENSE` file.
- `Load Status` has no `category`, `is_default_for_category`, labels or `billable_cancellation`; it is seeded via `fixtures/load_status.json` as well as `install.py`. Move seeding to `install.py` plus a patch and drop the fixture.
- Hard-coded status names: `api/v1/loads.py` (`"Draft"`, `"Quoting"`, `"Tendered"`), `doctype/tender/tender.py` (`"Confirmed"`), `doctype/load_order/load_order.py` (`"Draft"`). Replace them with category lookups.
- No `services/` package yet. Move `utils/load.py` into it and add `services/load_lifecycle.py` and `services/status.py`.
- No `dry_run` / `idempotency_key` / `{code, message, hint}` errors on `tender_load`.
- Missing roles: Account Manager, Tracking Rep, Vecto Agent.
- No `patches/` for schema/data changes.
- No `LICENSE`, `AGENTS.md` or `docs/` on `develop`; these exist only on `main`.

---

## Backlog (not Phase 2)

Keep these out of core until the load file ships. Prefer a later phase or a separate app/addon:

- AI email / PDF / EDI order capture (Revenova Artimus, Qargo Qi)
- Mileage / PC*Miler / groupage route optimization
- Visual drag-drop planner (McLeod-style) beyond the Kanban dispatch board
- SMS / appointment scheduling workflows
- Native driver mobile app and ePOD OCR
- ELD / HOS / IFTA (Phase 9 `vecto_regional`)
- Emissions reporting

---

## Development Workflow

### Per-feature cycle
1. Branch off `develop`: `git checkout -b feat/<phase>-<short-description>`
2. If new doctypes: add JSON under `vecto/vecto/doctype/` (or create in Desk with Developer Mode) → commit schema JSON.
3. For Roles / Workspace / Print Formats: list in `hooks.py` `fixtures`, then `bench --site localhost.v16 export-fixtures --app vecto`.
4. Implement controller, client script, API endpoints in Cursor.
5. `bench --site localhost.v16 migrate` after any schema change.
6. Test manually in browser; run `bench --site localhost.v16 run-tests --app vecto` before PR.
7. Commit after every feature: schema JSON first (separate commit), then controller logic.
8. Merge to `develop` via PR.

### Useful bench commands (run from `frappe-v16/` bench root)
```bash
# Install app on site (requires ERPNext)
bench --site localhost.v16 install-app vecto

# Apply migrations after schema changes
bench --site localhost.v16 migrate

# Export hooked fixtures (Roles, Workspace, etc.) — not DocType schema
bench --site localhost.v16 export-fixtures --app vecto

# Open Python console (test frappe.db calls interactively)
bench --site localhost.v16 console

# Watch JS/CSS for hot reload during frontend work
bench watch

# Run app tests
bench --site localhost.v16 run-tests --app vecto

# Restart workers (after hooks.py changes)
bench restart
```

### Cursor workflow tips
- Start each new controller file with: `# Implements: <Phase X> — <Doctype name>` then paste the spec from this file.
- Use `@frappe.whitelist()` stubs first, then ask Cursor to fill in logic.
- When implementing child table logic, always reference the parent doctype name explicitly in prompts.
- For scheduled tasks, prototype logic in `bench console` first, then move to the task file.

## Environment

- Frappe version: v16
- Python: ≥ 3.10
- Node: ≥ 18 (for desk JS bundling)
- Bench: latest stable
- Default site name (local dev): `localhost.v16` (also used: `vecto-test` for frappe-only smoke tests — full Vecto install requires ERPNext)
- Bench root: `~/develop/frappe-v16/`
- App path: `~/develop/frappe-v16/apps/vecto/`
- Line length: 110 (ruff + `.editorconfig`)