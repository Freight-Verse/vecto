# Copyright (c) 2026, Freightverse and contributors
# For license information, please see license.txt

"""Scheduled tasks for Vecto."""

import frappe
from frappe.utils import now_datetime


def expire_pending_tenders():
	"""Mark Pending tenders Expired when past expiry_datetime."""
	now = now_datetime()
	tenders = frappe.get_all(
		"Tender",
		filters={"status": "Pending", "expiry_datetime": ["<", now]},
		pluck="name",
	)
	for name in tenders:
		frappe.db.set_value("Tender", name, "status", "Expired")
