const BASE = "/api";

function getCsrfToken() {
	return (
		document.cookie
			.split("; ")
			.find((r) => r.startsWith("csrf_token="))
			?.split("=")[1] || "fetch"
	);
}

function redirectToLogin(forceReload = false) {
	const target = forceReload ? `/shop?logout=${Date.now()}#/login` : "/shop#/login";

	window.location.replace(target);
}

function extractErrorMessage(json) {
	if (json?._server_messages) {
		try {
			const messages = JSON.parse(json._server_messages);
			const first = messages?.[0] ? JSON.parse(messages[0]) : null;
			if (first?.message) {
				return first.message.replace(/<[^>]+>/g, "").trim();
			}
		} catch {
			// fall back to the remaining error fields
		}
	}

	if (typeof json?.message === "string" && json.message.trim()) {
		return json.message;
	}

	if (typeof json?.exception === "string" && json.exception.trim()) {
		return json.exception.split(":").slice(1).join(":").trim() || json.exception;
	}

	if (typeof json?.exc === "string" && json.exc.trim()) {
		return json.exc;
	}

	return "API Error";
}

async function request(method, endpoint, data = null) {
	const options = {
		method,
		headers: {
			"Content-Type": "application/json",
			"X-Frappe-CSRF-Token": getCsrfToken(),
		},
		credentials: "include",
	};
	if (data) options.body = JSON.stringify(data);

	const res = await fetch(`${BASE}${endpoint}`, options);
	const json = await res.json();
	if (res.status === 403 || res.status === 401) {
		if (json.message === "Not permitted" || json.exc_type === "AuthenticationError") {
			redirectToLogin(true);
			return;
		}
	}
	if (!res.ok) throw new Error(extractErrorMessage(json));
	return json;
}

export const api = {
	// Auth
	getSessionProfile: () => request("GET", "/method/trade_nest.api.get_session_profile"),
	getProfile: () => request("GET", "/method/trade_nest.api.get_profile"),
	updateProfile: (data) => request("POST", "/method/trade_nest.api.update_profile", data),
	signup: async (formData) => {
		const res = await fetch("/api/method/trade_nest.api.signup_customer", {
			method: "POST",
			headers: { "X-Frappe-CSRF-Token": getCsrfToken() },
			credentials: "include",
			body: formData,
		});
		const json = await res.json();
		if (!res.ok) throw new Error(extractErrorMessage(json));
		return json;
	},
	uploadProfileImage: async (file) => {
		const form = new FormData();
		form.append("file", file, file.name);
		const res = await fetch("/api/method/trade_nest.api.upload_profile_image", {
			method: "POST",
			headers: { "X-Frappe-CSRF-Token": getCsrfToken() },
			credentials: "include",
			body: form,
		});
		const json = await res.json();
		if (!res.ok) throw new Error(extractErrorMessage(json));
		return json;
	},

	login: async (usr, pwd) => {
		const res = await fetch("/api/method/login", {
			method: "POST",
			headers: {
				"Content-Type": "application/x-www-form-urlencoded",
				"X-Frappe-CSRF-Token": getCsrfToken(),
			},
			credentials: "include",
			body: new URLSearchParams({ usr, pwd }),
		});
		const json = await res.json();
		if (!res.ok) throw new Error(json.message || "Login failed");
		return json;
	},
	forgotPassword: (email) =>
		request("POST", "/method/frappe.core.reset_password", { user: email }),
	logout: async () => {
		await request("POST", "/method/logout");
		redirectToLogin(true);
	},

	// Items
	getItems: (page = 1, search = "", pageSize = 12, category = "", vendor = "") =>
		request(
			"GET",
			`/method/trade_nest.api.get_items?page=${page}&search=${encodeURIComponent(search)}&page_length=${pageSize}&category=${encodeURIComponent(category)}&vendor=${encodeURIComponent(vendor)}`,
		),
	getItem: (item_code, vendor = "") =>
		request(
			"GET",
			`/method/trade_nest.api.get_item?item_code=${encodeURIComponent(item_code)}&vendor=${encodeURIComponent(vendor)}`,
		),

	// Orders
	placeOrder: (items, payment_method = "COD", shipping_address = "", notes = "") =>
		request("POST", "/method/trade_nest.api.place_order", {
			items: JSON.stringify(items),
			payment_method,
			shipping_address,
			notes,
		}),
	getOrders: (page = 1, pageSize = 10) =>
		request("GET", `/method/trade_nest.api.get_orders?page=${page}&page_size=${pageSize}`),
	getOrder: (name) =>
		request("GET", `/method/trade_nest.api.get_order?name=${encodeURIComponent(name)}`),
	cancelOrder: (name, reason = "") =>
		request("POST", "/method/trade_nest.api.cancel_order", { name, reason }),

	// Reviews
	submitReview: (data) => request("POST", "/method/trade_nest.api.submit_review", data),
	getReviews: (item_code, page = 1) =>
		request(
			"GET",
			`/method/trade_nest.api.get_reviews?item_code=${encodeURIComponent(item_code)}&page=${page}`,
		),

	// Addresses
	getMyAddresses: () => request("GET", "/method/trade_nest.api.get_my_addresses"),
	saveAddress: (data) => request("POST", "/method/trade_nest.api.save_address", data),
	deleteAddress: (name) => request("POST", "/method/trade_nest.api.delete_address", { name }),

	// Vendor registration (customer → vendor)
	registerAsVendor: (data) => request("POST", "/method/trade_nest.api.register_as_vendor", data),

	checkEmailExists: (email) =>
		request("POST", "/method/trade_nest.api.check_email_exists", { email }),
	sendOtp: (email) => request("POST", "/method/trade_nest.api.send_otp", { email }),
	verifyOtp: (email, otp) =>
		request("POST", "/method/trade_nest.api.verify_otp", { email, otp }),

	// Razorpay
	createRazorpayOrder: (order_name) =>
		request("POST", "/method/trade_nest.api.create_razorpay_order", { order_name }),
	verifyRazorpayPayment: (data) =>
		request("POST", "/method/trade_nest.api.verify_razorpay_payment", data),
};
