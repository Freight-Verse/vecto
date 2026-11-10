// Copyright (c) 2026, Freightverse and contributors
// For license information, please see license.txt

// Implements: Phase 2 — Tender

frappe.ui.form.on("Tender", {
	refresh(frm) {
		if (frm.doc.status !== "Pending" || frm.is_new()) {
			return;
		}
		frm.add_custom_button(
			__("Accept"),
			() => {
				frm.set_value("status", "Accepted");
				frm.save();
			},
			__("Actions")
		);
		frm.add_custom_button(
			__("Reject"),
			() => {
				frm.set_value("status", "Rejected");
				frm.save();
			},
			__("Actions")
		);
	},
});
