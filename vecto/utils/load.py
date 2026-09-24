# Copyright (c) 2026, Freightverse and contributors
# For license information, please see license.txt

"""Load Order helpers — totals and status log. Not whitelisted."""

from frappe.utils import flt, now_datetime


def compute_load_totals(doc):
	"""Set total_sell, total_buy, margin, margin_pct unless rate_override is set."""
	if doc.rate_override:
		return

	customer_accessorials = 0
	carrier_accessorials = 0
	for row in doc.get("accessorials") or []:
		row.total = flt(row.quantity or 1) * flt(row.rate)
		if row.billable_to in (None, "", "Customer", "Both"):
			if row.billable_to != "Carrier":
				customer_accessorials += flt(row.total)
		if row.billable_to in ("Carrier", "Both"):
			carrier_accessorials += flt(row.total)

	doc.total_sell = flt(doc.sell_rate) + flt(doc.fsc_sell) + customer_accessorials
	doc.total_buy = flt(doc.buy_rate) + flt(doc.fsc_buy) + carrier_accessorials
	doc.margin = flt(doc.total_sell) - flt(doc.total_buy)
	if flt(doc.total_sell):
		doc.margin_pct = flt(doc.margin) / flt(doc.total_sell) * 100
	else:
		doc.margin_pct = 0


def append_status_log(doc, notes=None):
	"""Append a read-only Load Status Log row for the current status."""
	doc.append(
		"status_log",
		{
			"timestamp": now_datetime(),
			"status": doc.status,
			"updated_by": doc.modified_by or doc.owner,
			"notes": notes,
		},
	)
