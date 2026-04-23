<template>
	<div class="auth-page">
		<div class="auth-card" :class="{ 'auth-card-vendor': isVendor }">
			<div class="auth-logo">
				<div class="logo-icon">T</div>
				<span class="logo-text">Trade<span class="logo-accent">Nest</span></span>
			</div>

			<h1 class="auth-title">Create Account</h1>
			<p class="auth-sub">Create a new account on Trade Nest</p>
			<p v-if="formStarted" class="register-as-tag">
				Register As <strong>{{ accountType }}</strong>
			</p>

			<!-- Account Type Selector -->
			<div class="field-group" style="margin-bottom: 1.25rem" v-if="!formStarted">
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

			<!-- ═══════════════ CUSTOMER FLOW ═══════════════ -->
			<template v-if="!isVendor">
				<!-- Step 1: Info -->
				<template v-if="customerStep === 1">
					<form @submit.prevent="customerSendOtp" class="auth-form">
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
						<div v-if="error" class="auth-error">⚠️ {{ error }}</div>
						<button type="submit" class="auth-btn" :disabled="loading">
							<span v-if="loading" class="spinner"></span>
							<span v-else>Send OTP →</span>
						</button>
					</form>
				</template>

				<!-- Step 2: OTP -->
				<template v-if="customerStep === 2">
					<form @submit.prevent="customerVerifyOtp" class="auth-form">
						<div class="otp-hint">
							OTP sent to <b>{{ email }}</b>
						</div>
						<div class="field-group">
							<label>Enter 6-digit OTP</label>
							<div class="otp-inputs">
								<input
									v-for="(_, i) in 6"
									:key="i"
									:ref="(el) => (otpRefs[i] = el)"
									v-model="otpDigits[i]"
									type="text"
									inputmode="numeric"
									maxlength="1"
									class="otp-box"
									@input="onOtpInput(i)"
									@keydown.backspace="onOtpBackspace(i)"
									:disabled="loading"
								/>
							</div>
						</div>
						<div class="otp-resend">
							<span v-if="resendCooldown > 0">Resend in {{ resendCooldown }}s</span>
							<button
								v-else
								type="button"
								class="resend-btn"
								@click="customerSendOtp"
							>
								Resend OTP
							</button>
						</div>
						<div v-if="error" class="auth-error">⚠️ {{ error }}</div>
						<button
							type="submit"
							class="auth-btn"
							:disabled="loading || otpDigits.join('').length < 6"
						>
							<span v-if="loading" class="spinner"></span>
							<span v-else>Verify OTP →</span>
						</button>
						<button type="button" class="back-btn" @click="customerStep = 1">
							← Back
						</button>
					</form>
				</template>

				<!-- Step 3: Set Password -->
				<template v-if="customerStep === 3">
					<form @submit.prevent="handleCustomerSignup" class="auth-form">
						<div class="step-success-hint">
							✅ Email verified! Now set your password.
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
						<div v-if="error" class="auth-error">⚠️ {{ error }}</div>
						<div v-if="success" class="auth-success">✅ {{ success }}</div>
						<button type="submit" class="auth-btn" :disabled="loading || !!success">
							<span v-if="loading" class="spinner"></span>
							<span v-else>Create Account</span>
						</button>
					</form>
				</template>
			</template>

			<!-- ═══════════════ VENDOR FLOW ═══════════════ -->
			<template v-else>
				<!-- Vendor Step Indicator -->
				<div class="vendor-steps">
					<div
						v-for="s in vendorSteps"
						:key="s.step"
						class="vstep"
						:class="{ active: vendorStep === s.step, done: vendorStep > s.step }"
					>
						<div class="vstep-dot">
							<span v-if="vendorStep > s.step">✓</span>
							<span v-else>{{ s.step }}</span>
						</div>
						<span class="vstep-label">{{ s.label }}</span>
					</div>
					<div class="vstep-line"></div>
				</div>

				<!-- Vendor Step 1: Account Details -->
				<template v-if="vendorStep === 1">
					<form @submit.prevent="vendorNext(1)" class="auth-form">
						<div class="section-heading">Account Details</div>
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
						<div v-if="error" class="auth-error">⚠️ {{ error }}</div>
						<button type="submit" class="auth-btn" :disabled="loading">
							<span v-if="loading" class="spinner"></span>
							<span v-else>Next: Verification →</span>
						</button>
					</form>
				</template>

				<!-- Vendor Step 2: OTP Verification -->
				<template v-if="vendorStep === 2">
					<form @submit.prevent="vendorVerifyOtp" class="auth-form">
						<div class="section-heading">Email Verification</div>
						<div class="otp-hint">
							OTP sent to <b>{{ email }}</b>
						</div>
						<div class="field-group">
							<label>Enter 6-digit OTP</label>
							<div class="otp-inputs">
								<input
									v-for="(_, i) in 6"
									:key="i"
									:ref="(el) => (otpRefs[i] = el)"
									v-model="otpDigits[i]"
									type="text"
									inputmode="numeric"
									maxlength="1"
									class="otp-box"
									@input="onOtpInput(i)"
									@keydown.backspace="onOtpBackspace(i)"
									:disabled="loading"
								/>
							</div>
						</div>
						<div class="otp-resend">
							<span v-if="resendCooldown > 0">Resend in {{ resendCooldown }}s</span>
							<button v-else type="button" class="resend-btn" @click="vendorSendOtp">
								Resend OTP
							</button>
						</div>
						<div v-if="error" class="auth-error">⚠️ {{ error }}</div>
						<button
							type="submit"
							class="auth-btn"
							:disabled="loading || otpDigits.join('').length < 6"
						>
							<span v-if="loading" class="spinner"></span>
							<span v-else>Verify & Continue →</span>
						</button>
						<button type="button" class="back-btn" @click="vendorStep = 1">
							← Back
						</button>
					</form>
				</template>

				<!-- Vendor Step 3: Business Details -->
				<template v-if="vendorStep === 3">
					<form @submit.prevent="vendorNext(3)" class="auth-form">
						<div class="section-heading">Business Details</div>
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
							<div class="field-group field-span-2">
								<label>Store Description</label>
								<textarea
									v-model="storeDescription"
									placeholder="Tell us what you sell and what makes your store special."
									rows="3"
									:disabled="loading"
								></textarea>
							</div>
							<div class="field-group field-span-2">
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
										<button type="button" @click="removeImage(i)">✖</button>
									</div>
								</div>
							</div>
						</div>
						<div v-if="error" class="auth-error">⚠️ {{ error }}</div>
						<button type="submit" class="auth-btn" :disabled="loading">
							<span v-if="loading" class="spinner"></span>
							<span v-else>Next: Payout Details →</span>
						</button>
						<button type="button" class="back-btn" @click="vendorStep = 2">
							← Back
						</button>
					</form>
				</template>

				<!-- Vendor Step 4: Payout + Password -->
				<template v-if="vendorStep === 4">
					<form @submit.prevent="handleVendorSignup" class="auth-form">
						<div class="section-heading">Payout &amp; Password</div>
						<div class="field-grid">
							<div class="field-group field-span-2">
								<label>IFSC Code</label>
								<div class="ifsc-row">
									<input
										v-model="ifscCode"
										type="text"
										placeholder="SBIN0001234"
										:disabled="loading"
										@input="normalizeIfscInput"
										class="ifsc-input"
									/>
									<button
										type="button"
										class="ifsc-lookup-btn"
										@click="lookupIfsc"
										:disabled="ifscLoading || !ifscCode"
									>
										<span v-if="ifscLoading" class="spinner spinner-sm"></span>
										<span v-else>Lookup</span>
									</button>
								</div>
								<div v-if="ifscError" class="ifsc-error">{{ ifscError }}</div>
							</div>
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
									readonly
								/>
							</div>
							<div class="field-group field-span-2">
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
							<div class="field-group field-span-2">
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
						</div>
						<div v-if="error" class="auth-error">⚠️ {{ error }}</div>
						<div v-if="success" class="auth-success">✅ {{ success }}</div>
						<button type="submit" class="auth-btn" :disabled="loading || !!success">
							<span v-if="loading" class="spinner"></span>
							<span v-else>Create Vendor Account</span>
						</button>
						<button type="button" class="back-btn" @click="vendorStep = 3">
							← Back
						</button>
					</form>
				</template>
			</template>

			<p class="auth-footer">
				Already have an account?
				<RouterLink to="/login">Login</RouterLink>
			</p>
		</div>
	</div>
</template>

<script setup>
import { computed, ref, nextTick, watch } from "vue";
import { RouterLink, useRouter } from "vue-router";
import { api } from "@/api/frappe";

const router = useRouter();

// ── Account type ──────────────────────────────────────────
const accountType = ref("Customer");
const isVendor = computed(() => accountType.value === "Vendor");

function setAccountType(type) {
	accountType.value = type;
	resetAll();
}

const formStarted = computed(() => {
	if (!isVendor.value) return customerStep.value > 1;
	return vendorStep.value > 1;
});

// ── Shared fields ─────────────────────────────────────────
const fullName = ref("");
const email = ref("");
const password = ref("");
const phone = ref("");
const showPwd = ref(false);
const loading = ref(false);
const error = ref("");
const success = ref("");

// ── Vendor fields ─────────────────────────────────────────
const vendorName = ref("");
const storeName = ref("");
const gstNumber = ref("");
const address = ref("");
const storeDescription = ref("");
const bankAccountName = ref("");
const bankName = ref("");
const bankAccountNumber = ref("");
const ifscCode = ref("");
const ifscLoading = ref(false);
const ifscError = ref("");
const storeImages = ref([]);
const previewUrls = ref([]);

// ── OTP state ─────────────────────────────────────────────
const otpDigits = ref(["", "", "", "", "", ""]);
const otpRefs = ref([]);
const resendCooldown = ref(0);
let cooldownTimer = null;

// ── Steps ─────────────────────────────────────────────────
const customerStep = ref(1); // 1=info, 2=otp, 3=password
const vendorStep = ref(1); // 1=account, 2=otp, 3=business, 4=payout+pwd

const vendorSteps = [
	{ step: 1, label: "Account" },
	{ step: 2, label: "Verify" },
	{ step: 3, label: "Business" },
	{ step: 4, label: "Payout" },
];

// ── Input normalizers ─────────────────────────────────────
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
	ifscError.value = "";
}

// ── OTP helpers ───────────────────────────────────────────
function resetOtp() {
	otpDigits.value = ["", "", "", "", "", ""];
}

function startCooldown() {
	resendCooldown.value = 30;
	clearInterval(cooldownTimer);
	cooldownTimer = setInterval(() => {
		resendCooldown.value--;
		if (resendCooldown.value <= 0) clearInterval(cooldownTimer);
	}, 1000);
}

function onOtpInput(i) {
	const val = otpDigits.value[i];
	if (val && i < 5) {
		nextTick(() => otpRefs.value[i + 1]?.focus());
	}
}

function onOtpBackspace(i) {
	if (!otpDigits.value[i] && i > 0) {
		otpDigits.value[i - 1] = "";
		nextTick(() => otpRefs.value[i - 1]?.focus());
	}
}

// ── IFSC Lookup (free RazorpayX API) ─────────────────────
async function lookupIfsc() {
	const code = ifscCode.value.trim();
	if (!code || code.length < 11) {
		ifscError.value = "Please enter a valid 11-character IFSC code.";
		return;
	}
	ifscLoading.value = true;
	ifscError.value = "";
	try {
		const res = await fetch(`https://ifsc.razorpay.com/${code}`);
		if (!res.ok) throw new Error("IFSC not found");
		const data = await res.json();
		bankName.value = data.BANK || "";
	} catch {
		ifscError.value = "Invalid IFSC code. Please check and try again.";
		bankName.value = "";
	} finally {
		ifscLoading.value = false;
	}
}

// ── Image upload ──────────────────────────────────────────
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

// ── Customer flow ─────────────────────────────────────────
async function customerSendOtp() {
	error.value = "";
	if (!fullName.value.trim() || !email.value.trim() || phone.value.length < 10) {
		error.value = "Please fill all fields correctly.";
		return;
	}
	loading.value = true;
	try {
		await api.checkEmailExists(email.value.trim().toLowerCase());
		await api.checkPhoneExists(phone.value);
		await api.checkGstExists(gstNumber.value);
		await api.checkBankExists(bankAccountNumber.value);
		await api.sendOtp(email.value.trim().toLowerCase());
		resetOtp();
		startCooldown();
		customerStep.value = 2;
		nextTick(() => otpRefs.value[0]?.focus());
	} catch (e) {
		error.value = e.message || "Failed to send OTP. Please try again.";
	} finally {
		loading.value = false;
	}
}

async function customerVerifyOtp() {
	error.value = "";
	const otp = otpDigits.value.join("");
	if (otp.length < 6) return;
	loading.value = true;
	try {
		await api.verifyOtp(email.value.trim().toLowerCase(), otp);
		customerStep.value = 3;
	} catch (e) {
		error.value = e.message || "Invalid OTP. Please try again.";
	} finally {
		loading.value = false;
	}
}

async function handleCustomerSignup() {
	error.value = "";
	success.value = "";
	if (!password.value || password.value.length < 8) {
		error.value = "Password must be at least 8 characters.";
		return;
	}
	loading.value = true;
	try {
		const formData = new FormData();
		formData.append("email", email.value.trim().toLowerCase());
		formData.append("full_name", fullName.value.trim());
		formData.append("password", password.value);
		formData.append("account_type", "Customer");
		formData.append("phone", phone.value);
		const res = await api.signup(formData);

		if (res.account_type === "Vendor") {
			router.push("/desk");
		} else {
			router.push("/shop#/");
		}
		window.location.reload();
	} catch (e) {
		error.value = e.message || "Network error. Please try again.";
	} finally {
		loading.value = false;
	}
}

// ── Vendor flow ───────────────────────────────────────────
async function vendorNext(step) {
	error.value = "";
	if (step === 1) {
		if (!fullName.value.trim() || !email.value.trim() || phone.value.length < 10) {
			error.value = "Please fill all fields correctly.";
			return;
		}

		loading.value = true;

		try {
			await api.checkEmailExists(email.value.trim().toLowerCase());
			await api.checkPhoneExists(phone.value);
			await api.checkGstExists(gstNumber.value);
			await api.checkBankExists(bankAccountNumber.value);
			await vendorSendOtp();

			vendorStep.value = 2;
		} catch (e) {
			error.value = e.message || "Failed to proceed.";
		} finally {
			loading.value = false;
		}

		return;
	}
	if (step === 3) {
		error.value = "";

		if (!vendorName.value.trim() || !storeName.value.trim()) {
			error.value = "Vendor name and store name are required.";
			return;
		}

		if (storeImages.value.length !== 3) {
			error.value = "Please upload exactly 3 store images.";
			return;
		}

		loading.value = true;
		try {
			await api.checkVendorDetails({
				vendor_name: vendorName.value.trim(),
				store_name: storeName.value.trim(),
			});

			vendorStep.value = 4;
		} catch (e) {
			error.value = e.message || "Validation failed.";
		} finally {
			loading.value = false;
		}
	}
}

let timer;

watch(storeName, (val) => {
	clearTimeout(timer);

	if (val.length < 3) return;

	timer = setTimeout(async () => {
		try {
			await api.checkVendorDetails({ store_name: val });
			error.value = "";
		} catch (e) {
			error.value = e.message;
		}
	}, 500);
});

async function vendorSendOtp() {
	try {
		await api.sendOtp(email.value.trim().toLowerCase());
		resetOtp();
		startCooldown();
		nextTick(() => otpRefs.value[0]?.focus());
	} catch (e) {
		error.value = e.message || "Failed to send OTP.";
		throw e;
	}
}

async function vendorVerifyOtp() {
	error.value = "";
	const otp = otpDigits.value.join("");
	if (otp.length < 6) return;
	loading.value = true;
	try {
		await api.verifyOtp(email.value.trim().toLowerCase(), otp);
		vendorStep.value = 3;
	} catch (e) {
		error.value = e.message || "Invalid OTP. Please try again.";
	} finally {
		loading.value = false;
	}
}

async function handleVendorSignup() {
	error.value = "";
	success.value = "";
	if (!password.value || password.value.length < 8) {
		error.value = "Password must be at least 8 characters.";
		return;
	}
	loading.value = true;
	try {
		const formData = new FormData();
		formData.append("email", email.value.trim().toLowerCase());
		formData.append("full_name", fullName.value.trim());
		formData.append("password", password.value);
		formData.append("account_type", "Vendor");
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
		storeImages.value.forEach((file) => formData.append("store_images", file));
		const res = await api.signup(formData);

		if (res.account_type === "Vendor") {
			router.push("/desk");
		} else {
			router.push("/shop#/");
		}
		window.location.reload();
	} catch (e) {
		error.value = e.message || "Network error. Please try again.";
	} finally {
		loading.value = false;
	}
}

// ── Reset ─────────────────────────────────────────────────
function resetAll() {
	fullName.value = "";
	email.value = "";
	password.value = "";
	phone.value = "";
	vendorName.value = "";
	storeName.value = "";
	gstNumber.value = "";
	address.value = "";
	storeDescription.value = "";
	bankAccountName.value = "";
	bankName.value = "";
	bankAccountNumber.value = "";
	ifscCode.value = "";
	error.value = "";
	success.value = "";
	customerStep.value = 1;
	vendorStep.value = 1;
	resetOtp();
	storeImages.value = [];
	previewUrls.value = [];
}
</script>

<style scoped>
.register-as-tag {
	font-size: 0.82rem;
	color: #888;
	margin: -1rem 0 1.25rem;
}
.register-as-tag strong {
	color: #5b4fcf;
	font-weight: 700;
}

/* ── New additions only (existing styles untouched) ──── */

.otp-hint {
	font-size: 0.85rem;
	color: #666;
	margin-bottom: 0.25rem;
}

.otp-inputs {
	display: flex;
	gap: 0.5rem;
}

.otp-box {
	width: 44px;
	height: 52px;
	text-align: center;
	font-size: 1.3rem;
	font-weight: 700;
	border: 1.5px solid #e0e0e0;
	border-radius: 10px;
	outline: none;
	transition: border-color 0.15s;
	color: #1a1a2e;
	caret-color: #5b4fcf;
}

.otp-box:focus {
	border-color: #5b4fcf;
	box-shadow: 0 0 0 3px rgba(91, 79, 207, 0.1);
}

.otp-resend {
	font-size: 0.82rem;
	color: #888;
	margin-top: -0.25rem;
}

.resend-btn {
	background: none;
	border: none;
	color: #5b4fcf;
	font-weight: 600;
	font-size: 0.82rem;
	cursor: pointer;
	padding: 0;
}

.resend-btn:hover {
	text-decoration: underline;
}

.step-success-hint {
	background: #e8f8f0;
	color: #27ae60;
	padding: 0.65rem 0.9rem;
	border-radius: 10px;
	font-size: 0.85rem;
	font-weight: 500;
}

.back-btn {
	background: none;
	border: 1.5px solid #e0e0e0;
	border-radius: 10px;
	padding: 0.65rem;
	font-size: 0.88rem;
	font-weight: 600;
	color: #555;
	cursor: pointer;
	width: 100%;
	transition:
		border-color 0.15s,
		color 0.15s;
}

.back-btn:hover {
	border-color: #5b4fcf;
	color: #5b4fcf;
}

/* Vendor step indicator */
.vendor-steps {
	position: relative;
	display: flex;
	justify-content: space-between;
	margin-bottom: 1.75rem;
	padding: 0 0.5rem;
}

.vstep-line {
	position: absolute;
	top: 16px;
	left: 10%;
	right: 10%;
	height: 2px;
	background: #ece8ff;
	z-index: 0;
}

.vstep {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 0.35rem;
	z-index: 1;
}

.vstep-dot {
	width: 32px;
	height: 32px;
	border-radius: 50%;
	border: 2px solid #e0e0e0;
	background: #fff;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 0.8rem;
	font-weight: 700;
	color: #aaa;
	transition: all 0.2s;
}

.vstep.active .vstep-dot {
	border-color: #5b4fcf;
	background: #5b4fcf;
	color: #fff;
}

.vstep.done .vstep-dot {
	border-color: #27ae60;
	background: #27ae60;
	color: #fff;
}

.vstep-label {
	font-size: 0.72rem;
	color: #aaa;
	font-weight: 600;
}

.vstep.active .vstep-label {
	color: #5b4fcf;
}

.vstep.done .vstep-label {
	color: #27ae60;
}

.section-heading {
	font-size: 1rem;
	font-weight: 800;
	color: #1a1a2e;
	margin-bottom: 0.75rem;
	padding-bottom: 0.5rem;
	border-bottom: 2px solid #ece8ff;
}

/* IFSC row */
.ifsc-row {
	display: flex;
	gap: 0.5rem;
}

.ifsc-input {
	flex: 1;
}

.ifsc-lookup-btn {
	padding: 0 1rem;
	background: linear-gradient(135deg, #5b4fcf, #764ba2);
	color: #fff;
	border: none;
	border-radius: 10px;
	font-size: 0.85rem;
	font-weight: 700;
	cursor: pointer;
	transition: opacity 0.2s;
	min-width: 76px;
	display: flex;
	align-items: center;
	justify-content: center;
}

.ifsc-lookup-btn:disabled {
	opacity: 0.5;
	cursor: not-allowed;
}

.ifsc-error {
	font-size: 0.8rem;
	color: #e74c3c;
	margin-top: 0.3rem;
}

.spinner-sm {
	width: 14px;
	height: 14px;
	border: 2px solid rgba(255, 255, 255, 0.4);
	border-top-color: #fff;
	border-radius: 50%;
	animation: spin 0.7s linear infinite;
	display: inline-block;
}

/* ── Existing styles (kept as-is) ───────────────────────── */

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

.preview-grid {
	display: flex;
	gap: 12px;
	margin-top: 12px;
}
.preview-item {
	position: relative;
}
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
	max-width: 600px;
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
	.otp-box {
		width: 38px;
		height: 46px;
		font-size: 1.1rem;
	}
	.preview-item img {
		width: 70px;
		height: 70px;
	}
}
</style>
