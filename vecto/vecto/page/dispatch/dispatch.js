// Copyright (c) 2026, Freightverse and contributors
// For license information, please see license.txt

// Implements: Phase 2 — Dispatch Board (/app/dispatch)

frappe.pages["dispatch"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Dispatch"),
		single_column: true,
	});

	page.vecto_filters = {
		from_date: null,
		to_date: null,
		dispatcher: null,
		carrier: null,
		load_type: null,
	};

	page.add_field({
		fieldname: "from_date",
		label: __("From Date"),
		fieldtype: "Date",
		change() {
			page.vecto_filters.from_date = this.get_value();
			page.vecto_refresh();
		},
	});
	page.add_field({
		fieldname: "to_date",
		label: __("To Date"),
		fieldtype: "Date",
		change() {
			page.vecto_filters.to_date = this.get_value();
			page.vecto_refresh();
		},
	});
	page.add_field({
		fieldname: "dispatcher",
		label: __("Dispatcher"),
		fieldtype: "Link",
		options: "User",
		change() {
			page.vecto_filters.dispatcher = this.get_value();
			page.vecto_refresh();
		},
	});
	page.add_field({
		fieldname: "carrier",
		label: __("Carrier"),
		fieldtype: "Link",
		options: "Carrier",
		change() {
			page.vecto_filters.carrier = this.get_value();
			page.vecto_refresh();
		},
	});
	page.add_field({
		fieldname: "load_type",
		label: __("Load Type"),
		fieldtype: "Select",
		options: "\nFTL\nLTL\nPartial",
		change() {
			page.vecto_filters.load_type = this.get_value();
			page.vecto_refresh();
		},
	});

	$(page.body).html('<div class="vecto-dispatch-board p-3"></div>');

	page.vecto_refresh = function () {
		frappe.call({
			method: "vecto.vecto.page.dispatch.dispatch.get_dispatch_board",
			args: page.vecto_filters,
			callback(r) {
				render_board(page, r.message || { columns: [] });
			},
		});
	};

	page.vecto_refresh();
};

function render_board(page, data) {
	const $board = $(page.body).find(".vecto-dispatch-board");
	$board.empty().css({
		display: "flex",
		gap: "12px",
		overflowX: "auto",
		alignItems: "flex-start",
	});

	(data.columns || []).forEach((col) => {
		const $col = $(`
			<div class="vecto-dispatch-col" style="min-width:240px;max-width:280px;background:var(--control-bg);border-radius:8px;padding:10px;">
				<h5 style="margin:0 0 8px 0;">
					<span class="indicator-pill ${frappe.utils.escape_html(col.color || "Gray")}">
						${frappe.utils.escape_html(col.status)}
					</span>
					<span class="text-muted"> ${(col.loads || []).length}</span>
				</h5>
				<div class="vecto-dispatch-cards"></div>
			</div>
		`);
		const $cards = $col.find(".vecto-dispatch-cards");
		(col.loads || []).forEach((load) => {
			const lane = [load.origin, load.destination].filter(Boolean).join(" → ");
			const $card = $(`
				<div class="frappe-card" style="padding:10px;margin-bottom:8px;cursor:pointer;">
					<div class="bold">${frappe.utils.escape_html(load.name)}</div>
					<div>${frappe.utils.escape_html(load.shipper || "")}</div>
					<div class="text-muted">${frappe.utils.escape_html(lane)}</div>
					<div>${frappe.utils.escape_html(load.assigned_carrier || "")}</div>
				</div>
			`);
			$card.on("click", () => frappe.set_route("Form", "Load Order", load.name));
			$cards.append($card);
		});
		$board.append($col);
	});
}
