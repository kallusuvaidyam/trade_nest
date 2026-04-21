<template>
	<div class="vr-page">
		<div class="vr-card">
			<div class="vr-header">
				<div class="vr-icon">🏪</div>
				<h1 class="vr-title">Become a Vendor</h1>
				<p class="vr-sub">Open your store on Trade Nest and sell products.</p>
			</div>

			<div v-if="success" class="vr-success">
				<div class="success-icon">✓</div>
				<h2>Application Submitted!</h2>
				<p>Our team will review your application within 24-48 hours. You will receive an email upon approval.</p>
				<RouterLink to="/items" class="vr-shop-link">Go to Shop</RouterLink>
			</div>

			<form v-else @submit.prevent="submit" class="vr-form">
				<div class="form-group">
					<label>Vendor / Business Name *</label>
					<input
						v-model="form.vendor_name"
						type="text"
						required
						placeholder="e.g. Rahul Enterprises"
						class="form-input"
					/>
				</div>

				<div class="form-group">
					<label>Store Name *</label>
					<input
						v-model="form.store_name"
						type="text"
						required
						placeholder="e.g. Rahul Electronics"
						class="form-input"
					/>
				</div>

				<div class="form-group">
					<label>Phone Number *</label>
					<input
						v-model="form.phone"
						type="tel"
						required
						placeholder="+91 98765 43210"
						class="form-input"
					/>
				</div>

				<div class="form-group">
					<label>GST Number (Optional)</label>
					<input
						v-model="form.gst_number"
						type="text"
						placeholder="22AAAAA0000A1Z5"
						class="form-input"
					/>
				</div>

				<div class="form-group">
					<label>Business Address</label>
					<textarea
						v-model="form.address"
						placeholder="Full business address..."
						class="form-textarea"
						rows="3"
					></textarea>
				</div>

				<p v-if="errorMsg" class="vr-error">⚠️ {{ errorMsg }}</p>

				<button type="submit" class="vr-submit" :disabled="loading">
					<span v-if="loading" class="spinner"></span>
					<span v-else>Submit Application</span>
				</button>
			</form>
		</div>
	</div>
</template>

<script setup>
import { ref } from "vue";
import { RouterLink } from "vue-router";
import { api } from "@/api/frappe";

const form = ref({ vendor_name: "", store_name: "", phone: "", gst_number: "", address: "" });
const loading = ref(false);
const success = ref(false);
const errorMsg = ref("");

async function submit() {
	loading.value = true;
	errorMsg.value = "";
	try {
		await api.registerAsVendor(form.value);
		success.value = true;
	} catch (e) {
		errorMsg.value = e.message || "Registration failed. Please try again.";
	} finally {
		loading.value = false;
	}
}
</script>

<style scoped>
.vr-page {
	min-height: 100vh;
	background: #f5f6fa;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 2rem 1.5rem;
	font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.vr-card {
	background: #fff;
	border-radius: 20px;
	box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
	padding: 2.5rem 2rem;
	width: 100%;
	max-width: 480px;
}
.vr-header {
	text-align: center;
	margin-bottom: 2rem;
}
.vr-icon {
	font-size: 3rem;
	margin-bottom: 0.75rem;
}
.vr-title {
	font-size: 1.6rem;
	font-weight: 800;
	color: #1a1a2e;
	margin: 0 0 0.5rem;
}
.vr-sub {
	font-size: 0.88rem;
	color: #888;
}

.vr-success {
	text-align: center;
	padding: 1rem 0;
}
.success-icon {
	width: 56px;
	height: 56px;
	border-radius: 50%;
	background: #e8f8f0;
	color: #27ae60;
	font-size: 1.5rem;
	display: flex;
	align-items: center;
	justify-content: center;
	margin: 0 auto 1rem;
	font-weight: 700;
}
.vr-success h2 {
	font-size: 1.1rem;
	font-weight: 800;
	color: #1a1a2e;
	margin: 0 0 0.5rem;
}
.vr-success p {
	font-size: 0.88rem;
	color: #888;
	margin-bottom: 1.5rem;
}
.vr-shop-link {
	display: inline-block;
	padding: 0.7rem 1.75rem;
	background: linear-gradient(135deg, #5b4fcf, #764ba2);
	color: #fff;
	border-radius: 12px;
	text-decoration: none;
	font-weight: 600;
}

.form-group {
	margin-bottom: 1.1rem;
}
.form-group label {
	display: block;
	font-size: 0.82rem;
	font-weight: 600;
	color: #444;
	margin-bottom: 0.4rem;
}
.form-input,
.form-textarea {
	width: 100%;
	box-sizing: border-box;
	border: 1.5px solid #e8eaed;
	border-radius: 10px;
	padding: 0.7rem 0.9rem;
	font-size: 0.9rem;
	font-family: inherit;
	color: #1a1a2e;
	transition: border-color 0.15s;
}
.form-input:focus,
.form-textarea:focus {
	outline: none;
	border-color: #5b4fcf;
}
.form-textarea {
	resize: vertical;
}

.vr-error {
	background: #fff0f0;
	color: #e74c3c;
	border-radius: 8px;
	padding: 0.6rem 0.9rem;
	font-size: 0.85rem;
	margin-bottom: 1rem;
}
.vr-submit {
	width: 100%;
	padding: 0.85rem;
	background: linear-gradient(135deg, #5b4fcf, #764ba2);
	color: #fff;
	border: none;
	border-radius: 12px;
	font-size: 0.95rem;
	font-weight: 700;
	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 0.5rem;
	transition: opacity 0.2s;
}
.vr-submit:disabled {
	opacity: 0.6;
	cursor: not-allowed;
}
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
</style>
