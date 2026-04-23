<template>
	<nav class="navbar">
		<div class="navbar-inner">
			<!-- Logo -->
			<RouterLink to="/" class="navbar-logo">
				<div class="logo-icon">T</div>
				<span class="logo-text">Trade<span class="logo-accent">Nest</span></span>
			</RouterLink>

			<!-- Nav Links -->
			<div class="nav-links">
				<RouterLink to="/" class="nav-link">Home</RouterLink>
				<RouterLink to="/items" class="nav-link">Shop</RouterLink>
				<RouterLink to="/cart" class="nav-link">
					Cart
					<span v-if="isLoggedIn && cartCount > 0" class="cart-badge">{{
						cartCount
					}}</span>
				</RouterLink>
				<RouterLink to="/orders" class="nav-link">Orders</RouterLink>
				<RouterLink to="/privacy-policy" class="nav-link">Privacy</RouterLink>
			</div>

			<div v-if="isLoggedIn" class="user-menu" @click="toggleDropdown" ref="menuRef">
				<div class="avatar">
					<img v-if="userImage" :src="userImage" class="avatar-img" :alt="userName" />
					<span v-else>{{ userInitial }}</span>
				</div>
				<span class="user-name">{{ userName }}</span>
				<span class="chevron" :class="{ open: dropdownOpen }">▾</span>

				<div v-if="dropdownOpen" class="dropdown">
					<div class="dropdown-header" @click.stop="goToProfile">
						<div class="avatar lg" style="cursor: pointer">
							<img
								v-if="userImage"
								:src="userImage"
								class="avatar-img"
								:alt="userName"
							/>
							<span v-else>{{ userInitial }}</span>
						</div>
						<div>
							<div class="dh-name">{{ userName }}</div>
							<div class="dh-email">{{ userEmail }}</div>
						</div>
					</div>
					<hr class="dropdown-divider" />
					<RouterLink to="/profile" class="dropdown-item" @click="dropdownOpen = false">
						👤 My Profile
					</RouterLink>
					<RouterLink to="/orders" class="dropdown-item" @click="dropdownOpen = false">
						📦 My Orders
					</RouterLink>
					<RouterLink to="/cart" class="dropdown-item" @click="dropdownOpen = false">
						🛒 My Cart
					</RouterLink>
					<RouterLink
						to="/become-vendor"
						class="dropdown-item"
						@click="dropdownOpen = false"
					>
						🏪 Become a Vendor
					</RouterLink>
					<RouterLink to="/profile" class="dropdown-item" @click="dropdownOpen = false">
						⚙️ Settings
					</RouterLink>
					<hr class="dropdown-divider" />
					<button class="dropdown-item logout" @click="confirmLogout">🚪 Logout</button>
				</div>
			</div>

			<div v-else class="guest-actions">
				<RouterLink to="/login" class="auth-link">Login</RouterLink>
				<RouterLink to="/signup" class="auth-btn-link">Create Account</RouterLink>
			</div>
		</div>
	</nav>

	<!-- Logout Confirmation -->
	<Teleport to="body">
		<div v-if="logoutConfirm" class="confirm-overlay" @click.self="logoutConfirm = false">
			<div class="confirm-box">
				<div class="confirm-icon">🚪</div>
				<h3>Confirm Logout</h3>
				<p>You will be logged out of your account.</p>
				<div class="confirm-actions">
					<button class="confirm-cancel" @click="logoutConfirm = false">Cancel</button>
					<button class="confirm-ok" @click="doLogout">Logout</button>
				</div>
			</div>
		</div>
	</Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { RouterLink, useRouter } from "vue-router";
import { useCartStore } from "@/stores/cart";
import { api } from "@/api/frappe";

const router = useRouter();
const cart = useCartStore();
const cartCount = computed(() => cart.items.length);

const dropdownOpen = ref(false);
const menuRef = ref(null);
const isLoggedIn = ref(false);
const userName = ref("Account");
const userEmail = ref("");
const userImage = ref("");
const logoutConfirm = ref(false);
const userInitial = computed(() => userName.value.charAt(0).toUpperCase());

onMounted(async () => {
	try {
		const res = await api.getSessionProfile();
		const profile = res.message;
		isLoggedIn.value = !!profile?.authenticated;

		if (isLoggedIn.value) {
			userEmail.value = profile.email;
			userName.value = profile.full_name || profile.email.split("@")[0];
			userImage.value = profile.user_image || "";
		}
	} catch {
		isLoggedIn.value = false;
	}

	document.addEventListener("click", onOutsideClick);
});

onUnmounted(() => document.removeEventListener("click", onOutsideClick));

function toggleDropdown() {
	dropdownOpen.value = !dropdownOpen.value;
}

function onOutsideClick(e) {
	if (menuRef.value && !menuRef.value.contains(e.target)) {
		dropdownOpen.value = false;
	}
}

function goToProfile() {
	dropdownOpen.value = false;
	router.push("/profile");
}

function confirmLogout() {
	dropdownOpen.value = false;
	logoutConfirm.value = true;
}

async function doLogout() {
	logoutConfirm.value = false;
	await api.logout();
}
</script>

<style scoped>
.navbar {
	position: sticky;
	top: 0;
	z-index: 100;
	background: #fff;
	border-bottom: 1px solid #ebebeb;
	box-shadow: 0 1px 6px rgba(0, 0, 0, 0.07);
}
.navbar-inner {
	max-width: 1200px;
	margin: 0 auto;
	padding: 0 1.5rem;
	height: 62px;
	display: flex;
	align-items: center;
	gap: 2rem;
}

/* Logo */
.navbar-logo {
	display: flex;
	align-items: center;
	gap: 0.5rem;
	text-decoration: none;
	flex-shrink: 0;
}
.logo-icon {
	width: 34px;
	height: 34px;
	background: linear-gradient(135deg, #5b4fcf, #764ba2);
	color: #fff;
	font-weight: 800;
	font-size: 1.1rem;
	border-radius: 9px;
	display: flex;
	align-items: center;
	justify-content: center;
}
.logo-text {
	font-size: 1.15rem;
	font-weight: 700;
	color: #1a1a2e;
}
.logo-accent {
	color: #5b4fcf;
}

/* Nav links */
.nav-links {
	display: flex;
	align-items: center;
	gap: 0.25rem;
	flex: 1;
}
.nav-link {
	text-decoration: none;
	color: #555;
	font-size: 0.88rem;
	font-weight: 500;
	padding: 0.4rem 0.75rem;
	border-radius: 8px;
	transition: all 0.15s;
	position: relative;
}
.nav-link:hover {
	background: #f5f3ff;
	color: #5b4fcf;
}
.nav-link.router-link-active {
	color: #5b4fcf;
	background: #f0edff;
}
.cart-badge {
	position: absolute;
	top: -2px;
	right: -2px;
	background: #e74c3c;
	color: #fff;
	font-size: 0.65rem;
	font-weight: 700;
	min-width: 16px;
	height: 16px;
	border-radius: 8px;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 0 3px;
}

/* User menu */
.user-menu {
	display: flex;
	align-items: center;
	gap: 0.5rem;
	cursor: pointer;
	padding: 0.4rem 0.75rem;
	border-radius: 10px;
	border: 1.5px solid #ebebeb;
	position: relative;
	transition: border-color 0.15s;
	flex-shrink: 0;
}
.user-menu:hover {
	border-color: #5b4fcf;
}
.guest-actions {
	display: flex;
	align-items: center;
	gap: 0.75rem;
	flex-shrink: 0;
}
.auth-link {
	color: #5b4fcf;
	font-size: 0.9rem;
	font-weight: 600;
	text-decoration: none;
}
.auth-btn-link {
	text-decoration: none;
	background: linear-gradient(135deg, #5b4fcf, #764ba2);
	color: #fff;
	padding: 0.65rem 1rem;
	border-radius: 10px;
	font-size: 0.85rem;
	font-weight: 700;
	box-shadow: 0 10px 24px rgba(91, 79, 207, 0.22);
}
.avatar {
	width: 28px;
	height: 28px;
	background: linear-gradient(135deg, #5b4fcf, #764ba2);
	color: #fff;
	font-size: 0.8rem;
	font-weight: 700;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
}
.avatar.lg {
	width: 38px;
	height: 38px;
	font-size: 1rem;
	flex-shrink: 0;
}
.user-name {
	font-size: 0.85rem;
	font-weight: 500;
	color: #333;
	text-decoration: none;
}
.chevron {
	font-size: 0.75rem;
	color: #888;
	transition: transform 0.2s;
}
.chevron.open {
	transform: rotate(180deg);
}

/* Dropdown */
.dropdown {
	position: absolute;
	top: calc(100% + 8px);
	right: 0;
	background: #fff;
	border: 1px solid #ebebeb;
	border-radius: 12px;
	box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
	min-width: 220px;
	overflow: hidden;
	animation: fadeDown 0.15s ease;
}
@keyframes fadeDown {
	from {
		opacity: 0;
		transform: translateY(-6px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}
.dropdown-header {
	display: flex;
	align-items: center;
	gap: 0.75rem;
	padding: 1rem;
}
.dh-name {
	font-weight: 600;
	font-size: 0.88rem;
	color: #1a1a2e;
}
.dh-email {
	font-size: 0.75rem;
	color: #888;
	margin-top: 2px;
}
.dropdown-divider {
	border: none;
	border-top: 1px solid #f0f0f0;
	margin: 0;
}
.dropdown-item {
	display: flex;
	align-items: center;
	gap: 0.5rem;
	padding: 0.7rem 1rem;
	font-size: 0.87rem;
	color: #333;
	text-decoration: none;
	transition: background 0.15s;
	width: 100%;
	background: none;
	border: none;
	cursor: pointer;
	text-align: left;
}
.dropdown-item:hover {
	background: #f9f7ff;
	color: #5b4fcf;
}
.dropdown-item.logout:hover {
	background: #fff5f5;
	color: #e74c3c;
}

@media (max-width: 640px) {
	.nav-links {
		display: none;
	}
	.user-name {
		display: none;
	}
	.guest-actions {
		margin-left: auto;
		gap: 0.5rem;
	}
	.auth-btn-link {
		padding: 0.55rem 0.8rem;
		font-size: 0.8rem;
	}
}

/* Avatar image */
.avatar-img {
	width: 100%;
	height: 100%;
	object-fit: cover;
	border-radius: 50%;
}

/* Avatar Lightbox */
.av-overlay {
	position: fixed;
	inset: 0;
	background: rgba(10, 10, 20, 0.88);
	z-index: 9999;
	display: flex;
	align-items: center;
	justify-content: center;
	animation: av-fade 0.2s ease;
}
@keyframes av-fade {
	from {
		opacity: 0;
	}
	to {
		opacity: 1;
	}
}
.av-close {
	position: fixed;
	top: 1.25rem;
	right: 1.5rem;
	background: rgba(255, 255, 255, 0.15);
	border: none;
	color: #fff;
	font-size: 1.2rem;
	width: 38px;
	height: 38px;
	border-radius: 50%;
	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 10000;
}
.av-close:hover {
	background: rgba(255, 255, 255, 0.3);
}
.av-box {
	background: #fff;
	border-radius: 18px;
	overflow: hidden;
	max-width: 340px;
	width: 90%;
	animation: av-up 0.22s ease;
	text-align: center;
}
@keyframes av-up {
	from {
		transform: translateY(24px);
		opacity: 0;
	}
	to {
		transform: translateY(0);
		opacity: 1;
	}
}
.av-img-wrap {
	width: 100%;
	height: 300px;
	background: linear-gradient(135deg, #667eea, #764ba2);
	display: flex;
	align-items: center;
	justify-content: center;
}
.av-img {
	width: 100%;
	height: 100%;
	object-fit: cover;
}
.av-placeholder {
	font-size: 6rem;
	font-weight: 800;
	color: #fff;
	text-transform: uppercase;
}
.av-info {
	padding: 1.25rem 1.5rem 1.5rem;
}
.av-name {
	font-size: 1.1rem;
	font-weight: 700;
	color: #1a1a2e;
	margin: 0 0 0.3rem;
}
.av-email {
	font-size: 0.85rem;
	color: #888;
	margin: 0;
}

/* Logout Confirmation */
.confirm-overlay {
	position: fixed;
	inset: 0;
	background: rgba(10, 10, 20, 0.6);
	z-index: 9999;
	display: flex;
	align-items: center;
	justify-content: center;
}
.confirm-box {
	background: #fff;
	border-radius: 18px;
	padding: 2rem 2rem 1.5rem;
	max-width: 320px;
	width: 90%;
	text-align: center;
	animation: av-up 0.2s ease;
}
.confirm-icon {
	font-size: 2.5rem;
	margin-bottom: 0.75rem;
}
.confirm-box h3 {
	font-size: 1.05rem;
	font-weight: 700;
	color: #1a1a2e;
	margin: 0 0 0.4rem;
}
.confirm-box p {
	font-size: 0.85rem;
	color: #888;
	margin: 0 0 1.5rem;
}
.confirm-actions {
	display: flex;
	gap: 0.75rem;
}
.confirm-cancel {
	flex: 1;
	padding: 0.6rem;
	border: 1.5px solid #e0e0e0;
	border-radius: 10px;
	background: #fff;
	color: #555;
	font-size: 0.9rem;
	font-weight: 600;
	cursor: pointer;
	transition: border-color 0.15s;
}
.confirm-cancel:hover {
	border-color: #aaa;
}
.confirm-ok {
	flex: 1;
	padding: 0.6rem;
	border: none;
	border-radius: 10px;
	background: #e74c3c;
	color: #fff;
	font-size: 0.9rem;
	font-weight: 600;
	cursor: pointer;
	transition: background 0.15s;
}
.confirm-ok:hover {
	background: #c0392b;
}
</style>
