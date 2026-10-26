# ADR-0001: Build Vecto as a Frappe app on ERPNext
Status: Proposed · Date: 2026-10-26 · Decider: Anupam

**Context.** We need a TMS with accounting, CRM-lite masters and multi-tenant hosting. ERPNext already
provides Customer/Supplier/Item/Invoices/Payments, and Frappe sites are straightforward to host (self-hosted bench, Frappe Press, Frappe Cloud).

**Decision.** Target **Frappe/ERPNext v16** only (decided by Anupam, 2026-10-26; v16 is supported
until end of 2029). Single Frappe app `vecto`, required_apps = ["erpnext"]. Carrier links to Supplier;
accessorials are Items; billing produces Sales/Purchase Invoices.

**Consequences.** + Accounting and hosting for free. + Desk for admin screens. − Tied to Frappe
upgrade cycle; keep Vecto code off ERPNext internals (no monkey patches, hooks only).
