import frappe

no_cache = 1


def get_context(context):
    if frappe.session.user != "Guest":
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = "/shop"
        raise frappe.Redirect

    frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = "/shop#/login"
    raise frappe.Redirect
