# Task 0002: Load data model and configurable statuses
Issue: #5 (load core data model), part of #6 (statuses) · Branch: `feat/0002-load-data-model` · Phase: M0 · Module: Vecto
Depends on: task 0001 merged.

## Goal
Shipment Orders and multi-stop Loads with commodities, references and charges, plus user-editable
**Load Status** records with a fixed category (ADR-0006). A dispatcher can create a valid load in Desk.

## In scope
- DocTypes: Load Status, Shipment Order, Load, and child tables Load Stop, Load Commodity, Load Reference, Load Charge.
- Default statuses created on install/patch (idempotent).
- Validation and totals in `vecto/services/load.py`.
- Tests.

## Out of scope (do NOT build)
- Status transitions and the lifecycle service (task 0003). In this task `status` is set to the
  default Draft-category status on insert and is **read-only** in the form.
- Carriers, tendering, rating lookups, invoices, MCP tools, SPA screens.

## Design

### Load Status (module Vecto, autoname `field:status_name`, `track_changes`)
| Field | Type | Notes |
|---|---|---|
| status_name | Data | unique, user-editable |
| category | Select | `Draft\nPlanning\nTendering\nCovered\nDispatched\nIn Transit\nDelivered\nBilling\nClosed\nCancelled` — required, fixed list (constant `STATUS_CATEGORIES` in `vecto/services/status.py`) |
| color | Select | `gray\nblue\ngreen\namber\nred\norange\nviolet` |
| sort_order | Int | |
| is_default_for_category | Check | at most one per category (validate) |
| customer_label | Data | shown to customers; defaults to status_name |
| carrier_label | Data | shown to carriers; defaults to status_name |
| edi_214_code | Data | optional, max 2 chars |
| enabled | Check | default 1 |
Rules: every category must keep at least one enabled status; deleting or disabling the last one is blocked.

Default statuses (inserted only if missing): Draft (Draft) · Planned (Planning) · Tendered (Tendering) ·
Covered (Covered) · Dispatched, At Pickup (Dispatched) · Loaded, In Transit, At Delivery (In Transit) ·
Delivered, POD Received (Delivered) · Invoiced, Settled (Billing) · Closed (Closed) · Cancelled, TONU (Cancelled).
The first listed per category is `is_default_for_category = 1`.

### Shipment Order (submittable: no; naming `SO-.YYYY.-.#####`)
| Field | Type |
|---|---|
| customer | Link Customer (required) |
| customer_reference | Data |
| mode | Link Mode (required) |
| requested_pickup_date | Date |
| notes | Text |
| loads | read-only HTML/Table summary via connections (Dashboard link to Load) |

### Load (naming `LD-.YYYY.-.#####`, `track_changes`)
| Field | Type | Notes |
|---|---|---|
| shipment_order | Link Shipment Order | optional |
| customer | Link Customer | required; fetched from shipment order if set |
| mode | Link Mode | required |
| equipment_type | Link Equipment Type | must allow the selected mode |
| status | Link Load Status | read-only; set on insert to the default Draft-category status |
| status_category | Data | read-only, `fetch_from: status.category` |
| currency | Link Currency | default from Vecto Settings |
| stops | Table Load Stop | |
| commodities | Table Load Commodity | |
| references | Table Load Reference | |
| charges | Table Load Charge | |
| total_weight | Float | computed from commodities, in `weight_uom` |
| weight_uom | Link UOM | default from Vecto Settings |
| customer_total | Currency | computed |
| carrier_total | Currency | computed |
| margin | Currency | computed = customer_total − carrier_total |
| margin_percent | Percent | computed; 0 when customer_total is 0 |
| internal_notes | Text | |

**Load Stop** (child): `sequence` Int (required) · `stop_type` Link Stop Type (required) · `stop_category` Data (fetch `stop_type.category`, read-only) · `facility` Link Facility (required) · `time_zone` Data (fetch `facility.time_zone`, read-only) · `appointment_start` Datetime · `appointment_end` Datetime · `appointment_required` Check (fetch `facility.appointment_required`) · `instructions` Small Text · `actual_arrival` Datetime · `actual_departure` Datetime.

**Load Commodity** (child): `description` Data (required) · `pieces` Int · `packaging` Select `Pallets\nCartons\nCrates\nDrums\nLoose\nOther` · `weight` Float (required, > 0) · `weight_uom` Link UOM (required) · `length`/`width`/`height` Float + `dimension_uom` Link UOM · `freight_class` Data (LTL) · `is_hazmat` Check · `un_number` Data (required when hazmat) · `declared_value` Currency.

**Load Reference** (child): `reference_type` Link Reference Type (required) · `value` Data (required) · `stop_sequence` Int (optional: ties a reference to a stop).

**Load Charge** (child): `side` Select `Customer\nCarrier` (required) · `charge_item` Link Item (required; linehaul, fuel and accessorials are ERPNext Items) · `description` Data · `qty` Float (default 1) · `rate` Currency · `amount` Currency (computed qty × rate, read-only).

### Rules (in `vecto/services/load.py`, called from `Load.validate`)
1. At least two stops; at least one stop with category Pickup and one with category Delivery
   (use `stop_category`, never stop type names).
2. Sequences are 1..n with no gaps or duplicates; rows are sorted by sequence on save.
3. The first stop's category is Pickup; the last stop's category is Delivery.
4. `appointment_end` ≥ `appointment_start`; if a facility requires appointments, both are required.
   Appointment times are entered and displayed in the stop's `time_zone` (store as entered and keep
   `time_zone` beside them; document this in the field description).
5. Equipment type must list the load's mode.
6. Commodity weights are converted into the load's `weight_uom` using ERPNext UOM Conversion Factor;
   if a conversion is missing, raise a clear error naming both UOMs.
7. Charge amounts and totals use `flt(value, precision)`; totals rounded to currency precision.
8. `status` cannot be changed through save in this task (the lifecycle service in 0003 will own it);
   attempts to change it raise `frappe.ValidationError`.

### Permissions
| Role | Shipment Order | Load |
|---|---|---|
| Vecto Admin | full | full |
| Dispatcher | create, read, write | create, read, write |
| Account Manager | create, read, write | create, read, write |
| Tracking Rep | read | read, write (stops' actual times only — enforce in service) |
| Billing | read | read |
| Load Status | Vecto Admin full; others read |

### Patches
- `vecto.patches.v0_1.create_default_load_statuses` (same function as install).

## Acceptance criteria
- [ ] A dispatcher can create a Load with 2+ stops, commodities, references and both-side charges; totals and margin compute correctly.
- [ ] Each rule 1–8 above rejects bad input with a specific message.
- [ ] Renaming a status (e.g. "Covered" → "Booked") breaks nothing; all rules use categories.
- [ ] Disabling the last enabled status of a category is blocked.
- [ ] Weights in mixed UOMs total correctly; missing conversion gives a clear error.
- [ ] Tracking Rep cannot change charges or commodities.
- [ ] No hard-coded status, stop type or mode names outside the installer.

## Tests to write
- `vecto/vecto/doctype/load/test_load.py`: happy path; each rule's failure; totals/margin; UOM conversion; status read-only; permissions per role.
- `vecto/vecto/doctype/load_status/test_load_status.py`: category required; one default per category; last-enabled guard; rename safety.

## Notes for the implementer
- Use test helpers to create Customer, Items, Facilities; don't depend on demo data.
- Keep business rules in `services/load.py` with small pure functions (`validate_stops(stops)`,
  `compute_totals(load)`), so they are unit-testable without the DocType.
