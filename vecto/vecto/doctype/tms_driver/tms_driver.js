// Copyright (c) 2026, Freightverse and contributors
// For license information, please see license.txt

// Implements: Phase 1 — TMS Driver

frappe.ui.form.on("TMS Driver", {
	refresh(frm) {
		frm.trigger("check_license_expiry");
	},

	license_expiry(frm) {
		frm.trigger("check_license_expiry");
	},

	check_license_expiry(frm) {
		if (!frm.doc.license_expiry) {
			return;
		}
		const expiry = frappe.datetime.str_to_obj(frm.doc.license_expiry);
		const today = frappe.datetime.str_to_obj(frappe.datetime.get_today());
		const in_30 = frappe.datetime.str_to_obj(frappe.datetime.add_days(frappe.datetime.get_today(), 30));
		if (expiry <= today) {
			frm.dashboard.set_headline_alert(
				__("License expired on {0}", [frm.doc.license_expiry]),
				"red"
			);
		} else if (expiry <= in_30) {
			frm.dashboard.set_headline_alert(
				__("License expires within 30 days ({0})", [frm.doc.license_expiry]),
				"orange"
			);
		}
	},
});
