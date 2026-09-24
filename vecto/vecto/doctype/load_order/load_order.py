# Copyright (c) 2026, Freightverse and contributors
# For license information, please see license.txt

# Implements: Phase 2 — Load Order

import frappe
from frappe import _
from frappe.model.document import Document

from vecto.utils.load import append_status_log, compute_load_totals


class LoadOrder(Document):
	def validate(self):
		if not self.status:
			self.status = "Draft"
		compute_load_totals(self)
		if self.is_new() or self.has_value_changed("status"):
			append_status_log(self)

	def before_submit(self):
		if not self.shipper or not self.origin or not self.destination:
			frappe.throw(
				_("Shipper, Origin, and Destination are required"),
				frappe.ValidationError,
			)
		if not self.get("stops"):
			frappe.throw(_("Add at least one Stop before submit"), frappe.ValidationError)

	def on_update_after_submit(self):
		if not self.has_value_changed("status"):
			return
		# Child rows are not persisted by db_update(); insert the log row directly.
		frappe.get_doc(
			{
				"doctype": "Load Status Log",
				"parent": self.name,
				"parenttype": "Load Order",
				"parentfield": "status_log",
				"timestamp": frappe.utils.now_datetime(),
				"status": self.status,
				"updated_by": frappe.session.user,
			}
		).insert(ignore_permissions=True)
