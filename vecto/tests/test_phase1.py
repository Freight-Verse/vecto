# Copyright (c) 2026, Freightverse and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from vecto.install import (
	DEFAULT_LOAD_STATUSES,
	TMS_ROLES,
	create_default_load_statuses,
	create_tms_roles,
)

PHASE1_DOCTYPES = [
	"Carrier",
	"Carrier Equipment Type Detail",
	"TMS Driver",
	"TMS Vehicle",
	"Shipper",
	"Shipper Contact Detail",
	"Shipper Address Detail",
	"TMS Location",
	"Commodity",
	"TMS Settings",
	"Load Status",
]


class TestPhase1Foundation(FrappeTestCase):
	def test_phase1_doctypes_exist(self):
		for dt in PHASE1_DOCTYPES:
			self.assertTrue(frappe.db.exists("DocType", dt), f"Missing DocType: {dt}")

	def test_tms_roles_exist(self):
		create_tms_roles()
		for role in TMS_ROLES:
			self.assertTrue(frappe.db.exists("Role", role), f"Missing Role: {role}")

	def test_vecto_workspace_exists(self):
		self.assertTrue(frappe.db.exists("Workspace", "Vecto"))

	def test_default_load_statuses_seeded(self):
		create_default_load_statuses()
		for row in DEFAULT_LOAD_STATUSES:
			self.assertTrue(
				frappe.db.exists("Load Status", row["status_name"]),
				f"Missing Load Status: {row['status_name']}",
			)
		# status field on Load Order (when created) must be Link → Load Status
		meta = frappe.get_meta("Load Status")
		self.assertEqual(meta.autoname, "field:status_name")

	def test_create_carrier_and_driver(self):
		carrier = frappe.get_doc(
			{
				"doctype": "Carrier",
				"carrier_name": "_Test Carrier Phase1",
				"status": "Active",
				"equipment_types": [{"equipment_type": "Dry Van"}],
			}
		).insert(ignore_permissions=True)

		driver = frappe.get_doc(
			{
				"doctype": "TMS Driver",
				"driver_name": "_Test Driver Phase1",
				"carrier": carrier.name,
				"status": "Active",
			}
		).insert(ignore_permissions=True)

		self.assertEqual(carrier.name, "_Test Carrier Phase1")
		self.assertEqual(driver.carrier, carrier.name)

		driver.delete()
		carrier.delete()

	def test_create_shipper_location_commodity(self):
		shipper = frappe.get_doc(
			{
				"doctype": "Shipper",
				"shipper_name": "_Test Shipper Phase1",
				"customer_code": "TSP1",
			}
		).insert(ignore_permissions=True)

		location = frappe.get_doc(
			{
				"doctype": "TMS Location",
				"location_name": "_Test Loc Phase1",
				"location_type": "Warehouse",
				"city": "Chicago",
				"state": "IL",
			}
		).insert(ignore_permissions=True)

		commodity = frappe.get_doc(
			{
				"doctype": "Commodity",
				"commodity_name": "_Test Commodity Phase1",
				"freight_class": "70",
			}
		).insert(ignore_permissions=True)

		settings = frappe.get_single("TMS Settings")
		settings.load_number_prefix = "LOAD"
		settings.save(ignore_permissions=True)

		self.assertEqual(frappe.db.get_single_value("TMS Settings", "load_number_prefix"), "LOAD")

		commodity.delete()
		location.delete()
		shipper.delete()
