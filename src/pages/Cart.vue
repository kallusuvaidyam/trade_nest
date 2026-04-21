<template>
	<div class="cart-page">
		<div class="cart-container">
			<h1 class="cart-title">🛒 My Cart</h1>

			<!-- Empty -->
			<div v-if="cart.items.length === 0 && !orderSuccess" class="empty-cart">
				<div class="empty-icon">🛍️</div>
				<p>Your cart is empty</p>
				<RouterLink to="/items" class="browse-btn">Browse Products</RouterLink>
			</div>

			<div v-else-if="cart.items.length > 0" class="cart-layout">
				<!-- Items List -->
				<div class="cart-items">
					<div v-for="item in cart.items" :key="item.item_code" class="cart-item">
						<div class="ci-img-wrap">
							<img
								v-if="item.image"
								:src="item.image"
								:alt="item.item_name"
								class="ci-img"
							/>
							<div v-else class="ci-img-placeholder">
								{{ item.item_name.charAt(0) }}
							</div>
						</div>
						<div class="ci-info">
								<h3 class="ci-name">{{ item.item_name }}</h3>
							<p class="ci-uom">📦 {{ item.stock_uom }}</p>
							<div class="ci-price">
								<span v-if="item.price > 0"
									>₹{{ (item.price * item.qty).toLocaleString("en-IN") }}</span
								>
								<span v-else class="ci-price-na">Price not set</span>
							</div>
						</div>
						<div class="ci-actions">
							<div class="qty-control">
								<button @click="cart.decQty(item.item_code)" class="qty-btn">
									−
								</button>
								<span class="qty-val">{{ item.qty }}</span>
								<button @click="cart.incQty(item.item_code)" class="qty-btn">
									+
								</button>
							</div>
							<button @click="cart.removeItem(item.item_code)" class="remove-btn">
								🗑
							</button>
						</div>
					</div>
				</div>

				<!-- Summary + Payment -->
				<div class="cart-summary">
					<h2 class="summary-title">Order Summary</h2>
					<div class="summary-row">
						<span>Items ({{ cart.items.reduce((s,i) => s + i.qty, 0) }})</span>
						<span>{{
							cart.hasPrice ? "₹" + cart.total.toLocaleString("en-IN") : "—"
						}}</span>
					</div>
					<div class="summary-row">
						<span>Delivery</span>
						<span class="free-tag">Free</span>
					</div>
					<div class="summary-divider"></div>
					<div class="summary-row total">
						<span>Total</span>
						<span>{{
							cart.hasPrice ? "₹" + cart.total.toLocaleString("en-IN") : "Price TBD"
						}}</span>
					</div>

					<!-- Shipping Address -->
					<div class="shipping-section">
						<p class="payment-label">Shipping Address <span class="required-star">*</span></p>

						<!-- Saved addresses -->
						<div v-if="savedAddresses.length > 0" class="saved-addresses">
							<label
								v-for="addr in savedAddresses"
								:key="addr.name"
								:class="['addr-opt', selectedAddressName === addr.name ? 'active' : '']"
								@click="selectAddress(addr)"
							>
								<div class="addr-radio">
									<span :class="['addr-dot', selectedAddressName === addr.name ? 'checked' : '']"></span>
								</div>
								<div class="addr-body">
									<span class="addr-label">{{ addr.label }}</span>
									<span v-if="addr.is_default" class="addr-default-badge">Default</span>
									<p class="addr-text">{{ addr.address }}</p>
								</div>
								<button class="addr-delete" @click.stop="deleteAddress(addr.name)" title="Delete">✕</button>
							</label>
							<button class="addr-add-new" @click="showNewAddress = !showNewAddress">
								{{ showNewAddress ? '✕ Cancel' : '+ Add New Address' }}
							</button>
						</div>

						<!-- New address form -->
						<div v-if="savedAddresses.length === 0 || showNewAddress" class="new-addr-form">
							<input
								v-model="newAddrLabel"
								placeholder="Label (e.g. Home, Work)"
								class="addr-label-input"
							/>
							<textarea
								v-model="shippingAddress"
								placeholder="Enter your full delivery address..."
								:class="['address-input', addressError ? 'address-error' : '']"
								rows="3"
								@input="addressError = false"
							></textarea>
							<label class="save-addr-check">
								<input type="checkbox" v-model="saveNewAddress" />
								Save this address for future orders
							</label>
						</div>
					</div>

					<!-- Payment Method -->
					<div class="payment-section">
						<p class="payment-label">Payment Method</p>
						<div class="payment-options">
							<label :class="['pay-opt', paymentMethod === 'COD' ? 'active' : '']">
								<input type="radio" v-model="paymentMethod" value="COD" hidden />
								<span class="pay-icon">💵</span>
								<div>
									<div class="pay-title">Cash on Delivery</div>
									<div class="pay-sub">Pay cash on delivery</div>
								</div>
							</label>
							<label
								:class="['pay-opt', paymentMethod === 'Online' ? 'active' : '']"
							>
								<input
									type="radio"
									v-model="paymentMethod"
									value="Online"
									hidden
								/>
								<span class="pay-icon">💳</span>
								<div>
									<div class="pay-title">Online Payment</div>
									<div class="pay-sub">UPI / Card / Net Banking</div>
								</div>
							</label>
						</div>
					</div>

					<button class="place-order-btn" :disabled="placing" @click="handlePlaceOrder">
						<span v-if="placing" class="spinner"></span>
						<span v-else>⚡ Place Order</span>
					</button>
					<button class="clear-btn" @click="cart.clearCart">Clear Cart</button>
				</div>
			</div>
		</div>

		<!-- Success Modal -->
		<Teleport to="body">
			<div v-if="orderSuccess" class="success-overlay" @click.self="orderSuccess = null">
				<div class="success-box">
					<div class="success-icon-wrap">
						<svg width="52" height="52" viewBox="0 0 52 52" fill="none">
							<circle cx="26" cy="26" r="26" fill="#e8f8f0" />
							<path
								d="M14 26.5l8.5 8.5 16-17"
								stroke="#27ae60"
								stroke-width="3.5"
								stroke-linecap="round"
								stroke-linejoin="round"
							/>
						</svg>
					</div>
					<h2>Order Placed!</h2>
					<p class="so-name">{{ orderSuccess.order }}</p>
					<div class="so-items-list">
						<div v-for="item in orderSuccess.items" :key="item.item_code" class="so-item-row">
							<span class="so-item-name">{{ item.item_name }}</span>
							<span class="so-item-qty">× {{ item.qty }}</span>
							<span class="so-item-amt">₹{{ Number(item.amount).toLocaleString("en-IN") }}</span>
						</div>
					</div>
					<div class="so-meta">
						<span class="so-pm-badge">
							{{
								orderSuccess.payment_method === "COD"
									? "💵 Cash on Delivery"
									: "💳 Online Paid"
							}}
						</span>
						<span v-if="orderSuccess.grand_total > 0" class="so-total">
							₹{{ Number(orderSuccess.grand_total).toLocaleString("en-IN") }}
						</span>
					</div>
					<p class="so-note">
						{{
							orderSuccess.payment_method === "COD"
								? "Pay cash on delivery. Expected delivery within 7 days."
								: "Payment successful! Expected delivery within 7 days."
						}}
					</p>
					<div class="success-actions">
						<RouterLink
							to="/orders"
							class="view-orders-btn"
							@click="orderSuccess = null"
							>My Orders</RouterLink
						>
						<RouterLink to="/items" class="cont-btn" @click="orderSuccess = null"
							>Shop More</RouterLink
						>
					</div>
				</div>
			</div>
		</Teleport>

		<!-- Error Toast -->
		<Teleport to="body">
			<transition name="toast">
				<div v-if="errorMsg" class="error-toast">
					⚠️ {{ errorMsg }}
					<button @click="errorMsg = ''" class="et-close">✕</button>
				</div>
			</transition>
		</Teleport>
	</div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { RouterLink } from "vue-router";
import { useCartStore } from "@/stores/cart";
import { api } from "@/api/frappe";

const cart = useCartStore();
const placing = ref(false);
const orderSuccess = ref(null);
const errorMsg = ref("");
const paymentMethod = ref("COD");
const shippingAddress = ref("");
const addressError = ref(false);

// Address management
const savedAddresses = ref([]);
const selectedAddressName = ref(null);
const showNewAddress = ref(false);
const newAddrLabel = ref("Home");
const saveNewAddress = ref(true);

async function handlePlaceOrder() {
	if (paymentMethod.value === "Online") {
		await placeOnlineOrder();
	} else {
		await placeCODOrder();
	}
}

async function placeCODOrder() {
	if (!shippingAddress.value.trim()) {
		addressError.value = true;
		showError("Please enter your shipping address before placing the order.");
		return;
	}
	placing.value = true;
	errorMsg.value = "";
	try {
		await maybeSaveNewAddress();
		const res = await api.placeOrder(cart.items, "COD", shippingAddress.value);
		orderSuccess.value = res.message;
		cart.clearCart();
	} catch (e) {
		showError(e.message);
	} finally {
		placing.value = false;
	}
}

async function placeOnlineOrder() {
	if (!shippingAddress.value.trim()) {
		addressError.value = true;
		showError("Please enter your shipping address before placing the order.");
		return;
	}
	placing.value = true;
	errorMsg.value = "";
	try {
		await maybeSaveNewAddress();
		// Step 1: Place TN Order (payment_status = Pending)
		const orderRes = await api.placeOrder(cart.items, "Online", shippingAddress.value);
		const orderName = orderRes.message.order;

		// Step 2: Create Razorpay order
		const rzRes = await api.createRazorpayOrder(orderName);
		const rzData = rzRes.message;

		placing.value = false;

		// Step 3: Open Razorpay checkout
		openRazorpay(rzData, orderName);
	} catch (e) {
		placing.value = false;
		showError(e.message || "Online payment setup failed");
	}
}

function openRazorpay(rzData, orderName) {
	const options = {
		key: rzData.key_id,
		amount: rzData.amount,
		currency: rzData.currency,
		name: "Trade Nest",
		description: `Order ${orderName}`,
		order_id: rzData.razorpay_order_id,
		handler: async function (response) {
			placing.value = true;
			try {
				await api.verifyRazorpayPayment({
					razorpay_payment_id: response.razorpay_payment_id,
					razorpay_order_id: response.razorpay_order_id,
					razorpay_signature: response.razorpay_signature,
					order_name: orderName,
				});
				orderSuccess.value = {
					order: orderName,
					payment_method: "Online",
					grand_total: rzData.grand_total,
				};
				cart.clearCart();
			} catch (e) {
				showError("Payment verification failed: " + e.message);
			} finally {
				placing.value = false;
			}
		},
		prefill: {},
		theme: { color: "#5b4fcf" },
		modal: {
			ondismiss: () => {
				showError(
					"Payment cancelled. Order placed but payment pending — check My Orders.",
				);
			},
		},
	};

	const rzp = new window.Razorpay(options);
	rzp.open();
}

function showError(msg) {
	errorMsg.value = msg;
	setTimeout(() => (errorMsg.value = ""), 6000);
}

async function loadAddresses() {
	try {
		const res = await api.getMyAddresses();
		savedAddresses.value = res.message || [];
		const def = savedAddresses.value.find(a => a.is_default);
		if (def) selectAddress(def);
	} catch {}
}

function selectAddress(addr) {
	selectedAddressName.value = addr.name;
	shippingAddress.value = addr.address;
	showNewAddress.value = false;
	addressError.value = false;
}

async function deleteAddress(name) {
	try {
		await api.deleteAddress(name);
		savedAddresses.value = savedAddresses.value.filter(a => a.name !== name);
		if (selectedAddressName.value === name) {
			selectedAddressName.value = null;
			shippingAddress.value = "";
			const def = savedAddresses.value.find(a => a.is_default);
			if (def) selectAddress(def);
		}
	} catch (e) { showError(e.message); }
}

async function maybeSaveNewAddress() {
	if (saveNewAddress.value && shippingAddress.value.trim() && !selectedAddressName.value) {
		try {
			const res = await api.saveAddress({
				label: newAddrLabel.value || "Home",
				address: shippingAddress.value,
				set_default: savedAddresses.value.length === 0 ? 1 : 0,
			});
			savedAddresses.value.push(res.message);
		} catch {}
	}
}

// Load Razorpay script
onMounted(async () => {
	await loadAddresses();
	if (!document.getElementById("razorpay-script")) {
		const s = document.createElement("script");
		s.id = "razorpay-script";
		s.src = "https://checkout.razorpay.com/v1/checkout.js";
		document.head.appendChild(s);
	}
});
</script>

<style scoped>
.cart-page {
	min-height: 100vh;
	background: #f5f6fa;
	font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
	padding: 2rem 1.5rem 4rem;
}
.cart-container {
	max-width: 1000px;
	margin: 0 auto;
}
.cart-title {
	font-size: 1.5rem;
	font-weight: 800;
	color: #1a1a2e;
	margin: 0 0 1.5rem;
}

/* Empty */
.empty-cart {
	text-align: center;
	padding: 5rem 2rem;
	background: #fff;
	border-radius: 18px;
	box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}
.empty-icon {
	font-size: 3.5rem;
	margin-bottom: 1rem;
}
.empty-cart p {
	color: #888;
	font-size: 1rem;
	margin-bottom: 1.5rem;
}
.browse-btn {
	display: inline-block;
	background: linear-gradient(135deg, #5b4fcf, #764ba2);
	color: #fff;
	padding: 0.7rem 1.75rem;
	border-radius: 10px;
	text-decoration: none;
	font-weight: 600;
	font-size: 0.95rem;
}

/* Layout */
.cart-layout {
	display: grid;
	grid-template-columns: 1fr 320px;
	gap: 1.5rem;
	align-items: start;
}

/* Cart Items */
.cart-items {
	display: flex;
	flex-direction: column;
	gap: 1rem;
}
.cart-item {
	background: #fff;
	border-radius: 14px;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
	padding: 1rem;
	display: flex;
	align-items: center;
	gap: 1rem;
}
.ci-img-wrap {
	width: 80px;
	height: 80px;
	border-radius: 10px;
	overflow: hidden;
	flex-shrink: 0;
	background: #f0f1f6;
}
.ci-img {
	width: 100%;
	height: 100%;
	object-fit: cover;
}
.ci-img-placeholder {
	width: 100%;
	height: 100%;
	display: flex;
	align-items: center;
	justify-content: center;
	background: linear-gradient(135deg, #667eea, #764ba2);
	color: #fff;
	font-size: 1.8rem;
	font-weight: 800;
	text-transform: uppercase;
}
.ci-info {
	flex: 1;
	min-width: 0;
}
.ci-group {
	font-size: 0.7rem;
	font-weight: 600;
	color: #5b4fcf;
	text-transform: uppercase;
	background: #ede9ff;
	padding: 0.15rem 0.45rem;
	border-radius: 4px;
}
.ci-name {
	font-size: 0.95rem;
	font-weight: 700;
	color: #1a1a2e;
	margin: 0.35rem 0 0.2rem;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}
.ci-uom {
	font-size: 0.75rem;
	color: #999;
	margin: 0 0 0.35rem;
}
.ci-price {
	font-size: 1rem;
	font-weight: 700;
	color: #5b4fcf;
}
.ci-price-na {
	font-size: 0.8rem;
	color: #bbb;
	font-weight: 400;
}
.ci-actions {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 0.5rem;
	flex-shrink: 0;
}
.qty-control {
	display: flex;
	align-items: center;
	gap: 0.5rem;
	background: #f5f6fa;
	border-radius: 8px;
	padding: 0.25rem 0.5rem;
}
.qty-btn {
	background: none;
	border: none;
	font-size: 1.1rem;
	cursor: pointer;
	color: #5b4fcf;
	font-weight: 700;
	width: 24px;
	height: 24px;
	display: flex;
	align-items: center;
	justify-content: center;
	border-radius: 4px;
	transition: background 0.15s;
}
.qty-btn:hover {
	background: #ede9ff;
}
.qty-val {
	font-weight: 700;
	color: #1a1a2e;
	font-size: 0.95rem;
	min-width: 20px;
	text-align: center;
}
.remove-btn {
	background: none;
	border: none;
	font-size: 1.1rem;
	cursor: pointer;
	opacity: 0.5;
	transition: opacity 0.15s;
}
.remove-btn:hover {
	opacity: 1;
}

/* Summary */
.cart-summary {
	background: #fff;
	border-radius: 16px;
	box-shadow: 0 2px 12px rgba(0, 0, 0, 0.07);
	padding: 1.5rem;
	position: sticky;
	top: 80px;
}
.summary-title {
	font-size: 1rem;
	font-weight: 700;
	color: #1a1a2e;
	margin: 0 0 1rem;
}
.summary-row {
	display: flex;
	justify-content: space-between;
	font-size: 0.88rem;
	color: #555;
	margin-bottom: 0.6rem;
}
.summary-row.total {
	font-size: 1rem;
	font-weight: 700;
	color: #1a1a2e;
	margin-top: 0.4rem;
}
.free-tag {
	color: #27ae60;
	font-weight: 600;
}
.summary-divider {
	border: none;
	border-top: 1px solid #f0f0f0;
	margin: 0.75rem 0;
}

/* Shipping */
.shipping-section {
	margin-top: 1.25rem;
}
.address-input {
	width: 100%;
	box-sizing: border-box;
	border: 1.5px solid #e8eaed;
	border-radius: 10px;
	padding: 0.65rem 0.85rem;
	font-size: 0.85rem;
	color: #1a1a2e;
	resize: vertical;
	font-family: inherit;
	transition: border-color 0.15s;
}
.address-input:focus {
	outline: none;
	border-color: #5b4fcf;
}
.address-input.address-error {
	border-color: #e74c3c;
}
.required-star {
	color: #e74c3c;
}

/* Saved addresses */
.saved-addresses {
	display: flex;
	flex-direction: column;
	gap: 0.5rem;
	margin-bottom: 0.5rem;
}
.addr-opt {
	display: flex;
	align-items: flex-start;
	gap: 0.6rem;
	border: 1.5px solid #e8eaed;
	border-radius: 10px;
	padding: 0.65rem 0.75rem;
	cursor: pointer;
	transition: border-color 0.15s, background 0.15s;
}
.addr-opt.active {
	border-color: #5b4fcf;
	background: #f5f3ff;
}
.addr-radio { padding-top: 2px; flex-shrink: 0; }
.addr-dot {
	display: inline-block;
	width: 14px;
	height: 14px;
	border-radius: 50%;
	border: 2px solid #ccc;
	transition: border-color 0.15s;
}
.addr-dot.checked {
	border-color: #5b4fcf;
	background: #5b4fcf;
	box-shadow: inset 0 0 0 3px #fff;
}
.addr-body { flex: 1; min-width: 0; }
.addr-label {
	font-size: 0.8rem;
	font-weight: 700;
	color: #1a1a2e;
}
.addr-default-badge {
	font-size: 0.68rem;
	background: #5b4fcf;
	color: #fff;
	padding: 1px 6px;
	border-radius: 10px;
	margin-left: 5px;
	font-weight: 600;
}
.addr-text {
	font-size: 0.78rem;
	color: #666;
	margin: 2px 0 0;
	line-height: 1.4;
	white-space: pre-wrap;
}
.addr-delete {
	background: none;
	border: none;
	color: #ccc;
	cursor: pointer;
	font-size: 0.75rem;
	padding: 0;
	flex-shrink: 0;
	transition: color 0.15s;
}
.addr-delete:hover { color: #e74c3c; }
.addr-add-new {
	background: none;
	border: 1.5px dashed #ccc;
	border-radius: 10px;
	padding: 0.5rem;
	font-size: 0.82rem;
	color: #5b4fcf;
	cursor: pointer;
	font-weight: 600;
	transition: border-color 0.15s;
}
.addr-add-new:hover { border-color: #5b4fcf; }
.new-addr-form { display: flex; flex-direction: column; gap: 0.5rem; }
.addr-label-input {
	border: 1.5px solid #e8eaed;
	border-radius: 10px;
	padding: 0.55rem 0.85rem;
	font-size: 0.85rem;
	font-family: inherit;
	color: #1a1a2e;
	outline: none;
	transition: border-color 0.15s;
}
.addr-label-input:focus { border-color: #5b4fcf; }
.save-addr-check {
	display: flex;
	align-items: center;
	gap: 0.4rem;
	font-size: 0.78rem;
	color: #666;
	cursor: pointer;
}

/* Payment Options */
.payment-section {
	margin-top: 1.25rem;
}
.payment-label {
	font-size: 0.82rem;
	font-weight: 600;
	color: #888;
	text-transform: uppercase;
	letter-spacing: 0.05em;
	margin-bottom: 0.6rem;
}
.payment-options {
	display: flex;
	flex-direction: column;
	gap: 0.5rem;
}
.pay-opt {
	display: flex;
	align-items: center;
	gap: 0.75rem;
	border: 1.5px solid #e8eaed;
	border-radius: 10px;
	padding: 0.7rem 0.85rem;
	cursor: pointer;
	transition:
		border-color 0.15s,
		background 0.15s;
}
.pay-opt.active {
	border-color: #5b4fcf;
	background: #f5f3ff;
}
.pay-icon {
	font-size: 1.4rem;
	flex-shrink: 0;
}
.pay-title {
	font-size: 0.85rem;
	font-weight: 600;
	color: #1a1a2e;
}
.pay-sub {
	font-size: 0.73rem;
	color: #999;
	margin-top: 1px;
}

.place-order-btn {
	width: 100%;
	margin-top: 1.25rem;
	padding: 0.8rem;
	background: linear-gradient(135deg, #5b4fcf, #764ba2);
	color: #fff;
	border: none;
	border-radius: 12px;
	font-size: 0.95rem;
	font-weight: 700;
	cursor: pointer;
	transition: opacity 0.2s;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 0.5rem;
}
.place-order-btn:disabled {
	opacity: 0.65;
	cursor: not-allowed;
}
.place-order-btn:hover:not(:disabled) {
	opacity: 0.9;
}
.clear-btn {
	width: 100%;
	margin-top: 0.6rem;
	padding: 0.6rem;
	background: none;
	border: 1.5px solid #e0e0e0;
	border-radius: 10px;
	font-size: 0.85rem;
	color: #888;
	cursor: pointer;
	transition:
		border-color 0.15s,
		color 0.15s;
}
.clear-btn:hover {
	border-color: #e74c3c;
	color: #e74c3c;
}

/* Spinner */
.spinner {
	width: 18px;
	height: 18px;
	border: 2.5px solid rgba(255, 255, 255, 0.3);
	border-top-color: #fff;
	border-radius: 50%;
	animation: spin 0.7s linear infinite;
}
@keyframes spin {
	to {
		transform: rotate(360deg);
	}
}

/* Success Modal */
.success-overlay {
	position: fixed;
	inset: 0;
	background: rgba(10, 10, 20, 0.65);
	z-index: 9999;
	display: flex;
	align-items: center;
	justify-content: center;
}
.success-box {
	background: #fff;
	border-radius: 20px;
	padding: 2rem 2rem 1.75rem;
	max-width: 380px;
	width: 90%;
	text-align: center;
	animation: su-up 0.25s ease;
}
@keyframes su-up {
	from {
		transform: translateY(24px);
		opacity: 0;
	}
	to {
		transform: translateY(0);
		opacity: 1;
	}
}
.success-icon-wrap {
	margin-bottom: 1rem;
}
.success-box h2 {
	font-size: 1.15rem;
	font-weight: 800;
	color: #1a1a2e;
	margin: 0 0 0.5rem;
}
.so-name {
	font-size: 0.82rem;
	color: #5b4fcf;
	font-weight: 600;
	margin: 0 0 0.75rem;
	background: #f0edff;
	display: inline-block;
	padding: 0.2rem 0.7rem;
	border-radius: 6px;
}
.so-items-list {
	background: #f9f7ff;
	border-radius: 10px;
	padding: 0.6rem 0.85rem;
	margin: 0.5rem 0 0.75rem;
	text-align: left;
}
.so-item-row {
	display: flex;
	align-items: center;
	gap: 0.5rem;
	font-size: 0.82rem;
	padding: 0.25rem 0;
	border-bottom: 1px solid #ede9ff;
}
.so-item-row:last-child { border-bottom: none; }
.so-item-name { flex: 1; color: #333; font-weight: 500; }
.so-item-qty { color: #888; }
.so-item-amt { color: #5b4fcf; font-weight: 700; }
.so-meta {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 0.75rem;
	margin-bottom: 0.75rem;
	flex-wrap: wrap;
}
.so-pm-badge {
	font-size: 0.8rem;
	background: #f5f6fa;
	color: #555;
	padding: 0.25rem 0.6rem;
	border-radius: 6px;
	font-weight: 600;
}
.so-total {
	font-size: 1.2rem;
	font-weight: 800;
	color: #27ae60;
}
.so-note {
	font-size: 0.8rem;
	color: #888;
	line-height: 1.5;
	margin: 0 0 1.25rem;
}
.success-actions {
	display: flex;
	gap: 0.65rem;
}
.view-orders-btn,
.cont-btn {
	flex: 1;
	padding: 0.65rem 0.5rem;
	border-radius: 10px;
	text-decoration: none;
	font-size: 0.85rem;
	font-weight: 600;
	text-align: center;
	transition: opacity 0.15s;
}
.view-orders-btn {
	background: linear-gradient(135deg, #5b4fcf, #764ba2);
	color: #fff;
}
.view-orders-btn:hover {
	opacity: 0.88;
}
.cont-btn {
	border: 1.5px solid #e0e0e0;
	color: #555;
	background: #fff;
}
.cont-btn:hover {
	border-color: #5b4fcf;
	color: #5b4fcf;
}

/* Error Toast */
.error-toast {
	position: fixed;
	bottom: 1.5rem;
	right: 1.5rem;
	background: #e74c3c;
	color: #fff;
	border-radius: 12px;
	padding: 0.85rem 1.1rem;
	display: flex;
	align-items: center;
	gap: 0.75rem;
	font-size: 0.88rem;
	font-weight: 500;
	box-shadow: 0 8px 24px rgba(231, 76, 60, 0.3);
	z-index: 99999;
	max-width: 400px;
}
.et-close {
	background: none;
	border: none;
	color: rgba(255, 255, 255, 0.7);
	cursor: pointer;
	font-size: 1rem;
	margin-left: auto;
}
.toast-enter-active {
	animation: toast-in 0.3s ease;
}
.toast-leave-active {
	animation: toast-in 0.25s ease reverse;
}
@keyframes toast-in {
	from {
		opacity: 0;
		transform: translateY(16px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}

@media (max-width: 700px) {
	.cart-layout {
		grid-template-columns: 1fr;
	}
	.cart-summary {
		position: static;
	}
}
</style>
