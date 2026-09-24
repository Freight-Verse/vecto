# Copyright (c) 2026, Freightverse and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def require_api_key():
	"""Validate the X-Vecto-Key header against TMS Settings."""
	provided = frappe.get_request_header("X-Vecto-Key")
	if not provided:
		frappe.throw(_("X-Vecto-Key header is required"), frappe.AuthenticationError)

	expected = frappe.utils.password.get_decrypted_password("TMS Settings", "TMS Settings", "vecto_api_key")
	if not expected or provided != expected:
		frappe.throw(_("Invalid API key"), frappe.AuthenticationError)
