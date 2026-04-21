import frappe

def execute(filters=None):
    filters = filters or {}

    columns = [
        {"fieldname": "name", "label": "Commission ID", "fieldtype": "Link", "options": "TN Commission", "width": 150},
        {"fieldname": "vendor_name", "label": "Vendor", "fieldtype": "Data", "width": 150},
        {"fieldname": "order", "label": "Order", "fieldtype": "Link", "options": "TN Order", "width": 130},
        {"fieldname": "item_name", "label": "Item", "fieldtype": "Data", "width": 150},
        {"fieldname": "amount", "label": "Commission Amount", "fieldtype": "Currency", "width": 130},
        {"fieldname": "commission_rate", "label": "Rate %", "fieldtype": "Percent", "width": 80},
        {"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 100},
        {"fieldname": "transaction_date", "label": "Date", "fieldtype": "Date", "width": 110},
        {"fieldname": "payout_ref", "label": "Payout", "fieldtype": "Link", "options": "TN Vendor Payout", "width": 120},
    ]

    conditions = "WHERE 1=1"
    values = {}
    if filters.get("vendor"):
        conditions += " AND vendor = %(vendor)s"
        values["vendor"] = filters["vendor"]
    if filters.get("status"):
        conditions += " AND status = %(status)s"
        values["status"] = filters["status"]
    if filters.get("from_date"):
        conditions += " AND transaction_date >= %(from_date)s"
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions += " AND transaction_date <= %(to_date)s"
        values["to_date"] = filters["to_date"]

    data = frappe.db.sql(f"""
        SELECT name, vendor_name, `order`, item_name, amount, commission_rate, status, transaction_date, payout_ref
        FROM `tabTN Commission`
        {conditions}
        ORDER BY transaction_date DESC
    """, values, as_dict=True)

    return columns, data
