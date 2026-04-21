import frappe
from frappe.model.document import Document

class TNVendor(Document):
    def before_save(self):
        if self.user and not self.email:
            self.email = frappe.db.get_value("User", self.user, "email")

    def on_update(self):
        if self.has_value_changed("status"):
            self._notify_status_change()

    def _notify_status_change(self):
        if self.status == "Approved":
            frappe.sendmail(
                recipients=[self.email],
                subject="Your Vendor Account is Approved - Trade Nest",
                message=f"""
                <h2>Congratulations {self.vendor_name}!</h2>
                <p>Your vendor account on <b>Trade Nest</b> has been <b>approved</b>.</p>
                <p>You can now login and start adding products to your store: <b>{self.store_name or self.vendor_name}</b></p>
                <p>Login at: <a href="/shop">Trade Nest</a></p>
                <br><p>- Trade Nest Team</p>
                """,
                now=True
            )
        elif self.status == "Suspended":
            frappe.sendmail(
                recipients=[self.email],
                subject="Vendor Account Suspended - Trade Nest",
                message=f"""
                <h2>Account Suspended</h2>
                <p>Dear {self.vendor_name}, your vendor account has been temporarily suspended.</p>
                <p>Please contact support for more information.</p>
                <br><p>- Trade Nest Team</p>
                """,
                now=True
            )
