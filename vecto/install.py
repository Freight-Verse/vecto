# Copyright (c) 2026, Freightverse and contributors
# For license information, please see license.txt

"""Phase 1–2 install hooks — roles and default masters."""

import frappe

TMS_ROLES = [
	"TMS Admin",
	"Dispatcher",
	"Carrier Manager",
	"TMS Finance",
	"TMS Customer",
	"TMS Carrier Portal",
]

DEFAULT_LOAD_STATUSES = [
	{"status_name": "Draft", "sequence": 10, "color": "Gray"},
	{"status_name": "Quoting", "sequence": 20, "color": "Blue"},
	{"status_name": "Tendered", "sequence": 30, "color": "Cyan"},
	{"status_name": "Confirmed", "sequence": 40, "color": "Purple"},
	{"status_name": "In Transit", "sequence": 50, "color": "Orange"},
	{"status_name": "Delivered", "sequence": 60, "color": "Green"},
	{"status_name": "Invoiced", "sequence": 70, "color": "Yellow"},
	{"status_name": "Cancelled", "sequence": 90, "color": "Red"},
]


def after_install():
	create_tms_roles()
	create_default_load_statuses()
	frappe.db.commit()


def after_migrate():
	create_tms_roles()
	create_default_load_statuses()


def create_tms_roles():
	"""Ensure TMS roles exist and are assignable from User."""
	portal_roles = {"TMS Customer", "TMS Carrier Portal"}
	for role_name in TMS_ROLES:
		if frappe.db.exists("Role", role_name):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Role",
				"role_name": role_name,
				"desk_access": 0 if role_name in portal_roles else 1,
			}
		)
		doc.insert(ignore_permissions=True)


def create_default_load_statuses():
	"""Seed standard Load Status rows used as Link targets on Load Order."""
	if not frappe.db.exists("DocType", "Load Status"):
		return

	for row in DEFAULT_LOAD_STATUSES:
		if frappe.db.exists("Load Status", row["status_name"]):
			continue
		frappe.get_doc(
			{
				"doctype": "Load Status",
				"status_name": row["status_name"],
				"sequence": row["sequence"],
				"color": row["color"],
				"is_active": 1,
			}
		).insert(ignore_permissions=True)
