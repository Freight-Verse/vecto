app_name = "vecto"
app_title = "Vecto"
app_publisher = "Freightverse"
app_description = "A modern Transportation Management System built on Frappe — manage freight, shipments, carriers, and logistics operations end to end."
app_email = "tech@freightverse.io"
app_license = "agpl-3.0"

# ERPNext is required (Company, Account, Payment Terms Template, Customer, Supplier, UOM).
required_apps = ["erpnext"]

after_install = "vecto.install.after_install"
after_migrate = "vecto.install.after_migrate"

# Fixtures exported via: bench --site localhost.v16 export-fixtures --app vecto
fixtures = [
	{
		"dt": "Role",
		"filters": [
			[
				"name",
				"in",
				[
					"TMS Admin",
					"Dispatcher",
					"Carrier Manager",
					"TMS Finance",
					"TMS Customer",
					"TMS Carrier Portal",
				],
			]
		],
	},
	{"dt": "Workspace", "filters": [["module", "=", "Vecto"]]},
	{"dt": "Load Status"},
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/vecto/css/vecto.css"
# app_include_js = "/assets/vecto/js/vecto.js"

# include js, css files in header of web template
# web_include_css = "/assets/vecto/css/vecto.css"
# web_include_js = "/assets/vecto/js/vecto.js"

# Document Events
# ---------------
# Do not auto-create Tender on Load Order submit — use tender_load / Desk action.
doc_events = {
	"Tender": {
		"on_update": "vecto.vecto.doctype.tender.tender.sync_load_order_status",
	},
}

# Scheduled Tasks
# ---------------
scheduler_events = {
	"hourly": ["vecto.tasks.expire_pending_tenders"],
}

# scheduler_events_template = {
# 	"all": [
# 		"vecto.tasks.all"
# 	],
# 	"daily": [
# 		"vecto.tasks.daily"
# 	],
# 	"hourly": [
# 		"vecto.tasks.hourly"
# 	],
# 	"weekly": [
# 		"vecto.tasks.weekly"
# 	],
# 	"monthly": [
# 		"vecto.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "vecto.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "vecto.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "vecto.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "vecto.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["vecto.utils.before_request"]
# after_request = ["vecto.utils.after_request"]

# Job Events
# ----------
# before_job = ["vecto.utils.before_job"]
# after_job = ["vecto.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"vecto.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []


