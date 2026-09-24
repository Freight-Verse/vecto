app_name = "vecto"
app_title = "Vecto"
app_publisher = "Freightverse"
app_description = "A modern Transportation Management System built on Frappe — manage freight, shipments, carriers, and logistics operations end to end."
app_email = "tech@freightverse.io"
app_license = "mit"

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
# doc_events = {}

# Scheduled Tasks
# ---------------
# scheduler_events = {}

# Testing
# -------
# before_tests = "vecto.install.before_tests"
