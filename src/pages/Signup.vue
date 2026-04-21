<template>
	<div class="auth-page">
		<div class="auth-card" :class="{ 'auth-card-vendor': isVendor }">
			<div class="auth-logo">
				<div class="logo-icon">T</div>
				<span class="logo-text">Trade<span class="logo-accent">Nest</span></span>
			</div>

			<h1 class="auth-title">Create Account</h1>
			<p class="auth-sub">Create a new account on Trade Nest</p>

			<form @submit.prevent="handleSignup" class="auth-form">
				<div class="field-group">
					<label>Register As</label>
					<div class="account-type-grid">
						<button
							type="button"
							class="account-type-card"
							:class="{ active: accountType === 'Customer' }"
							@click="setAccountType('Customer')"
						>
							<span class="account-type-title">Customer</span>
							<span class="account-type-sub">Shop and place orders</span>
						</button>
						<button
							type="button"
							class="account-type-card"
							:class="{ active: accountType === 'Vendor' }"
							@click="setAccountType('Vendor')"
						>
							<span class="account-type-title">Vendor</span>
							<span class="account-type-sub">Open store and sell</span>
						</button>
					</div>
				</div>

				<template v-if="isVendor">
					<details class="form-section" open>
						<summary class="section-summary">
							<div>
								<div class="section-title">Account Details</div>
								<div class="section-subtitle">
									Basic profile and login information.
								</div>
							</div>
						</summary>
						<div class="section-body">
							<div class="field-grid">
								<div class="field-group">
									<label>Full Name</label>
									<input
										v-model="fullName"
										type="text"
										placeholder="Your full name"
										required
										:disabled="loading"
									/>
								</div>

								<div class="field-group">
									<label>Email</label>
									<input
										v-model="email"
										type="email"
										placeholder="email@example.com"
										required
										:disabled="loading"
									/>
								</div>

								<div class="field-group">
									<label>Password</label>
									<div class="password-wrap">
										<input
											v-model="password"
											:type="showPwd ? 'text' : 'password'"
											placeholder="Min. 8 characters"
											required
											minlength="8"
											:disabled="loading"
											autocomplete="new-password"
										/>
										<button
											type="button"
											class="toggle-pwd"
											@click="showPwd = !showPwd"
											tabindex="-1"
										>
											{{ showPwd ? "Hide" : "Show" }}
										</button>
									</div>
								</div>

								<div class="field-group">
									<label>Phone Number</label>
									<div class="input-with-prefix">
										<span class="prefix-tag">+91</span>
										<input
											v-model="phone"
											type="tel"
											inputmode="numeric"
											maxlength="10"
											pattern="[0-9]{10}"
											placeholder="9876543210"
											required
											:disabled="loading"
											@input="normalizePhoneInput"
										/>
									</div>
								</div>
							</div>
						</div>
					</details>

					<details class="form-section">
						<summary class="section-summary">
							<div>
								<div class="section-title">Verification</div>
								<div class="section-subtitle">
									Contact and KYC details for review.
								</div>
							</div>
						</summary>
						<div class="section-body">
							<div class="field-grid">
								<div class="field-group">
									<label>GST Number</label>
									<input
										v-model="gstNumber"
										type="text"
										placeholder="22AAAAA0000A1Z5"
										:disabled="loading"
										@input="normalizeGstInput"
									/>
								</div>

								<div class="field-group field-span-2">
									<label>Business Address</label>
									<textarea
										v-model="address"
										placeholder="Full business address..."
										rows="3"
										:disabled="loading"
									></textarea>
								</div>
							</div>
						</div>
					</details>

					<details class="form-section">
						<summary class="section-summary">
							<div>
								<div class="section-title">Business Details</div>
								<div class="section-subtitle">
									Store information shown during vendor review.
								</div>
							</div>
						</summary>
						<div class="section-body">
							<div class="field-grid">
								<div class="field-group">
									<label>Vendor / Business Name</label>
									<input
										v-model="vendorName"
										type="text"
										placeholder="e.g. Rahul Enterprises"
										required
										:disabled="loading"
									/>
								</div>

								<div class="field-group">
									<label>Store Name</label>
									<input
										v-model="storeName"
										type="text"
										placeholder="e.g. Rahul Electronics"
										required
										:disabled="loading"
									/>
								</div>

								<div class="field-group field-span-2">
									<label>Store Description</label>
									<textarea
										v-model="storeDescription"
										placeholder="Tell us what you sell and what makes your store special."
										rows="4"
										:disabled="loading"
									></textarea>
								</div>
								<div class="file-upload">
									<label class="upload-box">
										<input
											type="file"
											accept="image/*"
											multiple
											@change="handleFiles"
											:disabled="loading"
											hidden
										/>

										<div class="upload-content">
											<span v-if="storeImages.length === 0"
												>📁 Upload 3 images</span
											>
											<span v-else
												>✅ {{ storeImages.length }}/3 images
												selected</span
											>
										</div>
									</label>
								</div>
								<div class="preview-grid" v-if="previewUrls.length">
									<div
										v-for="(img, i) in previewUrls"
										:key="i"
										class="preview-item"
									>
										<img :src="img" />
										<button @click="removeImage(i)">✖</button>
									</div>
								</div>
							</div>
						</div>
					</details>

					<details class="form-section">
						<summary class="section-summary">
							<div>
								<div class="section-title">Payout Details</div>
								<div class="section-subtitle">
									Optional bank details to speed up onboarding.
								</div>
							</div>
						</summary>
						<div class="section-body">
							<div class="field-grid">
								<div class="field-group">
									<label>Account Holder Name</label>
									<input
										v-model="bankAccountName"
										type="text"
										placeholder="Name as per bank account"
										:disabled="loading"
									/>
								</div>

								<div class="field-group">
									<label>Bank Name</label>
									<input
										v-model="bankName"
										type="text"
										placeholder="e.g. State Bank of India"
										:disabled="loading"
									/>
								</div>

								<div class="field-group">
									<label>Account Number</label>
									<input
										v-model="bankAccountNumber"
										type="text"
										inputmode="numeric"
										placeholder="Bank account number"
										:disabled="loading"
										@input="normalizeBankAccountInput"
									/>
								</div>

								<div class="field-group">
									<label>IFSC Code</label>
									<input
										v-model="ifscCode"
										type="text"
										placeholder="SBIN0001234"
										:disabled="loading"
										@input="normalizeIfscInput"
									/>
								</div>
							</div>
						</div>
					</details>
				</template>

				<template v-else>
					<div class="field-group">
						<label>Full Name</label>
						<input
							v-model="fullName"
							type="text"
							placeholder="Your full name"
							required
							:disabled="loading"
						/>
					</div>

					<div class="field-group">
						<label>Email</label>
						<input
							v-model="email"
							type="email"
							placeholder="email@example.com"
							required
							:disabled="loading"
						/>
					</div>

					<div class="field-group">
						<label>Password</label>
						<div class="password-wrap">
							<input
								v-model="password"
								:type="showPwd ? 'text' : 'password'"
								placeholder="Min. 8 characters"
								required
								minlength="8"
								:disabled="loading"
								autocomplete="new-password"
							/>
							<button
								type="button"
								class="toggle-pwd"
								@click="showPwd = !showPwd"
								tabindex="-1"
							>
								{{ showPwd ? "Hide" : "Show" }}
							</button>
						</div>
					</div>
				</template>

				<div v-if="error" class="auth-error">⚠️ {{ error }}</div>
				<div v-if="success" class="auth-success">✅ {{ success }}</div>

				<button type="submit" class="auth-btn" :disabled="loading || !!success">
					<span v-if="loading" class="spinner"></span>
					<span v-else>Create Account</span>
				</button>
			</form>

			<p class="auth-footer">
				Already have an account?
				<RouterLink to="/login">Login</RouterLink>
			</p>
		</div>
	</div>
</template>

<script setup>
import { computed, ref } from "vue";
import { RouterLink, useRouter } from "vue-router";
import { api } from "@/api/frappe";

const router = useRouter();
const accountType = ref("Customer");
const isVendor = computed(() => accountType.value === "Vendor");
const fullName = ref("");
const email = ref("");
const password = ref("");
const vendorName = ref("");
const storeName = ref("");
const phone = ref("");
const gstNumber = ref("");
const address = ref("");
const storeDescription = ref("");
const bankAccountName = ref("");
const bankName = ref("");
const bankAccountNumber = ref("");
const ifscCode = ref("");
const showPwd = ref(false);
const loading = ref(false);
const error = ref("");
const success = ref("");
const storeImages = ref([]);
const previewUrls = ref([]);

function handleFiles(e) {
	const files = Array.from(e.target.files);

	if (files.length + storeImages.value.length > 3) {
		error.value = "Only 3 images allowed";
		return;
	}

	files.forEach((file) => {
		if (!file.type.startsWith("image/")) {
			error.value = "Only images allowed";
			return;
		}

		storeImages.value.push(file);
		previewUrls.value.push(URL.createObjectURL(file));
	});
}

function removeImage(index) {
	storeImages.value.splice(index, 1);
	previewUrls.value.splice(index, 1);
}

function setAccountType(type) {
	accountType.value = type;
}

function normalizePhoneInput() {
	phone.value = phone.value.replace(/\D/g, "").slice(0, 10);
}

function normalizeGstInput() {
	gstNumber.value = gstNumber.value.toUpperCase().replace(/\s+/g, "");
}

function normalizeBankAccountInput() {
	bankAccountNumber.value = bankAccountNumber.value.replace(/\s+/g, "");
}

function normalizeIfscInput() {
	ifscCode.value = ifscCode.value.toUpperCase().replace(/\s+/g, "");
}

function resetForm() {
	accountType.value = "Customer";
	fullName.value = "";
	email.value = "";
	password.value = "";
	vendorName.value = "";
	storeName.value = "";
	phone.value = "";
	gstNumber.value = "";
	address.value = "";
	storeDescription.value = "";
	bankAccountName.value = "";
	bankName.value = "";
	bankAccountNumber.value = "";
	ifscCode.value = "";
}

async function handleSignup() {
	loading.value = true;
	error.value = "";
	success.value = "";

	try {
		if (isVendor.value && storeImages.value.length !== 3) {
			error.value = "Please upload exactly 3 images";
			loading.value = false;
			return;
		}
		const formData = new FormData();

		formData.append("email", email.value);
		formData.append("full_name", fullName.value);
		formData.append("password", password.value);
		formData.append("account_type", accountType.value);
		formData.append("vendor_name", vendorName.value);
		formData.append("store_name", storeName.value);
		formData.append("phone", phone.value);
		formData.append("gst_number", gstNumber.value);
		formData.append("address", address.value);
		formData.append("store_description", storeDescription.value);
		formData.append("bank_account_name", bankAccountName.value);
		formData.append("bank_name", bankName.value);
		formData.append("bank_account_number", bankAccountNumber.value);
		formData.append("ifsc_code", ifscCode.value);

		// ✅ Add image file
		storeImages.value.forEach((file, i) => {
			formData.append(`store_images`, file);
		});

		// ✅ Send FormData instead of JSON
		const res = await api.signup(formData);

		success.value = res.message?.message || "Account created successfully. Please log in.";

		resetForm();
		setTimeout(() => router.push("/login"), 1000);
	} catch (e) {
		error.value = e.message || "Network error. Please try again.";
	} finally {
		loading.value = false;
	}
}
</script>

<style scoped>
.file-upload {
	width: 100%;
}

.upload-box {
	display: block;
	border: 1px dashed #d0c9ff;
	border-radius: 14px;
	padding: 1.4rem;
	text-align: center;
	cursor: pointer;
	background: #faf9ff;
	transition: all 0.25s ease;
}

.upload-box:hover {
	border-color: #5b4fcf;
	background: #f4f1ff;
}

.upload-content {
	font-size: 0.95rem;
	color: #5b4fcf;
	font-weight: 600;
}

/* 🔥 NEW: Grid preview */
.preview-grid {
	display: flex;
	gap: 12px;
	margin-top: 12px;
}

/* Each image box */
.preview-item {
	position: relative;
}

/* Image style */
.preview-item img {
	width: 90px;
	height: 90px;
	object-fit: cover;
	border-radius: 12px;
	border: 2px solid #eee;
	transition: transform 0.2s ease;
}

.preview-item img:hover {
	transform: scale(1.05);
}

/* ❌ Remove button */
.preview-item button {
	position: absolute;
	top: -6px;
	right: -6px;
	background: #ff4d4f;
	color: #fff;
	border: none;
	border-radius: 50%;
	font-size: 12px;
	width: 20px;
	height: 20px;
	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: center;
}

/* Mobile responsive */
@media (max-width: 640px) {
	.preview-item img {
		width: 70px;
		height: 70px;
	}
}

.auth-page {
	min-height: 100vh;
	background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 2rem 1rem;
	font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.auth-card {
	background: #fff;
	border-radius: 20px;
	padding: 2.5rem 2rem;
	width: 100%;
	max-width: 400px;
	box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.auth-card-vendor {
	max-width: 760px;
}

.auth-logo {
	display: flex;
	align-items: center;
	gap: 0.5rem;
	margin-bottom: 1.75rem;
}

.logo-icon {
	width: 36px;
	height: 36px;
	background: linear-gradient(135deg, #5b4fcf, #764ba2);
	color: #fff;
	font-weight: 800;
	font-size: 1.1rem;
	border-radius: 10px;
	display: flex;
	align-items: center;
	justify-content: center;
}

.logo-text {
	font-size: 1.2rem;
	font-weight: 700;
	color: #1a1a2e;
}

.logo-accent {
	color: #5b4fcf;
}

.auth-title {
	font-size: 1.5rem;
	font-weight: 800;
	color: #1a1a2e;
	margin: 0 0 0.3rem;
}

.auth-sub {
	font-size: 0.875rem;
	color: #888;
	margin: 0 0 1.75rem;
}

.auth-form {
	display: flex;
	flex-direction: column;
	gap: 1rem;
}

.form-section {
	border: 1px solid #ece8ff;
	border-radius: 16px;
	background: linear-gradient(180deg, #fcfbff 0%, #f7f4ff 100%);
	overflow: hidden;
}

.form-section[open] {
	box-shadow: 0 10px 24px rgba(91, 79, 207, 0.08);
}

.section-summary {
	list-style: none;
	cursor: pointer;
	padding: 1rem 1.1rem;
	display: flex;
	align-items: center;
	justify-content: space-between;
}

.section-summary::-webkit-details-marker {
	display: none;
}

.section-summary::after {
	content: "+";
	font-size: 1.35rem;
	font-weight: 500;
	color: #5b4fcf;
}

.form-section[open] .section-summary::after {
	content: "−";
}

.section-title {
	font-size: 0.98rem;
	font-weight: 700;
	color: #1a1a2e;
}

.section-subtitle {
	font-size: 0.8rem;
	color: #787196;
	margin-top: 0.15rem;
}

.section-body {
	padding: 0 1.1rem 1.1rem;
}

.field-grid {
	display: grid;
	grid-template-columns: repeat(2, minmax(0, 1fr));
	gap: 1rem;
}

.field-span-2 {
	grid-column: span 2;
}

.account-type-grid {
	display: grid;
	grid-template-columns: repeat(2, minmax(0, 1fr));
	gap: 0.75rem;
}

.account-type-card {
	display: flex;
	flex-direction: column;
	align-items: flex-start;
	gap: 0.2rem;
	border: 1.5px solid #e0e0e0;
	border-radius: 12px;
	background: #fff;
	padding: 0.9rem;
	cursor: pointer;
	text-align: left;
	transition: all 0.15s ease;
}

.account-type-card:hover {
	border-color: #8a7ce6;
	background: #f8f6ff;
}

.account-type-card.active {
	border-color: #5b4fcf;
	background: linear-gradient(180deg, #f5f2ff 0%, #efeaff 100%);
	box-shadow: 0 8px 20px rgba(91, 79, 207, 0.12);
}

.account-type-title {
	font-size: 0.92rem;
	font-weight: 700;
	color: #1a1a2e;
}

.account-type-sub {
	font-size: 0.78rem;
	color: #777;
}

.field-group {
	display: flex;
	flex-direction: column;
	gap: 0.35rem;
}

.field-group label {
	font-size: 0.82rem;
	font-weight: 600;
	color: #555;
}

.field-group input,
.field-group textarea {
	padding: 0.75rem 0.9rem;
	border: 1.5px solid #e0e0e0;
	border-radius: 10px;
	font-size: 0.9rem;
	color: #1a1a2e;
	outline: none;
	transition: border-color 0.15s;
	width: 100%;
	box-sizing: border-box;
	font-family: inherit;
}

.field-group input:focus,
.field-group textarea:focus {
	border-color: #5b4fcf;
}

.field-group input:disabled,
.field-group textarea:disabled {
	background: #f9f9f9;
}

.field-group textarea {
	resize: vertical;
}

.input-with-prefix {
	display: flex;
	align-items: center;
	border: 1.5px solid #e0e0e0;
	border-radius: 10px;
	background: #fff;
	overflow: hidden;
}

.input-with-prefix:focus-within {
	border-color: #5b4fcf;
}

.prefix-tag {
	padding: 0 0.85rem;
	background: #f4f1ff;
	color: #5b4fcf;
	font-size: 0.9rem;
	font-weight: 700;
	border-right: 1px solid #e6defe;
	align-self: stretch;
	display: flex;
	align-items: center;
}

.input-with-prefix input {
	border: 0;
	border-radius: 0;
}

.input-with-prefix input:focus {
	border-color: transparent;
}

.password-wrap {
	position: relative;
}

.password-wrap input {
	padding-right: 4rem;
}

.toggle-pwd {
	position: absolute;
	right: 0.9rem;
	top: 50%;
	transform: translateY(-50%);
	background: none;
	border: none;
	color: #5b4fcf;
	font-size: 0.8rem;
	font-weight: 600;
	cursor: pointer;
	padding: 0;
}

.auth-error {
	background: #fff0f0;
	color: #e74c3c;
	padding: 0.65rem 0.9rem;
	border-radius: 10px;
	font-size: 0.85rem;
	font-weight: 500;
}

.auth-success {
	background: #e8f8f0;
	color: #27ae60;
	padding: 0.65rem 0.9rem;
	border-radius: 10px;
	font-size: 0.85rem;
	font-weight: 500;
}

.auth-btn {
	margin-top: 0.5rem;
	padding: 0.75rem;
	background: linear-gradient(135deg, #5b4fcf, #764ba2);
	color: #fff;
	border: none;
	border-radius: 10px;
	font-size: 0.95rem;
	font-weight: 700;
	cursor: pointer;
	transition: opacity 0.2s;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 0.5rem;
	min-height: 44px;
}

.auth-btn:disabled {
	opacity: 0.6;
	cursor: not-allowed;
}

.spinner {
	width: 18px;
	height: 18px;
	border: 2px solid rgba(255, 255, 255, 0.4);
	border-top-color: #fff;
	border-radius: 50%;
	animation: spin 0.7s linear infinite;
}

@keyframes spin {
	to {
		transform: rotate(360deg);
	}
}

.auth-footer {
	text-align: center;
	margin-top: 1.5rem;
	font-size: 0.85rem;
	color: #888;
}

.auth-footer a {
	color: #5b4fcf;
	font-weight: 600;
	text-decoration: none;
}

.auth-footer a:hover {
	text-decoration: underline;
}

@media (max-width: 640px) {
	.auth-card {
		padding: 2rem 1.25rem;
	}

	.account-type-grid,
	.field-grid {
		grid-template-columns: 1fr;
	}

	.field-span-2 {
		grid-column: auto;
	}

	.section-body {
		padding: 0 0.95rem 0.95rem;
	}
}
</style>
