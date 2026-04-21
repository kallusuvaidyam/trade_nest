import frappe
from frappe.model.document import Document
from frappe.utils import today, add_days

class TNOrder(Document):
    def before_insert(self):
        self.transaction_date = today()
        self.expected_delivery_date = add_days(today(), 7)
        if self.customer_user and not self.customer_email:
            self.customer_email = frappe.db.get_value("User", self.customer_user, "email")
        if self.customer_user and not self.customer_name:
            self.customer_name = frappe.db.get_value("User", self.customer_user, "full_name")

    def before_save(self):
        self._calculate_totals()
        self._run_fraud_check()

    def _calculate_totals(self):
        self.subtotal = 0
        for item in self.items:
            item.amount = (item.qty or 1) * (item.rate or 0)
            item.commission_amount = item.amount * ((item.commission_rate or 10) / 100)
            item.vendor_earning = item.amount - item.commission_amount
            self.subtotal += item.amount
        self.grand_total = self.subtotal + (self.shipping_charges or 0) - (self.discount_amount or 0)

    def _run_fraud_check(self):
        score = 0
        flags = []

        # Check: multiple orders from same user today
        today_orders = frappe.db.count("TN Order", {
            "customer_user": self.customer_user,
            "transaction_date": today(),
            "name": ["!=", self.name or ""]
        })
        if today_orders >= 5:
            score += 30
            flags.append("Multiple orders today")

        # Check: very high order value
        if (self.grand_total or 0) > 50000:
            score += 20
            flags.append("High order value")

        # Check: new account ordering
        user_creation = frappe.db.get_value("User", self.customer_user, "creation")
        if user_creation:
            from frappe.utils import date_diff, getdate
            days_old = date_diff(today(), getdate(user_creation))
            if days_old < 1:
                score += 25
                flags.append("New account")

        # Check: COD with high value
        if self.payment_method == "COD" and (self.grand_total or 0) > 10000:
            score += 15
            flags.append("High value COD")

        self.fraud_score = min(score, 100)
        self.fraud_flags = ", ".join(flags) if flags else ""
        self.is_flagged = 1 if score >= 50 else 0
