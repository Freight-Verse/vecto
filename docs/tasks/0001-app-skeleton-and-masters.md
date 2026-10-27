# Task 0001: App skeleton, roles, settings and base masters
Issues: #4 (app skeleton), part of #61 (vocabulary masters) · Branch: `feat/0001-app-skeleton` · Phase: M0 · Module: Vecto

## Goal
A clean `vecto` Frappe app that installs on a Frappe/ERPNext **v16** site, with the module layout,
roles, settings and the first configurable masters every later task depends on.

## In scope
- The app itself, its module and package layout, license metadata.
- Roles, Vecto Settings, and five masters: Mode, Equipment Type, Stop Type, Reference Type, Facility.
- Default master records created on install (idempotent), never as fixtures.
- A "Vecto" workspace linking the above.
- Tests for install, defaults and validations.

## Out of scope (do NOT build)
- Loads, statuses, transitions (tasks 0002, 0003).
- Carriers, rating, tendering, chat, MCP, the Vue SPA.
- CI workflows (separate task), any UI beyond Desk forms and the workspace.

## Design

### App
- Create with `bench new-app vecto`: title **Vecto**, description "Open-source TMS built on Frappe and
  ERPNext", publisher **FreightVerse**, email hello@anupamvs.dev, license **agpl-3.0**.
- `hooks.py`: `required_apps = ["erpnext"]`, `app_license = "agpl-3.0"`, `after_install = "vecto.install.after_install"`.
- Repo root keeps the existing docs, `LICENSE`, `.cursor/`, `.github/`. Do not overwrite them.

### Modules (`modules.txt`) and package folders
| Module | Folder | Purpose |
|---|---|---|
| Vecto | `vecto/vecto/` | Core: settings, masters, loads |
| Carrier | `vecto/carrier/` | Carriers, compliance (later) |
| Rating | `vecto/rating/` | Rates, quotes (later) |
| Tracking | `vecto/tracking/` | Events, ETA (later) |
| Billing | `vecto/billing/` | Invoicing, settlement (later) |
| EDI | `vecto/edi/` | EDI (later) |
| Agent | `vecto/agent/` | Chat, tool-call audit (later) |

Plain packages with an `__init__.py` and a one-line module docstring:
`vecto/services/`, `vecto/mcp/`, `vecto/api/`, `vecto/integrations/`.

### Roles (created in `after_install`, desk access on)
Vecto Admin · Dispatcher · Account Manager · Billing · Tracking Rep · Vecto Agent.
(Carrier and Customer portal roles come with the portals.)

### Vecto Settings (Single, module Vecto)
| Field | Type | Notes |
|---|---|---|
| default_company | Link Company | required |
| default_currency | Link Currency | default from company |
| weight_uom | Link UOM | default "Pound" if it exists, else "Kg" |
| distance_uom | Link UOM | default "Mile" if it exists, else "Km" |
| default_time_zone | Autocomplete | options = IANA zones from `zoneinfo.available_timezones()` sorted; default system time zone |
| section: Assistant | Section Break | |
| enable_assistant | Check | default 0 |
| llm_provider | Select | `Anthropic\nOpenAI\nOpenAI-compatible` |
| llm_model | Data | |
| llm_api_key | Password | never returned by any API |
| llm_base_url | Data | only for OpenAI-compatible |
| section: MCP | Section Break | |
| enable_mcp | Check | default 0 |

Permissions: Vecto Admin read/write; System Manager read/write; others none.

### Masters (all module Vecto, `track_changes = 1`, autoname `field:<name field>`)
| DocType | Fields | Rules |
|---|---|---|
| **Mode** | `mode_name` Data (unique), `description` Small Text, `enabled` Check (1) | |
| **Equipment Type** | `equipment_type_name` Data (unique), `modes` Table MultiSelect → child **Equipment Type Mode** (`mode` Link Mode), `length` Float + `length_uom` Link UOM, `max_weight` Float + `weight_uom` Link UOM, `enabled` Check | `max_weight` ≥ 0 |
| **Stop Type** | `stop_type_name` Data (unique), `category` Select `Pickup\nDelivery\nOther` (required), `enabled` Check | category is fixed; names are user-editable |
| **Reference Type** | `reference_type_name` Data (unique), `description` Small Text, `enabled` Check | |
| **Facility** | `facility_name` Data (required), `customer` Link Customer, `time_zone` Autocomplete (IANA, required), `latitude` Float, `longitude` Float, `opening_hours` Small Text, `appointment_required` Check, `dock_notes` Small Text, `enabled` Check | autoname `naming_series:` `FAC-.#####`; address and contacts through Frappe's standard Address/Contact dynamic links; `time_zone` must be a valid IANA zone; lat in −90..90, long in −180..180 |

Permissions for masters: Vecto Admin full; Dispatcher, Account Manager, Tracking Rep, Billing read;
Dispatcher and Account Manager can also create/write **Facility**.

### Defaults created by `vecto/install.py::after_install()` (and the same function called from a patch, so existing sites get them)
- Modes: FTL, LTL, Partial, Intermodal, Drayage.
- Equipment Types: Dry Van 53', Reefer 53', Flatbed 48', Step Deck, Power Only, Box Truck 26'.
- Stop Types: Pickup (Pickup), Delivery (Delivery), Cross-dock (Other), Fuel (Other).
- Reference Types: PO, BOL, PRO, Pickup #, Delivery #, Seal #.
- Only insert a record if no record with that name exists — never overwrite user edits.

### Code placement
- Validation logic lives in `vecto/services/masters.py` (e.g. `validate_time_zone(tz: str) -> None`,
  `validate_coordinates(lat, lng) -> None`); controllers call these.
- No MCP tools or REST endpoints in this task.

### Patches
- `vecto.patches.v0_1.create_default_masters` → calls the same installer function.

## Acceptance criteria
- [ ] `bench --site test_site install-app vecto` succeeds on a fresh v16 site with ERPNext.
- [ ] Roles, Vecto Settings and all default master records exist after install.
- [ ] Running the installer twice creates no duplicates and does not change edited records.
- [ ] Facility with an invalid time zone or out-of-range coordinates is rejected with a clear message.
- [ ] A Stop Type cannot be saved without a category.
- [ ] Dispatcher can create a Facility; Billing cannot.
- [ ] `llm_api_key` never appears in `frappe.get_doc("Vecto Settings").as_dict()` output sent to clients.
- [ ] No hard-coded master names anywhere outside `install.py`.

## Tests to write
- `vecto/vecto/tests/test_install.py`: defaults present; idempotent re-run; edited record survives re-run.
- `vecto/vecto/doctype/facility/test_facility.py`: time zone and coordinate validation; permissions per role.
- `vecto/vecto/doctype/stop_type/test_stop_type.py`: category required.

## Notes for the implementer
- Frappe v16 only. Use `frappe.qb` where queries are needed.
- Keep DocType JSON tidy: field order as in the tables above, labels in sentence case.
- Commit as yourself; no attribution trailers (AGENTS.md §1).
