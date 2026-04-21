import frappe

def execute(filters=None):
    filters = filters or {}

    columns = [
        {"fieldname": "date", "label": "Date", "fieldtype": "Date", "width": 110},
        {"fieldname": "total_orders", "label": "Orders", "fieldtype": "Int", "width": 80},
        {"fieldname": "total_revenue", "label": "Revenue", "fieldtype": "Currency", "width": 130},
        {"fieldname": "cod_orders", "label": "COD Orders", "fieldtype": "Int", "width": 100},
        {"fieldname": "online_orders", "label": "Online Orders", "fieldtype": "Int", "width": 100},
        {"fieldname": "avg_order_value", "label": "Avg Order Value", "fieldtype": "Currency", "width": 130},
        {"fieldname": "flagged_orders", "label": "Flagged", "fieldtype": "Int", "width": 80},
    ]

    conditions = "WHERE status NOT IN ('Draft', 'Cancelled')"
    values = {}
    if filters.get("from_date"):
        conditions += " AND transaction_date >= %(from_date)s"
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions += " AND transaction_date <= %(to_date)s"
        values["to_date"] = filters["to_date"]

    data = frappe.db.sql(f"""
        SELECT
            transaction_date as date,
            COUNT(*) as total_orders,
            SUM(grand_total) as total_revenue,
            SUM(CASE WHEN payment_method = 'COD' THEN 1 ELSE 0 END) as cod_orders,
            SUM(CASE WHEN payment_method = 'Online' THEN 1 ELSE 0 END) as online_orders,
            AVG(grand_total) as avg_order_value,
            SUM(is_flagged) as flagged_orders
        FROM `tabTN Order`
        {conditions}
        GROUP BY transaction_date
        ORDER BY transaction_date DESC
    """, values, as_dict=True)

    return columns, data
