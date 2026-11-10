# Copyright (c) 2026, Freightverse and contributors
# For license information, please see license.txt

# Implements: Phase 2 — Load Order API

import frappe
from frappe import _


@frappe.whitelist()
def tender_load(load_order, carrier, offered_rate=None):
	"""Create a Tender for a Load Order. Does not run on Load Order submit."""
	if not load_order or not carrier:
		frappe.throw(_("load_order and carrier are required"), frappe.ValidationError)

	if not frappe.db.exists("Load Order", load_order):
		frappe.throw(_("Load Order {0} not found").format(load_order), frappe.DoesNotExistError)
	if not frappe.db.exists("Carrier", carrier):
		frappe.throw(_("Carrier {0} not found").format(carrier), frappe.DoesNotExistError)

	docstatus = frappe.db.get_value("Load Order", load_order, "docstatus")
	if docstatus != 1:
		frappe.throw(_("Submit the Load Order before tendering"), frappe.ValidationError)

	tender = frappe.get_doc(
		{
			"doctype": "Tender",
			"load_order": load_order,
			"carrier": carrier,
			"offered_rate": offered_rate,
			"status": "Pending",
		}
	)
	tender.insert(ignore_permissions=False)

	status = frappe.db.get_value("Load Order", load_order, "status")
	if status in ("Draft", "Quoting"):
		load = frappe.get_doc("Load Order", load_order)
		load.status = "Tendered"
		load.save(ignore_permissions=False)

	return {"tender": tender.name, "load": load_order, "status": "Pending"}
