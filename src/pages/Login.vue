<template>
	<div class="auth-page">
		<div class="auth-card">
			<!-- Logo -->
			<div class="auth-logo">
				<div class="logo-icon">T</div>
				<span class="logo-text">Trade<span class="logo-accent">Nest</span></span>
			</div>

			<!-- Login Form -->
			<template v-if="view === 'login'">
				<h1 class="auth-title">Welcome Back</h1>
				<p class="auth-sub">Access your account.</p>

				<form @submit.prevent="handleLogin" class="auth-form">
					<div class="field-group">
						<label>Email</label>
						<input
							v-model="form.usr"
							type="text"
							placeholder="email@example.com or username"
							required
							:disabled="loading"
							autocomplete="username"
						/>
					</div>

					<div class="field-group">
						<label>Password</label>
						<div class="password-wrap">
							<input
								v-model="form.pwd"
								:type="showPwd ? 'text' : 'password'"
								placeholder="••••••••"
								required
								:disabled="loading"
								autocomplete="current-password"
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

					<div class="forgot-link">
						<a @click.prevent="view = 'forgot'" href="#">Forgot Password?</a>
					</div>

					<div v-if="error" class="auth-error">⚠️ {{ error }}</div>

					<button type="submit" class="auth-btn" :disabled="loading">
						<span v-if="loading" class="spinner"></span>
						<span v-else>Login</span>
					</button>
				</form>

				<p class="auth-footer">
					I don't have an account.
					<RouterLink to="/signup">Sign Up Free</RouterLink>
				</p>
			</template>

			<!-- Forgot Password Form -->
			<template v-else-if="view === 'forgot'">
				<h1 class="auth-title">Forgot Password</h1>
				<p class="auth-sub">Enter your email to receive a reset link</p>

				<form @submit.prevent="handleForgot" class="auth-form">
					<div class="field-group">
						<label>Email</label>
						<input
							v-model="forgotEmail"
							type="email"
							placeholder="email@example.com"
							required
							:disabled="loading"
						/>
					</div>

					<div v-if="error" class="auth-error">⚠️ {{ error }}</div>
					<div v-if="forgotSuccess" class="auth-success">✅ {{ forgotSuccess }}</div>

					<button type="submit" class="auth-btn" :disabled="loading || !!forgotSuccess">
						<span v-if="loading" class="spinner"></span>
						<span v-else>Send Reset Link</span>
					</button>
				</form>

				<p class="auth-footer">
					<a
						@click.prevent="
							view = 'login';
							error = '';
							forgotSuccess = '';
						"
						href="#"
					>
						← Back to Login
					</a>
				</p>
			</template>
		</div>
	</div>
</template>

<script setup>
import { ref } from "vue";
import { RouterLink } from "vue-router";
import { api } from "@/api/frappe";
import { invalidateAuthCache } from "@/router/index";

const view = ref("login");
const loading = ref(false);
const error = ref("");
const showPwd = ref(false);

const form = ref({ usr: "", pwd: "" });

const forgotEmail = ref("");
const forgotSuccess = ref("");

async function handleLogin() {
	loading.value = true;
	error.value = "";
	try {
		await api.login(form.value.usr, form.value.pwd);
		invalidateAuthCache();
		window.location.href = "/shop";
	} catch (e) {
		error.value = "Invalid email or password";
	} finally {
		loading.value = false;
	}
}

async function handleForgot() {
	loading.value = true;
	error.value = "";
	forgotSuccess.value = "";
	try {
		const res = await api.forgotPassword(forgotEmail.value);
		forgotSuccess.value = res.message?.message || "Reset link sent! Check your email.";
	} catch (e) {
		error.value = e.message || "Something went wrong, please try again";
	} finally {
		loading.value = false;
	}
}
</script>

<style scoped>
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
.field-group input {
	padding: 0.65rem 0.9rem;
	border: 1.5px solid #e0e0e0;
	border-radius: 10px;
	font-size: 0.9rem;
	color: #1a1a2e;
	outline: none;
	transition: border-color 0.15s;
	width: 100%;
	box-sizing: border-box;
}
.field-group input:focus {
	border-color: #5b4fcf;
}
.field-group input:disabled {
	background: #f9f9f9;
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

.forgot-link {
	text-align: right;
	margin-top: -0.25rem;
}
.forgot-link a {
	font-size: 0.8rem;
	color: #5b4fcf;
	font-weight: 600;
	text-decoration: none;
}
.forgot-link a:hover {
	text-decoration: underline;
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
</style>
