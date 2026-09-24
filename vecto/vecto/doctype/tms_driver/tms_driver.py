# Copyright (c) 2026, Freightverse and contributors
# For license information, please see license.txt

# Implements: Phase 1 — TMS Driver

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, getdate, today


class TMSDriver(Document):
	def validate(self):
		self.warn_license_expiry()

	def warn_license_expiry(self):
		if not self.license_expiry:
			return

		expiry = getdate(self.license_expiry)
		threshold = getdate(add_days(today(), 30))
		if expiry <= getdate(today()):
			frappe.msgprint(
				_("Driver license expired on {0}").format(expiry),
				indicator="red",
				alert=True,
			)
		elif expiry <= threshold:
			frappe.msgprint(
				_("Driver license expires within 30 days ({0})").format(expiry),
				indicator="orange",
				alert=True,
			)
