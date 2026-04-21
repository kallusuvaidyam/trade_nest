import frappe

no_cache = 1


def get_context(context):
    user = frappe.session.user

    if user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    roles = frappe.get_roles(user)

    if "Customer" in roles and "System Manager" not in roles:
        frappe.local.flags.redirect_location = "/shop"
        raise frappe.Redirect
