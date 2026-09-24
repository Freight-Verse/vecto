# Copyright (c) 2026, Freightverse and contributors
# For license information, please see license.txt

# Implements: Phase 2 — Trip

from frappe.model.document import Document
from frappe.utils import flt


class Trip(Document):
	def validate(self):
		self.total_miles = sum(flt(row.miles) for row in self.get("loads") or [])
