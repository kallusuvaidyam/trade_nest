import frappe
from frappe.model.document import Document

class TNProductReview(Document):
    def before_insert(self):
        if self.order and self.customer_email:
            order = frappe.db.get_value("TN Order", self.order, ["customer_email", "status"], as_dict=True)
            if order and order.customer_email == self.customer_email and order.status == "Delivered":
                self.is_verified_purchase = 1
