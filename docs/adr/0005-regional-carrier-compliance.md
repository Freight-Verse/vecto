# ADR-0005: Regional carrier compliance, FMCSA first
Status: Proposed · Date: 2026-10-26 · Decider: Anupam

**Context.** Carriers must be verified against the regulator of every region a load touches. Each
region has a different regulator, identifier and data source (US: FMCSA with USDOT/MC numbers;
Canada: provincial National Safety Code profiles; Mexico: SICT permits; others vary). Companies
using Vecto operate in different sets of regions.

**Decision.**
1. A **Compliance Region** is configuration, not code: each site enables the regions it operates in.
2. Each region has a **provider adapter** behind one interface (`integrations/compliance/`):
   `lookup(identifier)`, `check(carrier)`, `changes_since(timestamp)` → a normalised
   Compliance Snapshot (authority, insurance, safety rating, out-of-service, expiries, raw payload).
3. **Rules live in data**: a Compliance Policy per region says what blocks, what warns
   (e.g. authority inactive → block; insurance below minimum → block; authority younger than N days → warn).
4. A load is checked against the policies of **every region its stops touch**.
5. FMCSA (United States) is the first adapter. Other regions follow the same interface.

**Consequences.** + Adding a region is an adapter plus policy rows; nothing else changes.
+ Same tools for chat, MCP and forms. − Some regions have no public API; their adapter starts as
manual verification with document upload and expiry tracking.

Details: `docs/integrations/CARRIER_COMPLIANCE.md`.
