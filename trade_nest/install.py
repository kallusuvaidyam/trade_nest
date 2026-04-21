import frappe

def after_install():
    _create_roles()
    _create_custom_fields()

def _create_roles():
    roles = ["Vendor", "Customer"]
    for role_name in roles:
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role_name,
                "desk_access": 1 if role_name == "Vendor" else 0
            }).insert(ignore_permissions=True)

def _create_custom_fields():
    if not frappe.db.exists("Custom Field", "Sales Order-custom_payment_method"):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Sales Order",
            "fieldname": "custom_payment_method",
            "fieldtype": "Select",
            "label": "Payment Method",
            "options": "COD\nOnline",
            "insert_after": "status"
        }).insert(ignore_permissions=True)
