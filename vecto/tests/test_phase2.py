# Copyright (c) 2026, Freightverse and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_to_date, now_datetime

from vecto.api.v1.loads import tender_load
from vecto.tasks import expire_pending_tenders


class TestPhase2LoadDispatch(FrappeTestCase):
	def setUp(self):
		self.shipper = self._ensure("Shipper", "_Test Shipper P2", {"shipper_name": "_Test Shipper P2"})
		self.origin = self._ensure(
			"TMS Location",
			"_Test Origin P2",
			{"location_name": "_Test Origin P2", "location_type": "Warehouse", "city": "Chicago", "state": "IL"},
		)
		self.destination = self._ensure(
			"TMS Location",
			"_Test Dest P2",
			{"location_name": "_Test Dest P2", "location_type": "Customer", "city": "Dallas", "state": "TX"},
		)
		self.carrier = self._ensure(
			"Carrier",
			"_Test Carrier P2",
			{"carrier_name": "_Test Carrier P2", "status": "Active"},
		)

	def _ensure(self, doctype, name, values):
		if frappe.db.exists(doctype, name):
			return frappe.get_doc(doctype, name)
		values["doctype"] = doctype
		return frappe.get_doc(values).insert(ignore_permissions=True)

	def _make_load(self, with_stop=True, **kwargs):
		payload = {
			"doctype": "Load Order",
			"naming_series": "LOAD-.YYYY.-",
			"shipper": self.shipper.name,
			"origin": self.origin.name,
			"destination": self.destination.name,
			"load_type": "FTL",
			"sell_rate": 1000,
			"buy_rate": 800,
			"fsc_sell": 50,
			"fsc_buy": 40,
		}
		payload.update(kwargs)
		if with_stop:
			payload["stops"] = [
				{
					"sequence": 1,
					"stop_type": "Pickup",
					"location": self.origin.name,
				}
			]
		return frappe.get_doc(payload).insert(ignore_permissions=True)

	def test_totals_and_status_log_on_create(self):
		load = self._make_load()
		self.assertEqual(load.status, "Draft")
		self.assertEqual(load.total_sell, 1050)
		self.assertEqual(load.total_buy, 840)
		self.assertEqual(load.margin, 210)
		self.assertTrue(load.status_log)
		self.assertEqual(load.status_log[0].status, "Draft")

	def test_submit_requires_stop(self):
		load = self._make_load(with_stop=False)
		self.assertRaises(frappe.ValidationError, load.submit)

	def test_submit_does_not_create_tender(self):
		load = self._make_load()
		load.submit()
		self.assertFalse(frappe.db.exists("Tender", {"load_order": load.name}))

	def test_tender_load_then_accept(self):
		load = self._make_load()
		load.submit()
		result = tender_load(load.name, self.carrier.name, offered_rate=750)
		self.assertTrue(frappe.db.exists("Tender", result["tender"]))
		self.assertEqual(frappe.db.get_value("Load Order", load.name, "status"), "Tendered")

		tender = frappe.get_doc("Tender", result["tender"])
		tender.status = "Accepted"
		tender.save(ignore_permissions=True)

		load.reload()
		self.assertEqual(load.status, "Confirmed")
		self.assertEqual(load.assigned_carrier, self.carrier.name)
		self.assertTrue(any(row.status == "Confirmed" for row in load.status_log))

	def test_expire_pending_tenders(self):
		load = self._make_load()
		load.submit()
		tender = frappe.get_doc(
			{
				"doctype": "Tender",
				"naming_series": "TNDR-.YYYY.-",
				"load_order": load.name,
				"carrier": self.carrier.name,
				"status": "Pending",
				"expiry_datetime": add_to_date(now_datetime(), hours=-1),
			}
		).insert(ignore_permissions=True)

		expire_pending_tenders()
		self.assertEqual(frappe.db.get_value("Tender", tender.name, "status"), "Expired")

	def test_trip_total_miles(self):
		driver = self._ensure(
			"TMS Driver",
			"_Test Driver P2",
			{"driver_name": "_Test Driver P2", "carrier": self.carrier.name, "status": "Active"},
		)
		vehicle = self._ensure(
			"TMS Vehicle",
			"P2-TEST-1",
			{"plate_number": "P2-TEST-1", "carrier": self.carrier.name, "status": "Active"},
		)
		load = self._make_load()
		trip = frappe.get_doc(
			{
				"doctype": "Trip",
				"naming_series": "TRIP-.YYYY.-",
				"driver": driver.name,
				"vehicle": vehicle.name,
				"trip_date": now_datetime().date(),
				"loads": [
					{"sequence": 1, "load_order": load.name, "miles": 10},
					{"sequence": 2, "load_order": load.name, "miles": 15},
				],
			}
		).insert(ignore_permissions=True)
		self.assertEqual(trip.total_miles, 25)
