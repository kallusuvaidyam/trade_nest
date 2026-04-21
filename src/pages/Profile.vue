<template>
	<div class="profile-page">
		<div class="profile-container">
			<div class="profile-header">
				<div class="profile-avatar-wrap" @click="openAvatarLightbox">
					<div class="profile-avatar">
						<img v-if="userImage" :src="userImage" class="avatar-img" :alt="userName" />
						<span v-else class="avatar-initial">{{ userInitial }}</span>
					</div>
					<div class="avatar-edit-hint">{{ uploading ? '...' : 'Edit' }}</div>
				</div>
				<input ref="fileInput" type="file" accept="image/*" style="display:none" @change="onFileChange" />
				<div class="profile-meta">
					<h1 class="profile-name">{{ userName }}</h1>
					<p class="profile-email">{{ userEmail }}</p>
					<span class="profile-role-badge">{{ userRole }}</span>
				</div>
			</div>

			<div class="profile-sections">
				<div class="profile-card">
					<h2 class="section-title">Account Details</h2>
					<div class="detail-row">
						<span class="detail-label">Full Name</span>
						<span class="detail-value">{{ userName }}</span>
					</div>
					<div class="detail-row">
						<span class="detail-label">Email</span>
						<span class="detail-value">{{ userEmail }}</span>
					</div>
					<div class="detail-row">
						<span class="detail-label">Username</span>
						<span class="detail-value">{{ username }}</span>
					</div>
					<div class="detail-row">
						<span class="detail-label">Role</span>
						<span class="detail-value">{{ userRole }}</span>
					</div>
					<div class="detail-row">
						<span class="detail-label">Member Since</span>
						<span class="detail-value">{{ memberSince }}</span>
					</div>
				</div>

				<div class="profile-card">
					<h2 class="section-title">Quick Links</h2>
					<div class="quick-links">
						<RouterLink to="/orders" class="quick-link">
							<span class="ql-icon">📦</span>
							<div>
								<div class="ql-title">My Orders</div>
								<div class="ql-sub">View your order history</div>
							</div>
							<span class="ql-arrow">›</span>
						</RouterLink>
						<RouterLink to="/cart" class="quick-link">
							<span class="ql-icon">🛒</span>
							<div>
								<div class="ql-title">My Cart</div>
								<div class="ql-sub">{{ cartCount }} item(s) in cart</div>
							</div>
							<span class="ql-arrow">›</span>
						</RouterLink>
						<RouterLink to="/become-vendor" class="quick-link">
							<span class="ql-icon">🏪</span>
							<div>
								<div class="ql-title">Become a Vendor</div>
								<div class="ql-sub">Start selling on Trade Nest</div>
							</div>
							<span class="ql-arrow">›</span>
						</RouterLink>
					</div>
				</div>

				<div class="profile-card danger-zone">
					<h2 class="section-title">Account Actions</h2>
					<button class="logout-btn" @click="confirmLogout = true">🚪 Logout</button>
				</div>
			</div>
		</div>

		<!-- Avatar Lightbox -->
		<Teleport to="body">
			<div v-if="avatarLightbox" class="av-overlay" @click="avatarLightbox = false">
				<button class="av-close" @click="avatarLightbox = false">✕</button>
				<div class="av-box" @click.stop>
					<div class="av-img-wrap">
						<img v-if="userImage" :src="userImage" :alt="userName" class="av-img" />
						<div v-else class="av-placeholder">{{ userInitial }}</div>
					</div>
					<div class="av-info">
						<p class="av-name">{{ userName }}</p>
						<p class="av-email">{{ userEmail }}</p>
						<button class="av-change-btn" :disabled="uploading" @click="triggerFileInput">
							{{ uploading ? 'Uploading...' : '📷 Change Photo' }}
						</button>
						<p v-if="uploadError" class="av-error">{{ uploadError }}</p>
						<p v-if="uploadSuccess" class="av-success">Photo updated!</p>
					</div>
				</div>
			</div>
		</Teleport>

		<!-- Logout Confirm -->
		<Teleport to="body">
			<div v-if="confirmLogout" class="confirm-overlay" @click.self="confirmLogout = false">
				<div class="confirm-box">
					<div class="confirm-icon">🚪</div>
					<h3>Confirm Logout</h3>
					<p>You will be logged out of your account.</p>
					<div class="confirm-actions">
						<button class="confirm-cancel" @click="confirmLogout = false">Cancel</button>
						<button class="confirm-ok" @click="doLogout">Logout</button>
					</div>
				</div>
			</div>
		</Teleport>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '@/api/frappe'
import { useCartStore } from '@/stores/cart'

const cart = useCartStore()
const cartCount = computed(() => cart.items.reduce((s, i) => s + i.qty, 0))

const userName = ref('Account')
const userEmail = ref('')
const userImage = ref('')
const username = ref('')
const userRole = ref('')
const memberSince = ref('')
const avatarLightbox = ref(false)
const confirmLogout = ref(false)
const fileInput = ref(null)
const uploading = ref(false)
const uploadError = ref('')
const uploadSuccess = ref(false)

const userInitial = computed(() => userName.value.charAt(0).toUpperCase())

onMounted(async () => {
	try {
		const res = await api.getProfile()
		const p = res.message
		userEmail.value = p.email
		userName.value = p.full_name || p.email.split('@')[0]
		userImage.value = p.user_image || ''
		username.value = p.name || p.email
		userRole.value = p.role_profile_name || 'Customer'
		if (p.creation) {
			memberSince.value = new Date(p.creation).toLocaleDateString('en-IN', {
				year: 'numeric', month: 'long', day: 'numeric'
			})
		}
	} catch {}
})

function openAvatarLightbox() {
	avatarLightbox.value = true
}

function triggerFileInput() {
	uploadError.value = ''
	uploadSuccess.value = false
	fileInput.value?.click()
}

async function onFileChange(e) {
	const file = e.target.files?.[0]
	if (!file) return
	uploading.value = true
	uploadError.value = ''
	uploadSuccess.value = false
	try {
		const res = await api.uploadProfileImage(file)
		const fileUrl = res.message?.user_image || res.message?.file_url
		if (!fileUrl) throw new Error('Upload failed')
		userImage.value = fileUrl
		uploadSuccess.value = true
		setTimeout(() => { uploadSuccess.value = false }, 3000)
	} catch (err) {
		uploadError.value = err.message || 'Upload failed'
	} finally {
		uploading.value = false
		e.target.value = ''
	}
}

async function doLogout() {
	confirmLogout.value = false
	await api.logout()
}
</script>

<style scoped>
.profile-page {
	min-height: 100vh;
	background: #f5f6fa;
	padding: 2rem 1.5rem 4rem;
	font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
.profile-container {
	max-width: 680px;
	margin: 0 auto;
}

.profile-header {
	background: #fff;
	border-radius: 20px;
	box-shadow: 0 2px 12px rgba(0,0,0,0.07);
	padding: 2rem;
	display: flex;
	align-items: center;
	gap: 1.75rem;
	margin-bottom: 1.25rem;
}
.profile-avatar-wrap {
	position: relative;
	cursor: zoom-in;
	flex-shrink: 0;
}
.profile-avatar {
	width: 90px;
	height: 90px;
	border-radius: 50%;
	background: linear-gradient(135deg, #5b4fcf, #764ba2);
	display: flex;
	align-items: center;
	justify-content: center;
	overflow: hidden;
}
.avatar-img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }
.avatar-initial { font-size: 2.2rem; font-weight: 800; color: #fff; }
.avatar-edit-hint {
	position: absolute;
	bottom: 0;
	right: 0;
	background: #5b4fcf;
	color: #fff;
	font-size: 0.6rem;
	font-weight: 700;
	padding: 2px 5px;
	border-radius: 8px;
}
.profile-name {
	font-size: 1.4rem;
	font-weight: 800;
	color: #1a1a2e;
	margin: 0 0 0.25rem;
}
.profile-email {
	font-size: 0.88rem;
	color: #888;
	margin: 0 0 0.5rem;
}
.profile-role-badge {
	background: #f0edff;
	color: #5b4fcf;
	font-size: 0.75rem;
	font-weight: 700;
	padding: 0.2rem 0.65rem;
	border-radius: 20px;
}

.profile-sections { display: flex; flex-direction: column; gap: 1.25rem; }
.profile-card {
	background: #fff;
	border-radius: 16px;
	box-shadow: 0 2px 8px rgba(0,0,0,0.06);
	padding: 1.5rem;
}
.section-title {
	font-size: 0.82rem;
	font-weight: 700;
	color: #888;
	text-transform: uppercase;
	letter-spacing: 0.05em;
	margin: 0 0 1.1rem;
}

.detail-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 0.65rem 0;
	border-bottom: 1px solid #f5f6fa;
	font-size: 0.88rem;
}
.detail-row:last-child { border-bottom: none; }
.detail-label { color: #888; font-weight: 500; }
.detail-value { color: #1a1a2e; font-weight: 600; }

.quick-links { display: flex; flex-direction: column; gap: 0.5rem; }
.quick-link {
	display: flex;
	align-items: center;
	gap: 0.85rem;
	padding: 0.75rem 0.85rem;
	border-radius: 10px;
	text-decoration: none;
	transition: background 0.15s;
}
.quick-link:hover { background: #f5f3ff; }
.ql-icon { font-size: 1.3rem; flex-shrink: 0; }
.ql-title { font-size: 0.88rem; font-weight: 600; color: #1a1a2e; }
.ql-sub { font-size: 0.75rem; color: #999; margin-top: 1px; }
.ql-arrow { margin-left: auto; color: #ccc; font-size: 1.1rem; font-weight: 700; }

.logout-btn {
	width: 100%;
	padding: 0.75rem;
	background: #fff5f5;
	color: #e74c3c;
	border: 1.5px solid #fdd;
	border-radius: 10px;
	font-size: 0.9rem;
	font-weight: 600;
	cursor: pointer;
	transition: background 0.15s;
}
.logout-btn:hover { background: #ffe0e0; }

/* Avatar Lightbox */
.av-overlay {
	position: fixed; inset: 0;
	background: rgba(10,10,20,0.88);
	z-index: 9999; display: flex;
	align-items: center; justify-content: center;
}
.av-close {
	position: fixed; top: 1.25rem; right: 1.5rem;
	background: rgba(255,255,255,0.15); border: none;
	color: #fff; font-size: 1.2rem; width: 38px; height: 38px;
	border-radius: 50%; cursor: pointer; display: flex;
	align-items: center; justify-content: center; z-index: 10000;
}
.av-box {
	background: #fff; border-radius: 18px;
	overflow: hidden; max-width: 340px; width: 90%; text-align: center;
}
.av-img-wrap {
	width: 100%; height: 300px;
	background: linear-gradient(135deg, #667eea, #764ba2);
	display: flex; align-items: center; justify-content: center;
}
.av-img { width: 100%; height: 100%; object-fit: cover; }
.av-placeholder { font-size: 6rem; font-weight: 800; color: #fff; text-transform: uppercase; }
.av-info { padding: 1.25rem 1.5rem 1.5rem; }
.av-name { font-size: 1.1rem; font-weight: 700; color: #1a1a2e; margin: 0 0 0.3rem; }
.av-email { font-size: 0.85rem; color: #888; margin: 0 0 1rem; }
.av-change-btn {
	width: 100%; padding: 0.6rem;
	background: #5b4fcf; color: #fff;
	border: none; border-radius: 10px;
	font-size: 0.88rem; font-weight: 600;
	cursor: pointer; transition: background 0.15s;
}
.av-change-btn:hover:not(:disabled) { background: #4a3fbf; }
.av-change-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.av-error { font-size: 0.8rem; color: #e74c3c; margin: 0.5rem 0 0; }
.av-success { font-size: 0.8rem; color: #27ae60; margin: 0.5rem 0 0; }

/* Logout confirm */
.confirm-overlay {
	position: fixed; inset: 0; background: rgba(10,10,20,0.6);
	z-index: 9999; display: flex; align-items: center; justify-content: center;
}
.confirm-box {
	background: #fff; border-radius: 18px; padding: 2rem 2rem 1.5rem;
	max-width: 320px; width: 90%; text-align: center;
}
.confirm-icon { font-size: 2.5rem; margin-bottom: 0.75rem; }
.confirm-box h3 { font-size: 1.05rem; font-weight: 700; color: #1a1a2e; margin: 0 0 0.4rem; }
.confirm-box p { font-size: 0.85rem; color: #888; margin: 0 0 1.5rem; }
.confirm-actions { display: flex; gap: 0.75rem; }
.confirm-cancel {
	flex: 1; padding: 0.6rem; border: 1.5px solid #e0e0e0;
	border-radius: 10px; background: #fff; color: #555;
	font-size: 0.9rem; font-weight: 600; cursor: pointer;
}
.confirm-ok {
	flex: 1; padding: 0.6rem; border: none;
	border-radius: 10px; background: #e74c3c; color: #fff;
	font-size: 0.9rem; font-weight: 600; cursor: pointer;
}
.confirm-ok:hover { background: #c0392b; }
</style>
