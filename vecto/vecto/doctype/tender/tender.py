# Copyright (c) 2026, Freightverse and contributors
# For license information, please see license.txt

# Implements: Phase 2 — Tender

import frappe
from frappe.model.document import Document
from frappe.utils import add_to_date, now_datetime


class Tender(Document):
	def validate(self):
		if not self.expiry_datetime:
			self.expiry_datetime = add_to_date(now_datetime(), hours=2)
		if self.has_value_changed("status") and self.status in ("Accepted", "Rejected"):
			self.response_datetime = now_datetime()
			if not self.responded_by:
				self.responded_by = frappe.session.user


def sync_load_order_status(doc, method=None):
	"""When a Tender is Accepted, confirm the load and copy the carrier."""
	if doc.status != "Accepted" or not doc.load_order:
		return
	if not frappe.db.exists("Load Order", doc.load_order):
		return

	load = frappe.get_doc("Load Order", doc.load_order)
	load.assigned_carrier = doc.carrier
	load.status = "Confirmed"
	if doc.offered_rate and not load.rate_override:
		load.buy_rate = doc.offered_rate
	load.save(ignore_permissions=True)
