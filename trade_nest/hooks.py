app_name = "trade_nest"
app_title = "Trade Nest"
app_publisher = "kallu"
app_description = "Trade Nest - Multi Vendor E-Commerce Platform"
app_email = "kallusuvaidyam@gmail.com"
app_license = "mit"

page_js = {"login": "public/js/login.js"}

after_install = "trade_nest.install.after_install"

fixtures = [
    {
        "doctype": "Role",
        "filters": [["role_name", "in", ["Vendor", "Customer"]]]
    },
    {
        "doctype": "Workspace",
        "filters": [["module", "=", "Trade Nest"]]
    },
    {
        "doctype": "Report",
        "filters": [["module", "=", "Trade Nest"]]
    },
    {
        "doctype": "Number Card",
        "filters": [["module", "=", "Trade Nest"]]
    },
]

scheduler_events = {
    "daily": [
        "trade_nest.tasks.daily_fraud_check",
        "trade_nest.tasks.update_vendor_stats",
    ],
    "weekly": [
        "trade_nest.tasks.generate_weekly_report",
    ],
}


doctype_js = {
    "TN Vendor": "public/js/tn_vendor.js",
}