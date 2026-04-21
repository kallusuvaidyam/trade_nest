import frappe


def redirect_on_login(login_manager):
    user = login_manager.user
    roles = frappe.get_roles(user)

    if "System Manager" in roles or "Administrator" in roles:
        return  # Frappe default desk pe jaaye

    # Customer aur normal users ko shop pe bhejo
    frappe.local.response["home_page"] = "/shop"
    raise frappe.exceptions.Redirect("/shop")


def on_logout(login_manager):
    """Post-logout redirect Vue login pe"""
    frappe.local.response["home_page"] = "/shop#/login"
