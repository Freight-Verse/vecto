# Copyright (c) 2026, Freightverse and contributors
# For license information, please see license.txt

# Implements: Phase 2 — Dispatch Board

import frappe
from frappe.utils import getdate


@frappe.whitelist()
def get_dispatch_board(from_date=None, to_date=None, dispatcher=None, carrier=None, load_type=None):
	"""Return Load Orders grouped by Load Status for the Kanban board."""
	filters = {}
	if dispatcher:
		filters["dispatcher"] = dispatcher
	if carrier:
		filters["assigned_carrier"] = carrier
	if load_type:
		filters["load_type"] = load_type
	if from_date:
		filters["pickup_date"] = [">=", getdate(from_date)]
	if to_date:
		if "pickup_date" in filters:
			filters["pickup_date"] = ["between", [getdate(from_date), getdate(to_date)]]
		else:
			filters["pickup_date"] = ["<=", getdate(to_date)]

	loads = frappe.get_all(
		"Load Order",
		filters=filters,
		fields=[
			"name",
			"status",
			"shipper",
			"origin",
			"destination",
			"assigned_carrier",
			"load_type",
			"pickup_date",
			"dispatcher",
		],
		order_by="pickup_date asc, modified desc",
	)

	statuses = frappe.get_all(
		"Load Status",
		filters={"is_active": 1},
		fields=["name", "status_name", "sequence", "color"],
		order_by="sequence asc",
	)

	by_status = {row.status: [] for row in statuses}
	for load in loads:
		by_status.setdefault(load.status, []).append(load)

	columns = []
	for status in statuses:
		columns.append(
			{
				"status": status.name,
				"color": status.color,
				"sequence": status.sequence,
				"loads": by_status.get(status.name, []),
			}
		)
	return {"columns": columns}
