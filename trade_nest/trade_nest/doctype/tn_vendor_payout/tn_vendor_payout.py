import frappe
from frappe.model.document import Document
from frappe.utils import today

class TNVendorPayout(Document):
    def before_save(self):
        self._calculate_payout()

    def _calculate_payout(self):
        filters = {"vendor": self.vendor, "status": "Pending"}
        if self.period_from:
            filters["transaction_date"] = [">=", self.period_from]
        if self.period_to:
            filters["transaction_date"] = ["<=", self.period_to]

        commissions = frappe.get_all("TN Commission", filters=filters, fields=["amount", "order"])
        self.total_orders = len(set(c["order"] for c in commissions))
        self.total_commission = sum(c["amount"] for c in commissions)

        orders = list(set(c["order"] for c in commissions))
        if orders:
            total_sales = 0
            for order in orders:
                items = frappe.get_all("TN Order Item", filters={"parent": order, "vendor": self.vendor}, fields=["amount"])
                total_sales += sum(i["amount"] for i in items)
            self.total_sales = total_sales

        self.net_payable = (self.total_sales or 0) - (self.total_commission or 0)

    def on_submit(self):
        frappe.db.set_value("TN Commission",
            {"vendor": self.vendor, "status": "Pending"},
            {"status": "Paid", "payout_ref": self.name}
        )
        vendor = frappe.get_doc("TN Vendor", self.vendor)
        vendor.total_commission_paid = (vendor.total_commission_paid or 0) + (self.total_commission or 0)
        vendor.save(ignore_permissions=True)

        vendor_email = frappe.db.get_value("TN Vendor", self.vendor, "email")
        if vendor_email:
            frappe.sendmail(
                recipients=[vendor_email],
                subject=f"Payout Processed - \u20b9{self.net_payable} - Trade Nest",
                message=f"""
                <h2>Payout Processed!</h2>
                <p>Dear {self.vendor_name},</p>
                <p>Your payout of <b>\u20b9{self.net_payable}</b> has been processed.</p>
                <table border="1" cellpadding="8" style="border-collapse:collapse;">
                  <tr><td><b>Payout ID</b></td><td>{self.name}</td></tr>
                  <tr><td><b>Period</b></td><td>{self.period_from} to {self.period_to}</td></tr>
                  <tr><td><b>Total Orders</b></td><td>{self.total_orders}</td></tr>
                  <tr><td><b>Total Sales</b></td><td>\u20b9{self.total_sales}</td></tr>
                  <tr><td><b>Commission Deducted</b></td><td>\u20b9{self.total_commission}</td></tr>
                  <tr><td><b>Net Payable</b></td><td><b>\u20b9{self.net_payable}</b></td></tr>
                  <tr><td><b>Payment Reference</b></td><td>{self.payment_reference or 'N/A'}</td></tr>
                </table>
                <br><p>- Trade Nest Team</p>
                """,
                now=True
            )
