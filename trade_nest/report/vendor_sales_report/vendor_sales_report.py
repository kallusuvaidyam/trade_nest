import frappe

def execute(filters=None):
    filters = filters or {}

    columns = [
        {"fieldname": "vendor", "label": "Vendor", "fieldtype": "Link", "options": "TN Vendor", "width": 150},
        {"fieldname": "vendor_name", "label": "Vendor Name", "fieldtype": "Data", "width": 150},
        {"fieldname": "total_orders", "label": "Total Orders", "fieldtype": "Int", "width": 100},
        {"fieldname": "total_sales", "label": "Total Sales", "fieldtype": "Currency", "width": 130},
        {"fieldname": "total_commission", "label": "Commission Earned (Platform)", "fieldtype": "Currency", "width": 160},
        {"fieldname": "vendor_earnings", "label": "Vendor Earnings", "fieldtype": "Currency", "width": 130},
        {"fieldname": "avg_order_value", "label": "Avg Order Value", "fieldtype": "Currency", "width": 130},
    ]

    conditions = ""
    values = {}
    if filters.get("vendor"):
        conditions += " AND oi.vendor = %(vendor)s"
        values["vendor"] = filters["vendor"]
    if filters.get("from_date"):
        conditions += " AND o.transaction_date >= %(from_date)s"
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions += " AND o.transaction_date <= %(to_date)s"
        values["to_date"] = filters["to_date"]

    data = frappe.db.sql(f"""
        SELECT
            oi.vendor,
            v.vendor_name,
            COUNT(DISTINCT oi.parent) as total_orders,
            SUM(oi.amount) as total_sales,
            SUM(oi.commission_amount) as total_commission,
            SUM(oi.vendor_earning) as vendor_earnings,
            AVG(oi.amount) as avg_order_value
        FROM `tabTN Order Item` oi
        JOIN `tabTN Order` o ON o.name = oi.parent
        JOIN `tabTN Vendor` v ON v.name = oi.vendor
        WHERE o.status NOT IN ('Cancelled', 'Refunded')
        {conditions}
        GROUP BY oi.vendor
        ORDER BY total_sales DESC
    """, values, as_dict=True)

    return columns, data
