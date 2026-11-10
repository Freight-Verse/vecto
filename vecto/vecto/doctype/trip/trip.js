// Copyright (c) 2026, Freightverse and contributors
// For license information, please see license.txt

// Implements: Phase 2 — Trip

frappe.ui.form.on("Trip", {
	refresh(frm) {
		frm.trigger("filter_vehicle_by_carrier");
	},

	driver(frm) {
		frm.trigger("filter_vehicle_by_carrier");
	},

	filter_vehicle_by_carrier(frm) {
		if (!frm.doc.driver) {
			frm.set_query("vehicle", () => ({}));
			return;
		}
		frappe.db.get_value("TMS Driver", frm.doc.driver, "carrier", (r) => {
			frm.set_query("vehicle", () => ({
				filters: r && r.carrier ? { carrier: r.carrier } : {},
			}));
		});
	},
});
