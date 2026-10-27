# Task 0003: Configurable load lifecycle
Issue: #6 · Branch: `feat/0003-load-lifecycle` · Phase: M0 · Module: Vecto + Tracking
Depends on: task 0002 merged.

## Goal
Load status changes happen only through one service that enforces user-configured transitions plus
fixed category guards, records a Tracking Event for every change, and supports dry-run and
idempotent retries (ADR-0003, ADR-0006).

## In scope
- DocTypes: Load Status Transition (+ child Load Status Transition Role, Load Status Transition Field), Tracking Event.
- `vecto/services/load_lifecycle.py` with the functions below.
- A whitelisted REST method and a Desk button that call the service.
- Default transitions (idempotent installer + patch). Tests.

## Out of scope (do NOT build)
- MCP tool registration (task for #7 wraps this service later; keep the signature tool-friendly).
- Notifications, EDI 214 output, portal updates (auto-actions are stored but only `create_tracking_event` runs now).
- Required documents check (documents epic); keep the field, skip enforcement with a TODO linked to the issue.

## Design

### Fixed category order (constant in `vecto/services/status.py`)
`Draft → Planning → Tendering → Covered → Dispatched → In Transit → Delivered → Billing → Closed`;
`Cancelled` is a side branch.
Guards that apply even if a transition row allows otherwise:
1. Forward moves may skip at most one category. Billing and Closed can only be reached from
   Delivered or Billing respectively — the single exception is guard 3's TONU path (Cancelled → Billing).
2. Backward moves are allowed only from Tendering → Planning (rejected or expired tender) and
   Covered → Planning (carrier fell off).
3. Cancelled is reachable only from categories before In Transit; nothing leaves Cancelled except
   Cancelled → Billing for a status flagged `billable_cancellation` (TONU).
4. Moves within the same category (e.g. Dispatched → At Pickup) are always allowed if a transition row exists.

Add `billable_cancellation` Check to **Load Status** (default 0; set 1 on the default "TONU" record via the installer).

### Load Status Transition (module Vecto, autoname hash, `track_changes`)
| Field | Type | Notes |
|---|---|---|
| from_status | Link Load Status | required |
| to_status | Link Load Status | required; ≠ from_status |
| mode | Link Mode | optional: applies only to this mode |
| customer | Link Customer | optional: applies only to this customer |
| allowed_roles | Table MultiSelect → **Load Status Transition Role** (`role` Link Role) | empty = any role with write on Load |
| required_fields | Table → **Load Status Transition Field** (`fieldname` Data, validated against Load meta) | e.g. carrier fields later |
| requires_reason | Check | |
| condition | Code (Python expression) | optional; evaluated with `frappe.safe_eval` against `{"load": load.as_dict()}` only |
| enabled | Check | default 1 |
Validation: the row itself must pass the fixed guards (reject saving an illegal transition).
Uniqueness: one row per (from_status, to_status, mode, customer).

**Resolution order** when finding transitions for a load: rows matching customer → rows matching
mode → rows with neither. The first non-empty level wins.

### Tracking Event (module Tracking, naming `TE-.YYYY.-.######`, not editable after insert)
`load` Link Load (required) · `event_type` Select `Status Change\nCheck Call\nException\nNote` ·
`from_status` Link Load Status · `to_status` Link Load Status · `occurred_at` Datetime (required) ·
`source` Select `User\nAPI\nMCP\nAssistant\nIntegration` · `reason` Small Text · `note` Text ·
`idempotency_key` Data (unique when set) · `actor` Link User.
Indexes: (`load`, `occurred_at`), `idempotency_key`.

### Service: `vecto/services/load_lifecycle.py`
```python
def allowed_transitions(load_name: str) -> list[dict]:
    """Statuses the current user can move this load to: [{status, category, requires_reason, missing_fields}]."""

def transition(load_name: str, to_status: str, *, reason: str | None = None,
               dry_run: bool = False, idempotency_key: str | None = None,
               source: str = "User") -> dict:
    """Validate and apply a status change. Returns
    {ok, dry_run, load, from_status, to_status, from_category, to_category, tracking_event, errors: [{code, message, hint}]}."""
```
Behaviour:
1. Permission: user must have write on the Load (`frappe.has_permission`) and, if `allowed_roles` is set, one of them.
2. Find the transition row (resolution order above); none → error `TRANSITION_NOT_ALLOWED`.
3. Apply fixed guards → `CATEGORY_GUARD`; check `required_fields` → `MISSING_FIELDS` (hint lists them);
   `requires_reason` → `REASON_REQUIRED`; `condition` false → `CONDITION_FAILED`.
4. `dry_run=True`: return the result without writing anything.
5. Idempotency: if a Tracking Event with this `idempotency_key` exists for this load and the same
   to_status, return its result unchanged (no second write); same key with a different to_status → `IDEMPOTENCY_CONFLICT`.
6. Apply: set `status` with a flag that lets Load.validate accept the change only from this service
   (e.g. `load.flags.via_lifecycle = True`), save, insert Tracking Event, all in one transaction.
7. Never compare status names; only categories and transition rows.

REST: `vecto.api.load.transition` (whitelisted, POST) and `vecto.api.load.allowed_transitions` (GET) —
thin wrappers that call the service and return its dict.

Desk: on the Load form, a "Change status" button listing `allowed_transitions`, asking for a reason
when required, calling the REST method with `dry_run=1` first (show what will change), then for real.

### Default transitions (inserted if missing, no mode/customer)
Draft→Planned · Planned→Tendered · Tendered→Covered · Tendered→Planned (reason) · Covered→Dispatched ·
Covered→Planned (reason) · Dispatched→At Pickup · At Pickup→Loaded · Loaded→In Transit ·
In Transit→At Delivery · At Delivery→Delivered · Delivered→POD Received · POD Received→Invoiced ·
Invoiced→Settled · Settled→Closed · Draft/Planned/Tendered→Cancelled (reason) ·
Covered/Dispatched/At Pickup→TONU (reason) · TONU→Invoiced.
Installer looks statuses up **by category and default flag** where possible; the default names are
only used to locate the records it created itself in task 0002.

### Patches
- `vecto.patches.v0_1.create_default_transitions`; `vecto.patches.v0_1.set_tonu_billable`.

## Acceptance criteria
- [ ] Every default transition works; a non-listed transition returns `TRANSITION_NOT_ALLOWED`.
- [ ] Each fixed guard blocks an illegal row at save time and at transition time.
- [ ] Customer-specific rows override mode rows, which override defaults.
- [ ] Dry-run writes nothing (no Load change, no Tracking Event).
- [ ] Repeating a call with the same idempotency key returns the same result and writes once.
- [ ] Changing `status` by editing the Load directly is rejected.
- [ ] Renamed statuses keep working.
- [ ] Desk button shows only allowed transitions and asks for a reason when required.

## Tests to write
- `vecto/vecto/tests/test_load_lifecycle.py`: every guard; resolution order; required fields; reason; condition;
  dry-run; idempotent replay and conflict; permission and role restrictions; rename safety; transaction rollback on failure.
- `vecto/tracking/doctype/tracking_event/test_tracking_event.py`: not editable after insert; unique idempotency key.

## Notes for the implementer
- `frappe.safe_eval` only, with a minimal context; never `eval`.
- The returned dict is the future MCP tool output — keep keys stable and documented in the docstring.
