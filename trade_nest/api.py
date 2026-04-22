import frappe
import json
import hmac
import hashlib
import re
from frappe.utils import today, add_days
from frappe import _
from frappe.utils.file_manager import save_file



# ─── OTP Verification ────────────────────────────────────────────────────────
# REPLACE existing send_otp and verify_otp with these

@frappe.whitelist(allow_guest=True)
def send_otp(email):
    import random

    email = (email or "").strip().lower()
    if not email:
        frappe.throw("Email is required.")

    otp = str(random.randint(100000, 999999))
    frappe.cache().set_value(f"otp:{email}", otp, expires_in_sec=300)

    frappe.sendmail(
        recipients=[email],
        subject="Your OTP - TradeNest",
        message=f"""
        <div style="font-family:sans-serif;max-width:400px;margin:0 auto">
          <h2 style="color:#5b4fcf">TradeNest Verification</h2>
          <p>Your one-time password (OTP) is:</p>
          <div style="font-size:2rem;font-weight:800;letter-spacing:0.3rem;color:#1a1a2e;padding:1rem;background:#f5f2ff;border-radius:10px;text-align:center">{otp}</div>
          <p style="color:#888;font-size:0.85rem;margin-top:1rem">This OTP expires in 5 minutes. Do not share it with anyone.</p>
        </div>
        """,
        now=True
    )

    return {"success": True}


@frappe.whitelist(allow_guest=True)
def verify_otp(email, otp):
    email = (email or "").strip().lower()
    saved = frappe.cache().get_value(f"otp:{email}")

    if not saved or saved != str(otp).strip():
        frappe.throw("Invalid or expired OTP. Please try again.")

    # Clear OTP after successful verification
    frappe.cache().delete_value(f"otp:{email}")

    return {"success": True}


# ─── Signup ───────────────────────────────────────────────────────────────────
# REPLACE existing signup_customer with this (adds phone for Customer too)

@frappe.whitelist(allow_guest=True, methods=["POST"])
def signup_customer(
    email,
    full_name,
    password,
    account_type="Customer",
    vendor_name=None,
    store_name=None,
    phone=None,
    gst_number=None,
    address=None,
    store_description=None,
    bank_account_name=None,
    bank_name=None,
    bank_account_number=None,
    ifsc_code=None,
):
    if frappe.session.user != "Guest":
        return {"success": True, "already_logged_in": True}

    email = (email or "").strip().lower()
    full_name = (full_name or "").strip()
    password = password or ""
    account_type = (account_type or "Customer").strip().title()

    if not email or not full_name or not password:
        frappe.throw(_("Full name, email, and password are required."))

    if len(password) < 8:
        frappe.throw(_("Password must be at least 8 characters long."))

    if account_type not in {"Customer", "Vendor"}:
        frappe.throw(_("Please choose a valid account type."))

    if frappe.db.exists("User", email):
        frappe.throw(_("An account with this email already exists."))

    vendor_data = _build_vendor_signup_data(
        full_name=full_name,
        vendor_name=vendor_name,
        store_name=store_name,
        phone=phone,
        gst_number=gst_number,
        address=address,
        store_description=store_description,
        bank_account_name=bank_account_name,
        bank_name=bank_name,
        bank_account_number=bank_account_number,
        ifsc_code=ifsc_code,
    )

    if account_type == "Vendor" and (not vendor_data["store_name"] or not vendor_data["phone"]):
        frappe.throw(_("Store name and phone number are required for vendor registration."))

    # Normalize customer phone too
    customer_phone = ""
    if account_type == "Customer" and phone:
        try:
            customer_phone = _normalize_india_phone(phone)
        except Exception:
            customer_phone = ""

    first_name, _sep, last_name = full_name.partition(" ")
    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "full_name": full_name,
        "enabled": 1,
        "send_welcome_email": 0,
        "user_type": "Website User",
        "new_password": password,
        "mobile_no": vendor_data["phone"] if account_type == "Vendor" else customer_phone,
    })
    user.flags.ignore_permissions = True
    user.insert()

    if frappe.db.exists("Role", account_type):
        user.add_roles(account_type)

    if account_type == "Vendor":
        vendor = frappe.new_doc("TN Vendor")
        vendor.vendor_name = vendor_data["vendor_name"]
        vendor.store_name = vendor_data["store_name"]
        vendor.user = user.name
        vendor.email = user.email
        vendor.phone = vendor_data["phone"]
        vendor.gst_number = vendor_data["gst_number"]
        vendor.address = vendor_data["address"]
        vendor.store_description = vendor_data["store_description"]
        vendor.bank_account_name = vendor_data["bank_account_name"]
        vendor.bank_name = vendor_data["bank_name"]
        vendor.bank_account_number = vendor_data["bank_account_number"]
        vendor.ifsc_code = vendor_data["ifsc_code"]
        vendor.status = "Pending"
        vendor.commission_rate = 10
        vendor.insert(ignore_permissions=True)

        # Handle store image uploads
        files = frappe.request.files.getlist("store_images") if hasattr(frappe.request, "files") else []
        for i, file in enumerate(files[:3]):
            content = file.stream.read()
            if content:
                file_doc = save_file(
                    file.filename or f"store_image_{i+1}",
                    content,
                    "TN Vendor",
                    vendor.name,
                    folder="Home/Attachments",
                    is_private=0,
                )
                if i == 0:
                    frappe.db.set_value("TN Vendor", vendor.name, "store_logo", file_doc.file_url)

        return {
            "success": True,
            "account_type": account_type,
            "message": _("Vendor account created successfully. Your application is under review."),
            "vendor": vendor.name,
        }
    
    frappe.local.login_manager.login_as(user.name)
    frappe.db.commit()

    return {
        "success": True,
        "account_type": account_type,
        "message": _("Account created successfully. Please log in."),
    }


@frappe.whitelist(allow_guest=True)
def check_email_exists(email):
    email = (email or "").strip().lower()
    if frappe.db.exists("User", email):
        frappe.throw(_("An account with this email already exists."))
    return {"available": True}


# ─── OTP Verification ────────────────────────────────────────────────────────────────────
@frappe.whitelist(allow_guest=True)
def send_otp(email):
    import random

    otp = str(random.randint(100000, 999999))

    frappe.cache().set_value(f"otp:{email}", otp, expires_in_sec=300)

    frappe.sendmail(
        recipients=[email],
        subject="Your OTP - TradeNest",
        message=f"Your OTP is <b>{otp}</b>",
        now=True
    )

    return {"success": True}


@frappe.whitelist(allow_guest=True)
def verify_otp(email, otp):
    saved = frappe.cache().get_value(f"otp:{email}")

    if not saved or saved != otp:
        frappe.throw("Invalid OTP")

    return {"success": True}


# ─── Items ────────────────────────────────────────────────────────────────────

@frappe.whitelist(allow_guest=False)
def get_items(page=1, page_length=12, search="", category="", vendor=""):
    """Get items from TN Vendor Item (vendor-listed products) with fallback to ERPNext Item."""
    page = int(page)
    page_length = int(page_length)

    conditions = "vi.is_active = 1"
    values = {}

    if search:
        conditions += " AND (vi.item_name LIKE %(search)s OR i.description LIKE %(search)s)"
        values["search"] = f"%{search}%"
    if vendor:
        conditions += " AND vi.vendor = %(vendor)s"
        values["vendor"] = vendor
    if category:
        conditions += " AND i.item_group = %(category)s"
        values["category"] = category

    values["limit_start"] = (page - 1) * page_length
    values["page_length"] = page_length

    items = frappe.db.sql(f"""
        SELECT
            vi.name as vendor_item_id,
            vi.item_code,
            vi.item_name,
            vi.custom_price as price,
            vi.stock_qty,
            vi.commission_rate,
            vi.image,
            vi.description,
            vi.vendor,
            v.vendor_name,
            v.store_name,
            v.store_logo,
            i.item_group,
            i.stock_uom,
            COALESCE(
                (SELECT AVG(rating) FROM `tabTN Product Review` WHERE item_code = vi.item_code AND status = 'Approved'),
                0
            ) as avg_rating,
            (SELECT COUNT(*) FROM `tabTN Product Review` WHERE item_code = vi.item_code AND status = 'Approved') as review_count
        FROM `tabTN Vendor Item` vi
        JOIN `tabItem` i ON i.item_code = vi.item_code AND i.disabled = 0
        LEFT JOIN `tabTN Vendor` v ON v.name = vi.vendor
        WHERE {conditions}
        ORDER BY vi.modified DESC
        LIMIT %(limit_start)s, %(page_length)s
    """, values, as_dict=True)

    total_query = f"""
        SELECT COUNT(*) FROM `tabTN Vendor Item` vi
        JOIN `tabItem` i ON i.item_code = vi.item_code AND i.disabled = 0
        LEFT JOIN `tabTN Vendor` v ON v.name = vi.vendor
        WHERE {conditions}
    """
    total_values = {k: v for k, v in values.items() if k not in ("limit_start", "page_length")}
    total = frappe.db.sql(total_query, total_values)[0][0]

    import re
    for item in items:
        for field in ("image", "store_logo"):
            if item.get(field):
                item[field] = re.sub(r'^https?://localhost(:\d+)?', '', item[field])

    return {"items": items, "total": total}


@frappe.whitelist(allow_guest=False)
def get_item(item_code, vendor=None):
    """Get single item detail with vendor info and reviews."""
    if vendor:
        vi = frappe.db.get_value(
            "TN Vendor Item",
            {"item_code": item_code, "vendor": vendor, "is_active": 1},
            ["name", "item_code", "item_name", "custom_price", "stock_qty",
             "commission_rate", "image", "description", "vendor"],
            as_dict=True
        )
    else:
        vi = frappe.db.get_value(
            "TN Vendor Item",
            {"item_code": item_code, "is_active": 1},
            ["name", "item_code", "item_name", "custom_price", "stock_qty",
             "commission_rate", "image", "description", "vendor"],
            as_dict=True
        )

    if not vi:
        item = frappe.get_doc("Item", item_code, ignore_permissions=True)
        price = frappe.db.get_value(
            "Item Price",
            {"item_code": item_code, "selling": 1, "price_list": "Standard Selling"},
            "price_list_rate",
        )
        return {
            "item_code": item.item_code,
            "item_name": item.item_name,
            "description": item.description,
            "image": item.image,
            "price": price or 0,
            "stock_uom": item.stock_uom,
            "item_group": item.item_group,
        }

    vendor_doc = frappe.get_doc("TN Vendor", vi.vendor) if vi.vendor else None

    reviews = frappe.get_all(
        "TN Product Review",
        filters={"item_code": item_code, "status": "Approved"},
        fields=["customer_name", "rating", "title", "review_text", "is_verified_purchase", "creation"],
        order_by="creation desc",
        limit=10,
        ignore_permissions=True
    )

    avg_rating = frappe.db.sql(
        "SELECT AVG(rating) FROM `tabTN Product Review` WHERE item_code=%s AND status='Approved'",
        item_code
    )[0][0] or 0

    return {
        "vendor_item_id": vi.name,
        "item_code": vi.item_code,
        "item_name": vi.item_name,
        "price": vi.custom_price,
        "stock_qty": vi.stock_qty,
        "image": vi.image,
        "description": vi.description,
        "vendor": vi.vendor,
        "vendor_name": vendor_doc.vendor_name if vendor_doc else None,
        "store_name": vendor_doc.store_name if vendor_doc else None,
        "store_logo": vendor_doc.store_logo if vendor_doc else None,
        "avg_rating": round(float(avg_rating), 1),
        "reviews": reviews,
    }


# ─── Profile ──────────────────────────────────────────────────────────────────

def _build_profile_payload(user):
    doc = frappe.get_doc("User", user)

    vendor = frappe.db.get_value("TN Vendor", {"user": user}, ["name", "vendor_name", "status", "store_name"], as_dict=True)

    roles = frappe.get_roles(user)
    role_label = "Vendor" if "Vendor" in roles else ("System Manager" if "System Manager" in roles else "Customer")

    return {
        "name": doc.name,
        "full_name": doc.full_name,
        "email": doc.email,
        "user_image": doc.user_image,
        "role_profile_name": role_label,
        "roles": roles,
        "creation": str(doc.creation),
        "is_vendor": bool(vendor),
        "vendor": vendor,
    }


@frappe.whitelist(allow_guest=True)
def get_session_profile():
    user = frappe.session.user

    if user == "Guest":
        return {"authenticated": False}

    return {
        "authenticated": True,
        **_build_profile_payload(user),
    }


@frappe.whitelist(allow_guest=False)
def get_profile():
    return _build_profile_payload(frappe.session.user)


def _normalize_india_phone(phone):
    phone = (phone or "").strip()
    if not phone:
        return ""

    digits = re.sub(r"\D", "", phone)
    if digits.startswith("0") and len(digits) == 11:
        digits = digits[1:]
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]

    if len(digits) != 10:
        frappe.throw(_("Please enter a valid 10-digit Indian phone number."))

    return f"+91 {digits}"


def _build_vendor_signup_data(
    full_name,
    vendor_name=None,
    store_name=None,
    phone=None,
    gst_number=None,
    address=None,
    store_description=None,
    bank_account_name=None,
    bank_name=None,
    bank_account_number=None,
    ifsc_code=None,
):
    return {
        "vendor_name": (vendor_name or full_name or "").strip(),
        "store_name": (store_name or "").strip(),
        "phone": _normalize_india_phone(phone),
        "gst_number": (gst_number or "").strip().upper(),
        "address": (address or "").strip(),
        "store_description": (store_description or "").strip(),
        "bank_account_name": (bank_account_name or "").strip(),
        "bank_name": (bank_name or "").strip(),
        "bank_account_number": re.sub(r"\s+", "", (bank_account_number or "").strip()),
        "ifsc_code": (ifsc_code or "").strip().upper(),
    }


@frappe.whitelist(allow_guest=True, methods=["POST"])
def signup_customer(
    email,
    full_name,
    password,
    account_type="Customer",
    vendor_name=None,
    store_name=None,
    phone=None,
    gst_number=None,
    address=None,
    store_description=None,
    bank_account_name=None,
    bank_name=None,
    bank_account_number=None,
    ifsc_code=None,
):
    if frappe.session.user != "Guest":
        return {"success": True, "already_logged_in": True}

    email = (email or "").strip().lower()
    full_name = (full_name or "").strip()
    password = password or ""
    account_type = (account_type or "Customer").strip().title()

    if not email or not full_name or not password:
        frappe.throw(_("Full name, email, and password are required."))

    if len(password) < 8:
        frappe.throw(_("Password must be at least 8 characters long."))

    if account_type not in {"Customer", "Vendor"}:
        frappe.throw(_("Please choose a valid account type."))

    if frappe.db.exists("User", email):
        frappe.throw(_("An account with this email already exists."))

    vendor_data = _build_vendor_signup_data(
        full_name=full_name,
        vendor_name=vendor_name,
        store_name=store_name,
        phone=phone,
        gst_number=gst_number,
        address=address,
        store_description=store_description,
        bank_account_name=bank_account_name,
        bank_name=bank_name,
        bank_account_number=bank_account_number,
        ifsc_code=ifsc_code,
    )

    if account_type == "Vendor" and (not vendor_data["store_name"] or not vendor_data["phone"]):
        frappe.throw(_("Store name and phone number are required for vendor registration."))

    first_name, _sep, last_name = full_name.partition(" ")
    user = frappe.get_doc(
        {
            "doctype": "User",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "enabled": 1,
            "send_welcome_email": 0,
            "user_type": "Website User",
            "new_password": password,
            "mobile_no": vendor_data["phone"] if account_type == "Vendor" else "",
        }
    )
    user.flags.ignore_permissions = True
    user.insert()

    if frappe.db.exists("Role", account_type):
        user.add_roles(account_type)

    if account_type == "Vendor":
        vendor = frappe.new_doc("TN Vendor")
        vendor.vendor_name = vendor_data["vendor_name"]
        vendor.store_name = vendor_data["store_name"]
        vendor.user = user.name
        vendor.email = user.email
        vendor.phone = vendor_data["phone"]
        vendor.gst_number = vendor_data["gst_number"]
        vendor.address = vendor_data["address"]
        vendor.store_description = vendor_data["store_description"]
        vendor.bank_account_name = vendor_data["bank_account_name"]
        vendor.bank_name = vendor_data["bank_name"]
        vendor.bank_account_number = vendor_data["bank_account_number"]
        vendor.ifsc_code = vendor_data["ifsc_code"]
        vendor.status = "Pending"
        vendor.commission_rate = 10
        vendor.insert(ignore_permissions=True)

        return {
            "success": True,
            "account_type": account_type,
            "message": _("Vendor account created successfully. Please log in."),
            "vendor": vendor.name,
        }

    return {
        "success": True,
        "account_type": account_type,
        "message": _("Customer account created successfully. Please log in."),
    }


@frappe.whitelist(allow_guest=False)
def update_profile(full_name=None, user_image=None):
    user = frappe.session.user
    doc = frappe.get_doc("User", user)
    if full_name:
        doc.full_name = full_name
        doc.first_name = full_name.split()[0]
        doc.last_name = " ".join(full_name.split()[1:]) if len(full_name.split()) > 1 else ""
    if user_image:
        doc.user_image = user_image
    doc.save(ignore_permissions=True)
    return {"success": True}


@frappe.whitelist(allow_guest=False, methods=["POST"])
def upload_profile_image():
    if "file" not in frappe.request.files:
        frappe.throw(_("Please choose an image to upload."))

    user = frappe.session.user
    image = frappe.request.files["file"]
    filename = image.filename or "profile-image"
    content_type = getattr(image, "content_type", "") or ""

    if content_type and not content_type.startswith("image/"):
        frappe.throw(_("Only image files are allowed for profile photos."))

    content = image.stream.read()
    if not content:
        frappe.throw(_("Uploaded image is empty."))

    file_doc = save_file(
        filename,
        content,
        "User",
        user,
        folder="Home/Attachments",
        is_private=0,
        df="user_image",
    )

    doc = frappe.get_doc("User", user)
    doc.user_image = file_doc.file_url
    doc.save(ignore_permissions=True)

    return {
        "file_name": file_doc.file_name,
        "file_url": file_doc.file_url,
        "user_image": doc.user_image,
    }


# ─── Customer Addresses ───────────────────────────────────────────────────────

@frappe.whitelist(allow_guest=False)
def get_my_addresses():
    user = frappe.session.user
    addresses = frappe.get_all(
        "TN Customer Address",
        filters={"customer_user": user},
        fields=["name", "label", "address", "is_default"],
        order_by="is_default desc, modified desc",
        ignore_permissions=True,
    )
    return addresses


@frappe.whitelist(allow_guest=False)
def save_address(label, address, name=None, set_default=0):
    user = frappe.session.user
    set_default = int(set_default)

    if name and frappe.db.exists("TN Customer Address", name):
        doc = frappe.get_doc("TN Customer Address", name)
        if doc.customer_user != user:
            frappe.throw("Not authorized", frappe.PermissionError)
        doc.label = label
        doc.address = address
        doc.save(ignore_permissions=True)
    else:
        doc = frappe.new_doc("TN Customer Address")
        doc.customer_user = user
        doc.label = label
        doc.address = address
        doc.is_default = 0
        doc.insert(ignore_permissions=True)

    if set_default:
        frappe.db.set_value("TN Customer Address", {"customer_user": user, "name": ["!=", doc.name]}, "is_default", 0)
        frappe.db.set_value("TN Customer Address", doc.name, "is_default", 1)
        frappe.db.commit()

    return {"name": doc.name, "label": doc.label, "address": doc.address, "is_default": bool(set_default)}


@frappe.whitelist(allow_guest=False)
def delete_address(name):
    user = frappe.session.user
    doc = frappe.get_doc("TN Customer Address", name)
    if doc.customer_user != user:
        frappe.throw("Not authorized", frappe.PermissionError)
    doc.delete(ignore_permissions=True)
    return {"success": True}


# ─── Vendor Registration ───────────────────────────────────────────────────────

@frappe.whitelist(allow_guest=False)
def register_as_vendor(
    vendor_name,
    store_name,
    phone,
    gst_number="",
    address="",
    store_description="",
    bank_account_name="",
    bank_name="",
    bank_account_number="",
    ifsc_code="",
):
    user = frappe.session.user
    user_doc = frappe.get_doc("User", user)

    existing = frappe.db.exists("TN Vendor", {"user": user})
    if existing:
        frappe.throw("You are already registered as a vendor.")

    vendor_data = _build_vendor_signup_data(
        full_name=user_doc.full_name,
        vendor_name=vendor_name,
        store_name=store_name,
        phone=phone,
        gst_number=gst_number,
        address=address,
        store_description=store_description,
        bank_account_name=bank_account_name,
        bank_name=bank_name,
        bank_account_number=bank_account_number,
        ifsc_code=ifsc_code,
    )

    vendor = frappe.new_doc("TN Vendor")
    vendor.vendor_name = vendor_data["vendor_name"]
    vendor.store_name = vendor_data["store_name"]
    vendor.user = user
    vendor.email = user_doc.email
    vendor.phone = vendor_data["phone"]
    vendor.gst_number = vendor_data["gst_number"]
    vendor.address = vendor_data["address"]
    vendor.store_description = vendor_data["store_description"]
    vendor.bank_account_name = vendor_data["bank_account_name"]
    vendor.bank_name = vendor_data["bank_name"]
    vendor.bank_account_number = vendor_data["bank_account_number"]
    vendor.ifsc_code = vendor_data["ifsc_code"]
    vendor.status = "Pending"
    vendor.commission_rate = 10
    vendor.insert(ignore_permissions=True)

    frappe.sendmail(
        recipients=[user_doc.email],
        subject="Vendor Registration Received - Trade Nest",
        message=f"""
        <h2>Thank you for registering as a Vendor!</h2>
        <p>Dear {vendor_name},</p>
        <p>We have received your vendor registration request for <b>{store_name}</b>.</p>
        <p>Our team will review your application and get back to you within 24-48 hours.</p>
        <p>You will receive an email once your account is approved.</p>
        <br><p>- Trade Nest Team</p>
        """,
        now=True
    )

    admin_email = frappe.db.get_value("User", "Administrator", "email")
    if admin_email:
        frappe.sendmail(
            recipients=[admin_email],
            subject=f"New Vendor Registration: {vendor_name}",
            message=f"""
            <h2>New Vendor Registration</h2>
            <p><b>Vendor Name:</b> {vendor_data["vendor_name"]}</p>
            <p><b>Store Name:</b> {vendor_data["store_name"]}</p>
            <p><b>Email:</b> {user_doc.email}</p>
            <p><b>Phone:</b> {vendor_data["phone"]}</p>
            <p>Please review and approve/reject in the <a href="/app/tn-vendor/{vendor.name}">Trade Nest Admin</a>.</p>
            """,
            now=True
        )

    return {"success": True, "vendor": vendor.name, "status": "Pending"}


# ─── Orders ───────────────────────────────────────────────────────────────────

@frappe.whitelist(allow_guest=False)
def place_order(items, payment_method="COD", shipping_address="", notes=""):
    if isinstance(items, str):
        items = json.loads(items)

    user = frappe.session.user
    user_doc = frappe.get_doc("User", user)

    order = frappe.new_doc("TN Order")
    order.customer_user = user
    order.customer_name = user_doc.full_name
    order.customer_email = user_doc.email
    order.payment_method = payment_method
    order.payment_status = "Pending"
    order.status = "Placed"
    order.shipping_address = shipping_address
    order.notes = notes

    vendor_set = set()
    for i in items:
        item_code = i.get("item_code")
        vendor_item_id = i.get("vendor_item_id")

        vendor_data = None
        if vendor_item_id:
            vendor_data = frappe.db.get_value(
                "TN Vendor Item", vendor_item_id,
                ["vendor", "commission_rate", "custom_price"],
                as_dict=True
            )
        if not vendor_data and item_code:
            vendor_data = frappe.db.get_value(
                "TN Vendor Item",
                {"item_code": item_code, "is_active": 1},
                ["vendor", "commission_rate", "custom_price"],
                as_dict=True
            )

        commission_rate = vendor_data.commission_rate if vendor_data else 10
        vendor = vendor_data.vendor if vendor_data else None
        rate = i.get("price") or (vendor_data.custom_price if vendor_data else 0)

        if vendor:
            vendor_set.add(vendor)

        order.append("items", {
            "item_code": item_code,
            "item_name": i.get("item_name", item_code),
            "vendor": vendor,
            "qty": i.get("qty", 1),
            "rate": rate,
            "commission_rate": commission_rate,
            "image": i.get("image", ""),
        })

    order.insert(ignore_permissions=True)

    _create_commission_records(order)
    _send_order_emails(order, vendor_set)
    _notify_admin_realtime(order.name, user_doc.full_name, order.grand_total)

    so_name = None
    try:
        so_name = _create_sales_order(order, user_doc)
        if so_name:
            frappe.db.set_value("TN Order", order.name, "sales_order", so_name)
    except Exception:
        pass  # Sales Order creation is best-effort, don't fail the main order

    return {
        "order": order.name,
        "sales_order": so_name,
        "customer": user,
        "grand_total": order.grand_total,
        "payment_method": payment_method,
        "fraud_score": order.fraud_score,
        "is_flagged": order.is_flagged,
        "items": [
            {"item_code": i.item_code, "item_name": i.item_name, "qty": i.qty, "amount": i.amount}
            for i in order.items
        ],
    }


def _create_sales_order(order, user_doc):
    """Create and submit an ERPNext Sales Order linked to the TN Order."""
    from frappe.utils import add_days, today as _today

    # Find or create ERPNext Customer
    customer_name = frappe.db.get_value("Customer", {"email_id": user_doc.email})
    if not customer_name:
        cust = frappe.new_doc("Customer")
        cust.customer_name = user_doc.full_name or user_doc.email.split("@")[0]
        cust.customer_type = "Individual"
        cust.customer_group = frappe.db.get_value("Customer Group", {"is_group": 0}, "name") or "All Customer Groups"
        cust.territory = frappe.db.get_value("Territory", {"is_group": 0}, "name") or "All Territories"
        cust.email_id = user_doc.email
        cust.insert(ignore_permissions=True)
        customer_name = cust.name

    so = frappe.new_doc("Sales Order")
    so.customer = customer_name
    so.order_type = "Sales"
    so.delivery_date = add_days(_today(), 7)
    so.custom_tn_order = order.name

    default_price_list = frappe.db.get_value("Price List", {"selling": 1, "enabled": 1}, "name") or "Standard Selling"
    so.selling_price_list = default_price_list

    for item in order.items:
        if not item.item_code or not item.rate:
            continue
        so.append("items", {
            "item_code": item.item_code,
            "item_name": item.item_name,
            "qty": item.qty,
            "rate": item.rate,
            "delivery_date": add_days(_today(), 7),
        })

    if not so.items:
        return None

    so.insert(ignore_permissions=True)
    so.submit()
    return so.name


def _create_commission_records(order):
    """Create TN Commission records for each vendor item in the order."""
    from frappe.utils import today as _today
    for item in order.items:
        if item.vendor and item.commission_amount:
            frappe.get_doc({
                "doctype": "TN Commission",
                "vendor": item.vendor,
                "order": order.name,
                "item_code": item.item_code,
                "item_name": item.item_name,
                "amount": item.commission_amount,
                "commission_rate": item.commission_rate,
                "status": "Pending",
                "transaction_date": _today(),
            }).insert(ignore_permissions=True)

    vendors_in_order = {}
    for item in order.items:
        if item.vendor:
            vendors_in_order[item.vendor] = vendors_in_order.get(item.vendor, 0) + item.amount

    for vendor_name, amount in vendors_in_order.items():
        frappe.db.set_value("TN Vendor", vendor_name,
            "total_sales",
            (frappe.db.get_value("TN Vendor", vendor_name, "total_sales") or 0) + amount
        )

    if order.is_flagged:
        frappe.get_doc({
            "doctype": "TN Fraud Log",
            "user_email": order.customer_email,
            "order": order.name,
            "risk_score": order.fraud_score,
            "flags": order.fraud_flags,
            "action_taken": "Flagged",
        }).insert(ignore_permissions=True)


def _send_order_emails(order, vendor_set):
    """Send order confirmation to customer, notification to vendors and admin."""
    items_html = "".join([
        f"<tr><td>{i.item_name}</td><td>{i.qty}</td><td>\u20b9{i.rate}</td><td>\u20b9{i.amount}</td></tr>"
        for i in order.items
    ])

    order_table = f"""
    <table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;width:100%">
      <thead style="background:#f0f0f0">
        <tr><th>Item</th><th>Qty</th><th>Rate</th><th>Amount</th></tr>
      </thead>
      <tbody>{items_html}</tbody>
      <tfoot>
        <tr><td colspan="3"><b>Grand Total</b></td><td><b>\u20b9{order.grand_total}</b></td></tr>
      </tfoot>
    </table>
    """

    frappe.sendmail(
        recipients=[order.customer_email],
        subject=f"Order Confirmed: {order.name} - Trade Nest",
        message=f"""
        <h2>Thank you for your order!</h2>
        <p>Dear {order.customer_name},</p>
        <p>Your order <b>{order.name}</b> has been placed successfully.</p>
        <br>
        <h3>Order Details</h3>
        {order_table}
        <p><b>Payment Method:</b> {order.payment_method}</p>
        <p><b>Expected Delivery:</b> {order.expected_delivery_date}</p>
        {f'<p><b>Shipping To:</b> {order.shipping_address}</p>' if order.shipping_address else ''}
        <br>
        <p>You can track your order at <a href="/shop#/orders">My Orders</a></p>
        <br><p>- Trade Nest Team</p>
        """,
        now=False
    )

    for vendor_name in vendor_set:
        vendor_doc = frappe.get_doc("TN Vendor", vendor_name)
        # Prefer the linked Frappe user's email (always valid), fallback to vendor.email
        vendor_email = None
        if vendor_doc.user:
            vendor_email = frappe.db.get_value("User", vendor_doc.user, "email")
        if not vendor_email:
            vendor_email = vendor_doc.email
        if not vendor_email:
            continue

        vendor_items = [i for i in order.items if i.vendor == vendor_name]
        vendor_items_html = "".join([
            f"<tr><td>{i.item_name}</td><td>{i.qty}</td><td>\u20b9{i.rate}</td><td>\u20b9{i.amount}</td><td>\u20b9{i.vendor_earning}</td></tr>"
            for i in vendor_items
        ])
        vendor_total = sum(i.amount for i in vendor_items)
        vendor_earning = sum(i.vendor_earning for i in vendor_items)

        frappe.sendmail(
            recipients=[vendor_email],
            subject=f"New Order Received: {order.name} - Trade Nest",
            message=f"""
            <h2>New Order for Your Products!</h2>
            <p>Dear {vendor_doc.vendor_name},</p>
            <p>You have received a new order <b>{order.name}</b>.</p>
            <br>
            <h3>Your Items in This Order</h3>
            <table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;width:100%">
              <thead style="background:#f0f0f0">
                <tr><th>Item</th><th>Qty</th><th>Rate</th><th>Amount</th><th>Your Earning</th></tr>
              </thead>
              <tbody>{vendor_items_html}</tbody>
              <tfoot>
                <tr><td colspan="3"><b>Total</b></td><td><b>\u20b9{vendor_total}</b></td><td><b>\u20b9{vendor_earning}</b></td></tr>
              </tfoot>
            </table>
            <p><b>Customer:</b> {order.customer_name}</p>
            <p><b>Payment Method:</b> {order.payment_method}</p>
            {f'<p><b>Ship To:</b> {order.shipping_address}</p>' if order.shipping_address else ''}
            <br>
            <p>Manage your orders at <a href="/app/tn-order/{order.name}">Vendor Portal</a></p>
            <br><p>- Trade Nest Team</p>
            """,
            now=False
        )

    # Admin gets desk notification only (no email) — see _notify_admin_realtime


def _notify_admin_realtime(order_name, customer_name, grand_total):
    try:
        # Realtime popup on Frappe desk
        frappe.publish_realtime(
            event="new_order",
            message={
                "title": "New Order!",
                "order_name": order_name,
                "customer": customer_name,
                "grand_total": grand_total,
            },
            user="Administrator",
        )

        # Persistent system notification (bell icon in Frappe desk)
        admin_users = frappe.db.sql("""
            SELECT DISTINCT u.name FROM `tabUser` u
            JOIN `tabHas Role` hr ON hr.parent = u.name
            WHERE hr.role = 'System Manager' AND u.enabled = 1
            AND u.name NOT IN ('Guest', 'Administrator')
            LIMIT 5
        """, as_list=True)
        notify_users = [r[0] for r in admin_users] or ["Administrator"]

        for admin_user in notify_users:
            frappe.get_doc({
                "doctype": "Notification Log",
                "subject": f"New Order: {order_name} — ₹{grand_total}",
                "email_content": f"Customer <b>{customer_name}</b> placed order <b>{order_name}</b> worth ₹{grand_total}.",
                "for_user": admin_user,
                "from_user": "Administrator",
                "document_type": "TN Order",
                "document_name": order_name,
                "type": "Alert",
                "read": 0,
            }).insert(ignore_permissions=True)

    except Exception:
        frappe.log_error(frappe.get_traceback(), "TradeNest: realtime notify failed")


@frappe.whitelist(allow_guest=False)
def get_orders(page=1, page_size=10):
    page = int(page)
    page_size = int(page_size)
    user = frappe.session.user

    total = frappe.db.count("TN Order", {"customer_user": user})

    orders = frappe.get_list(
        "TN Order",
        filters={"customer_user": user},
        fields=["name", "transaction_date", "grand_total", "status",
                "payment_method", "payment_status", "expected_delivery_date",
                "fraud_score", "is_flagged"],
        order_by="creation desc",
        limit_start=(page - 1) * page_size,
        limit_page_length=page_size,
        ignore_permissions=True,
    )

    for order in orders:
        order["items"] = frappe.get_all(
            "TN Order Item",
            filters={"parent": order["name"]},
            fields=["item_code", "item_name", "vendor", "vendor_name", "qty", "rate", "amount", "image"],
            ignore_permissions=True,
        )

    return {"orders": orders, "total": total}


@frappe.whitelist(allow_guest=False)
def get_order(name):
    user = frappe.session.user
    order = frappe.get_doc("TN Order", name, ignore_permissions=True)

    if order.customer_user != user:
        has_vendor_items = frappe.db.exists("TN Order Item", {
            "parent": name,
            "vendor": frappe.db.get_value("TN Vendor", {"user": user}, "name")
        })
        if not has_vendor_items:
            frappe.throw("Unauthorized", frappe.PermissionError)

    return order.as_dict()


@frappe.whitelist(allow_guest=False)
def cancel_order(name, reason=""):
    user = frappe.session.user
    order = frappe.get_doc("TN Order", name, ignore_permissions=True)

    if order.customer_user != user:
        frappe.throw("Unauthorized", frappe.PermissionError)

    if order.status not in ("Placed", "Processing"):
        frappe.throw(f"Order cannot be cancelled in '{order.status}' status.")

    order.status = "Cancelled"
    order.notes = (order.notes or "") + f"\nCancelled by customer. Reason: {reason}"
    order.save(ignore_permissions=True)

    frappe.db.set_value("TN Commission", {"order": name, "status": "Pending"}, "status", "Cancelled")

    return {"success": True}


# ─── Reviews ──────────────────────────────────────────────────────────────────

@frappe.whitelist(allow_guest=False)
def submit_review(item_code, order, rating, title="", review_text=""):
    user = frappe.session.user
    user_doc = frappe.get_doc("User", user)

    order_doc = frappe.get_doc("TN Order", order, ignore_permissions=True)
    if order_doc.customer_user != user:
        frappe.throw("Unauthorized", frappe.PermissionError)

    if frappe.db.exists("TN Product Review", {"item_code": item_code, "customer_email": user_doc.email, "order": order}):
        frappe.throw("You have already reviewed this product for this order.")

    vendor = frappe.db.get_value("TN Order Item", {"parent": order, "item_code": item_code}, "vendor")

    review = frappe.new_doc("TN Product Review")
    review.item_code = item_code
    review.vendor = vendor
    review.order = order
    review.customer_email = user_doc.email
    review.customer_name = user_doc.full_name
    review.rating = int(rating)
    review.title = title
    review.review_text = review_text
    review.status = "Pending"
    review.insert(ignore_permissions=True)

    return {"success": True, "review": review.name}


@frappe.whitelist(allow_guest=False)
def get_reviews(item_code, page=1):
    page = int(page)
    reviews = frappe.get_all(
        "TN Product Review",
        filters={"item_code": item_code, "status": "Approved"},
        fields=["customer_name", "rating", "title", "review_text", "is_verified_purchase", "creation"],
        order_by="creation desc",
        limit_start=(page - 1) * 10,
        limit_page_length=10,
        ignore_permissions=True
    )
    avg = frappe.db.sql(
        "SELECT AVG(rating), COUNT(*) FROM `tabTN Product Review` WHERE item_code=%s AND status='Approved'",
        item_code
    )[0]
    return {"reviews": reviews, "avg_rating": round(float(avg[0] or 0), 1), "total_reviews": avg[1]}


# ─── Razorpay Online Payment ───────────────────────────────────────────────────

@frappe.whitelist(allow_guest=False)
def create_razorpay_order(order_name):
    try:
        import razorpay
    except ImportError:
        frappe.throw("Razorpay module not installed. Run: bench pip install razorpay")

    conf = frappe.get_site_config()
    key_id = conf.get("razorpay_key_id", "")
    key_secret = conf.get("razorpay_key_secret", "")

    if not key_id or "REPLACE" in key_id:
        frappe.throw("Razorpay keys not configured. Contact admin.")

    order = frappe.get_doc("TN Order", order_name, ignore_permissions=True)
    amount_paise = int(order.grand_total * 100)

    client = razorpay.Client(auth=(key_id, key_secret))
    rz_order = client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "receipt": order_name,
        "notes": {"tn_order": order_name},
    })

    frappe.db.set_value("TN Order", order_name, "razorpay_order_id", rz_order["id"])

    return {
        "razorpay_order_id": rz_order["id"],
        "amount": amount_paise,
        "currency": "INR",
        "key_id": key_id,
        "order_name": order_name,
        "grand_total": order.grand_total,
    }


@frappe.whitelist(allow_guest=False)
def verify_razorpay_payment(razorpay_payment_id, razorpay_order_id, razorpay_signature, order_name):
    conf = frappe.get_site_config()
    key_secret = conf.get("razorpay_key_secret", "")

    body = f"{razorpay_order_id}|{razorpay_payment_id}"
    expected = hmac.new(key_secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    if expected != razorpay_signature:
        frappe.throw("Payment verification failed. Invalid signature.")

    frappe.db.set_value("TN Order", order_name, {
        "razorpay_payment_id": razorpay_payment_id,
        "payment_status": "Paid",
        "status": "Processing",
    })

    return {
        "success": True,
        "order_name": order_name,
    }
