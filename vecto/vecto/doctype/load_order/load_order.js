// Copyright (c) 2026, Freightverse and contributors
// For license information, please see license.txt

// Implements: Phase 2 — Load Order

frappe.ui.form.on("Load Order", {
	refresh(frm) {
		frm.set_query("status", () => ({
			filters: { is_active: 1 },
		}));
		frm.set_query("assigned_driver", () => ({
			filters: frm.doc.assigned_carrier ? { carrier: frm.doc.assigned_carrier } : {},
		}));
		frm.set_query("assigned_vehicle", () => ({
			filters: frm.doc.assigned_carrier ? { carrier: frm.doc.assigned_carrier } : {},
		}));

		if (frm.doc.docstatus === 1 && !frm.is_new()) {
			frm.add_custom_button(
				__("Tender Load"),
				() => {
					frappe.prompt(
						[
							{
								fieldname: "carrier",
								fieldtype: "Link",
								options: "Carrier",
								label: __("Carrier"),
								reqd: 1,
							},
							{
								fieldname: "offered_rate",
								fieldtype: "Currency",
								label: __("Offered Rate"),
							},
						],
						(values) => {
							frappe.call({
								method: "vecto.api.v1.loads.tender_load",
								args: {
									load_order: frm.doc.name,
									carrier: values.carrier,
									offered_rate: values.offered_rate,
								},
								freeze: true,
								callback(r) {
									if (r.message) {
										frappe.set_route("Form", "Tender", r.message.tender);
									}
								},
							});
						},
						__("Tender Load"),
						__("Create")
					);
				},
				__("Actions")
			);
		}
	},

	assigned_carrier(frm) {
		if (!frm.doc.assigned_carrier) {
			frm.set_value("assigned_driver", null);
			frm.set_value("assigned_vehicle", null);
			frm.refresh_field("assigned_driver");
			frm.refresh_field("assigned_vehicle");
		}
	},
});
