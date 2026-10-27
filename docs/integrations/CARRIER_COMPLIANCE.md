# Carrier compliance — regional design

See ADR-0005 for the decision. This file is the working spec.

## Data model
| DocType | Purpose |
|---|---|
| Compliance Region | Region code (e.g. `US`, `CA-ON`, `CA-AB`, `MX`), regulator name, provider adapter, enabled flag, credentials (Password fields), check freshness (hours) |
| Carrier Regulatory ID (child of Carrier) | Region · ID type (USDOT, MC, MX, FF, NSC, CVOR, SICT permit…) · value · verified on |
| Compliance Policy / Policy Rule | Per region: rule code, condition, threshold, action (block / warn / info) |
| Compliance Snapshot | Normalised result of one check: authority status, insurance on file and amounts, safety rating, out-of-service flag, expiries, source, raw payload, checked at |
| Compliance Event | Change detected between two snapshots (e.g. authority revoked, insurance cancelled) → notification + chat inbox |

Carrier keeps a computed **Compliance Status per region** (Compliant / Warning / Blocked / Unverified)
from its latest snapshot and the region's policy.

## Where checks happen
- **Onboarding:** enter a USDOT or MC number → registry lookup pre-fills the carrier (name, address, authority).
- **Tender and dispatch gate:** the load's stops give its regions; the carrier must pass each region's
  policy using a snapshot no older than the region's freshness window, else a fresh check runs.
  Failure returns `CARRIER_NOT_COMPLIANT` with the failing rules as the hint.
- **Monitoring:** scheduled re-check of active carriers (daily by default); changes create
  Compliance Events and can auto-block per policy.
- **Manual override:** a Vecto Admin can override a block for one load with a reason (audited).

## Region 1 — United States (FMCSA)
Sources (official, free):
- **QCMobile API** — `https://mobile.fmcsa.dot.gov/qc/services/`, JSON, `webKey` query parameter
  (request via the FMCSA developer portal with a Login.gov account). Endpoints used:
  `/carriers/{dot}`, `/carriers/docket-number/{mc}`, `/carriers/name/{name}`, `/carriers/{dot}/authority`,
  `/carriers/{dot}/oos`, `/carriers/{dot}/basics`, `/carriers/{dot}/cargo-carried`,
  `/carriers/{dot}/operation-classification`. Per-carrier calls, max 50 results per search, no
  webhooks — so we poll, cache and rate-limit ourselves.
- **FMCSA open data on data.transportation.gov** (Socrata, updated daily) — Licensing & Insurance,
  insurance history and carrier census datasets, for insurance details and bulk/changed-record sync.
- **SAFER** company snapshot — human-readable link stored on the carrier for dispatchers.

Default US policy (editable): operating authority active for the load type · not out of service ·
insurance on file meets the configured minimum · safety rating not "Unsatisfactory" ·
BOC-3 on file · warn if authority age < configurable days.

Optional commercial adapters later (fraud/identity, richer monitoring): Highway, RMIS, Carrier Assure.

## Next regions (confirmed order: Canada, Mexico, India, Europe/UK)
- **Canada** — National Safety Code carrier profiles are issued by each province (e.g. Ontario CVOR);
  no single national API. Start with manual verification + document upload + expiry; add
  province adapters where an API or bulk source exists.
- **Mexico** — SICT federal permits; start manual, research data sources.
- **India** — carrier and vehicle documents (RC, permits, insurance, fitness), GST and e-way bill
  references; start manual with document expiry tracking, then adapters where official APIs exist.
- **Europe / UK** — national operator licences (e.g. UK O-licence) and EU community licences;
  start manual, add adapters per country where public registers allow.
- **Other regions** — added on demand with the same adapter interface.

## MCP tools
| Tool | R/W | Purpose |
|---|---|---|
| `vecto_carrier_registry_lookup` | R | Look up a carrier in a region's registry by ID or name (onboarding pre-fill) |
| `vecto_carrier_compliance_check` | W (writes a snapshot) | Run a fresh check for one or all regions; returns status and failing rules |
| `vecto_carrier_compliance_status` | R | Current per-region status and last checked time |
| `vecto_compliance_override` | W, destructive | Admin override for one load, reason required, dry-run first |
