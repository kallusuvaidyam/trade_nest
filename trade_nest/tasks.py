import frappe
from frappe.utils import today, add_days, getdate, date_diff


def daily_fraud_check():
    """Flag suspicious users with multiple high-risk orders."""
    flagged_users = frappe.db.sql("""
        SELECT customer_email, customer_user, COUNT(*) as flag_count
        FROM `tabTN Order`
        WHERE is_flagged = 1
        AND transaction_date >= %s
        GROUP BY customer_user
        HAVING flag_count >= 3
    """, add_days(today(), -7), as_dict=True)

    for u in flagged_users:
        frappe.log_error(
            f"User {u.customer_email} has {u.flag_count} flagged orders in 7 days",
            "TradeNest: Repeated Fraud Flags"
        )


def update_vendor_stats():
    """Recalculate vendor pending commissions daily."""
    vendors = frappe.get_all("TN Vendor", filters={"status": "Approved"}, fields=["name"])
    for v in vendors:
        pending = frappe.db.sql(
            "SELECT COALESCE(SUM(amount), 0) FROM `tabTN Commission` WHERE vendor=%s AND status='Pending'",
            v.name
        )[0][0]
        frappe.db.set_value("TN Vendor", v.name, "pending_commission", pending)


def generate_weekly_report():
    """Send weekly summary to admin."""
    week_start = add_days(today(), -7)

    stats = frappe.db.sql("""
        SELECT
            COUNT(*) as total_orders,
            SUM(grand_total) as total_revenue,
            SUM(CASE WHEN status='Cancelled' THEN 1 ELSE 0 END) as cancelled,
            SUM(CASE WHEN is_flagged=1 THEN 1 ELSE 0 END) as flagged
        FROM `tabTN Order`
        WHERE transaction_date >= %s
    """, week_start, as_dict=True)[0]

    commission_stats = frappe.db.sql(
        "SELECT COALESCE(SUM(amount), 0) FROM `tabTN Commission` WHERE transaction_date >= %s AND status='Pending'",
        week_start
    )[0][0]

    admin_emails = frappe.db.sql("""
        SELECT DISTINCT u.email FROM `tabUser` u
        JOIN `tabHas Role` hr ON hr.parent = u.name
        WHERE hr.role = 'System Manager' AND u.enabled = 1
        LIMIT 3
    """, as_list=True)
    admin_email_list = [e[0] for e in admin_emails if e[0]]

    if admin_email_list:
        frappe.sendmail(
            recipients=admin_email_list,
            subject=f"Weekly Trade Nest Report ({week_start} to {today()})",
            message=f"""
            <h2>Weekly Performance Report</h2>
            <table border="1" cellpadding="8" style="border-collapse:collapse">
              <tr><td><b>Total Orders</b></td><td>{stats.total_orders or 0}</td></tr>
              <tr><td><b>Total Revenue</b></td><td>\u20b9{stats.total_revenue or 0}</td></tr>
              <tr><td><b>Cancelled Orders</b></td><td>{stats.cancelled or 0}</td></tr>
              <tr><td><b>Flagged Orders</b></td><td>{stats.flagged or 0}</td></tr>
              <tr><td><b>Pending Commissions</b></td><td>\u20b9{commission_stats or 0}</td></tr>
            </table>
            <br>
            <p><a href="/app/trade-nest-admin">Open Admin Dashboard</a></p>
            """,
            now=False
        )
