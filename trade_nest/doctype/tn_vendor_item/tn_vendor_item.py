import frappe
from frappe.model.document import Document

class TNVendorItem(Document):
    def before_save(self):
        if not self.commission_rate:
            self.commission_rate = frappe.db.get_value("TN Vendor", self.vendor, "commission_rate") or 10
