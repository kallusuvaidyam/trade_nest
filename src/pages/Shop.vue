<template>
	<div class="shop-page">
		<!-- Header -->
		<div class="shop-header">
			<div class="shop-header-inner">
				<div>
					<h1 class="shop-title">All Products</h1>
					<p class="shop-subtitle">{{ total }} items available</p>
				</div>
				<div class="search-box">
					<span class="search-icon">🔍</span>
					<input
						v-model="search"
						@input="onSearch"
						placeholder="Search products..."
						class="search-input"
					/>
				</div>
			</div>
		</div>

		<!-- Loading -->
		<div v-if="loading" class="loading-grid">
			<div v-for="n in 8" :key="n" class="skeleton-card">
				<div class="skeleton-img"></div>
				<div class="skeleton-line long"></div>
				<div class="skeleton-line short"></div>
				<div class="skeleton-btn"></div>
			</div>
		</div>

		<!-- Error -->
		<div v-else-if="error" class="error-state">
			<div class="error-icon">⚠️</div>
			<p>{{ error }}</p>
			<button @click="fetchItems" class="retry-btn">Retry</button>
		</div>

		<!-- Empty -->
		<div v-else-if="items.length === 0" class="empty-state">
			<div class="empty-icon">📦</div>
			<p>No products found</p>
		</div>

		<!-- Items Grid -->
		<div v-else class="items-grid">
			<div
				v-for="item in items"
				:key="item.item_code"
				class="item-card"
				:class="{ visible: visibleItems.has(item.item_code) }"
				:ref="el => observeCard(el, item.item_code)"
			>
				<!-- Image -->
				<div class="item-img-wrap" @click="openLightbox(item)">
					<img
						v-if="item.image && visibleItems.has(item.item_code)"
						:src="item.image"
						:alt="item.item_name"
						class="item-img"
						loading="lazy"
					/>
					<div v-else-if="!item.image" class="item-img-placeholder">
						<span>{{ item.item_name.charAt(0) }}</span>
					</div>
					<div v-else class="item-img-skeleton"></div>
					<div class="img-zoom-hint">🔍</div>
				</div>

				<!-- Info -->
				<div class="item-body">
					<div class="item-top-row">
						<span class="item-group">{{ item.item_group }}</span>
						<span v-if="item.avg_rating > 0" class="item-rating">★ {{ Number(item.avg_rating).toFixed(1) }}</span>
					</div>
					<h3 class="item-name">{{ item.item_name }}</h3>
					<p v-if="item.store_name || item.vendor_name" class="item-vendor">by {{ item.store_name || item.vendor_name }}</p>
					<p class="item-desc">{{ item.description ? item.description.replace(/<[^>]+>/g,'').slice(0,80) + '...' : 'Quality product' }}</p>
					<div class="item-price">
						<span v-if="item.price > 0">₹{{ Number(item.price).toLocaleString('en-IN') }}</span>
						<span v-else class="item-price-na">Price on request</span>
					</div>
					<div class="item-footer">
						<button class="buy-now-btn" @click="buyNow(item)">⚡ Buy Now</button>
						<button
							class="add-btn"
							:class="{ adding: addingItem === item.item_code }"
							@click="addToCart(item)"
						>
							<span v-if="addingItem === item.item_code">✓ Added!</span>
							<span v-else>Add to Cart</span>
						</button>
					</div>
				</div>
			</div>
		</div>

		<!-- Toast Notification -->
		<Teleport to="body">
			<transition name="toast">
				<div v-if="toast.show" class="toast-notification">
					<span class="toast-icon">🛒</span>
					<div>
						<div class="toast-title">Added to Cart!</div>
						<div class="toast-sub">{{ toast.name }}</div>
					</div>
					<button class="toast-close" @click="toast.show = false">✕</button>
				</div>
			</transition>
		</Teleport>

		<!-- Pagination -->
		<div v-if="totalPages > 1" class="pagination">
			<button @click="changePage(currentPage - 1)" :disabled="currentPage === 1" class="page-btn">‹</button>
			<span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
			<button @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages" class="page-btn">›</button>
		</div>

		<!-- Lightbox -->
		<Teleport to="body">
			<div v-if="lightbox.open" class="lightbox-overlay" @click.self="closeLightbox">
				<button class="lb-close" @click="closeLightbox">✕</button>
				<button class="lb-prev" @click="prevImage" v-if="lightboxIndex > 0">‹</button>
				<button class="lb-next" @click="nextImage" v-if="lightboxIndex < items.length - 1">
					›
				</button>
				<div class="lb-content">
					<div class="lb-img-wrap">
						<img
							v-if="lightbox.item.image"
							:src="lightbox.item.image"
							:alt="lightbox.item.item_name"
							class="lb-img"
						/>
						<div v-else class="lb-img-placeholder">
							{{ lightbox.item.item_name.charAt(0) }}
						</div>
					</div>
					<div class="lb-info">
						<div class="lb-badges">
							<span class="item-group">{{ lightbox.item.item_group }}</span>
							<span class="item-uom">📦 {{ lightbox.item.stock_uom }}</span>
						</div>
						<h2 class="lb-name">{{ lightbox.item.item_name }}</h2>
						<p class="lb-desc">
							{{ lightbox.item.description || "No description available" }}
						</p>
						<div class="lb-actions">
							<button class="buy-now-btn" @click="buyNow(lightbox.item); closeLightbox()">⚡ Buy Now</button>
							<button class="add-btn" @click="addToCart(lightbox.item); closeLightbox()">Add to Cart</button>
						</div>
					</div>
				</div>
				<div class="lb-counter">{{ lightboxIndex + 1 }} / {{ items.length }}</div>
			</div>
		</Teleport>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { api } from "@/api/frappe";
import { useCartStore } from "@/stores/cart";

const PAGE_SIZE = 12

const items = ref([]);
const loading = ref(true);
const error = ref(null);
const search = ref("");
const currentPage = ref(1);
const total = ref(0);
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)));
let searchTimer = null;

const cart = useCartStore();
const router = useRouter();

// Lazy loading
const visibleItems = ref(new Set());
let observer = null;
function observeCard(el, item_code) {
	if (!el || visibleItems.value.has(item_code)) return;
	if (!observer) {
		observer = new IntersectionObserver(
			(entries) => {
				entries.forEach((e) => {
					if (e.isIntersecting) {
						visibleItems.value = new Set([...visibleItems.value, e.target.dataset.code]);
						observer.unobserve(e.target);
					}
				});
			},
			{ rootMargin: "100px" }
		);
	}
	el.dataset.code = item_code;
	observer.observe(el);
}

// Toast
const toast = ref({ show: false, name: "" });
let toastTimer = null;
function showToast(name) {
	clearTimeout(toastTimer);
	toast.value = { show: true, name };
	toastTimer = setTimeout(() => (toast.value.show = false), 3000);
}

// Add to cart
const addingItem = ref(null);
function addToCart(item) {
	cart.addItem({
		item_code: item.item_code,
		item_name: item.item_name,
		vendor_item_id: item.vendor_item_id,
		vendor: item.vendor,
		price: item.price || item.custom_price || 0,
		image: item.image,
		item_group: item.item_group,
		stock_uom: item.stock_uom,
	});
	addingItem.value = item.item_code;
	setTimeout(() => (addingItem.value = null), 1200);
	showToast(item.item_name);
}

function buyNow(item) {
	cart.addItem({
		item_code: item.item_code,
		item_name: item.item_name,
		vendor_item_id: item.vendor_item_id,
		vendor: item.vendor,
		price: item.price || item.custom_price || 0,
		image: item.image,
	});
	router.push("/cart");
}

const lightbox = ref({ open: false, item: null });
const lightboxIndex = ref(0);

function openLightbox(item) {
	lightboxIndex.value = items.value.findIndex((i) => i.item_code === item.item_code);
	lightbox.value = { open: true, item };
	document.body.style.overflow = "hidden";
}
function closeLightbox() {
	lightbox.value = { open: false, item: null };
	document.body.style.overflow = "";
}
function prevImage() {
	if (lightboxIndex.value > 0) {
		lightboxIndex.value--;
		lightbox.value.item = items.value[lightboxIndex.value];
	}
}
function nextImage() {
	if (lightboxIndex.value < items.value.length - 1) {
		lightboxIndex.value++;
		lightbox.value.item = items.value[lightboxIndex.value];
	}
}
function onKeydown(e) {
	if (!lightbox.value.open) return;
	if (e.key === "Escape") closeLightbox();
	if (e.key === "ArrowLeft") prevImage();
	if (e.key === "ArrowRight") nextImage();
}
onMounted(() => document.addEventListener("keydown", onKeydown));
onUnmounted(() => document.removeEventListener("keydown", onKeydown));

async function fetchItems() {
	loading.value = true;
	error.value = null;
	try {
		const res = await api.getItems(currentPage.value, search.value, PAGE_SIZE);
		const data = res.message || {};
		items.value = Array.isArray(data) ? data : (data.items || []);
		total.value = data.total || items.value.length;
		// reset visible set on new page
		visibleItems.value = new Set();
	} catch (e) {
		error.value = e.message;
	} finally {
		loading.value = false;
	}
}

function changePage(p) {
	if (p < 1 || p > totalPages.value) return;
	currentPage.value = p;
	window.scrollTo({ top: 0, behavior: 'smooth' });
	fetchItems();
}

function onSearch() {
	clearTimeout(searchTimer);
	currentPage.value = 1;
	searchTimer = setTimeout(fetchItems, 400);
}

onMounted(fetchItems);
</script>

<style scoped>
.shop-page {
	min-height: 100vh;
	background: #f5f6fa;
	font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* Header */
.shop-header {
	background: #fff;
	border-bottom: 1px solid #e8eaed;
	padding: 1.25rem 2rem;
	position: sticky;
	top: 0;
	z-index: 10;
	box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}
.shop-header-inner {
	max-width: 1200px;
	margin: 0 auto;
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 1rem;
	flex-wrap: wrap;
}
.shop-title {
	font-size: 1.4rem;
	font-weight: 700;
	color: #1a1a2e;
	margin: 0;
}
.shop-subtitle {
	font-size: 0.8rem;
	color: #888;
	margin: 0.15rem 0 0;
}

/* Search */
.search-box {
	display: flex;
	align-items: center;
	background: #f5f6fa;
	border: 1.5px solid #e0e0e0;
	border-radius: 10px;
	padding: 0.45rem 1rem;
	gap: 0.5rem;
	min-width: 260px;
}
.search-box:focus-within {
	border-color: #5b4fcf;
	background: #fff;
}
.search-icon {
	font-size: 0.9rem;
}
.search-input {
	border: none;
	background: transparent;
	outline: none;
	font-size: 0.9rem;
	width: 100%;
	color: #333;
}

/* Grid */
.items-grid {
	max-width: 1200px;
	margin: 2rem auto;
	padding: 0 2rem 3rem;
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
	gap: 1.25rem;
}

/* Card */
.item-card {
	background: #fff;
	border-radius: 14px;
	overflow: hidden;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
	transition: transform 0.2s, box-shadow 0.2s, opacity 0.4s, translate 0.4s;
	cursor: pointer;
	display: flex;
	flex-direction: column;
	opacity: 0;
	translate: 0 20px;
}
.item-card.visible {
	opacity: 1;
	translate: 0 0;
}
.item-card:hover {
	transform: translateY(-4px);
	box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

/* Image */
.item-img-wrap {
	height: 160px;
	background: #f0f1f6;
	overflow: hidden;
}
.item-img {
	width: 100%;
	height: 100%;
	object-fit: cover;
}
.item-img-placeholder {
	width: 100%;
	height: 100%;
	display: flex;
	align-items: center;
	justify-content: center;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	font-size: 3rem;
	font-weight: 700;
	color: #fff;
	text-transform: uppercase;
}

/* Body */
.item-body {
	padding: 1rem;
	display: flex;
	flex-direction: column;
	flex: 1;
}
.item-top-row {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 0.4rem;
}
.item-group {
	font-size: 0.7rem;
	font-weight: 600;
	color: #5b4fcf;
	text-transform: uppercase;
	letter-spacing: 0.05em;
	background: #ede9ff;
	padding: 0.2rem 0.5rem;
	border-radius: 4px;
}
.item-rating {
	font-size: 0.72rem; font-weight: 700; color: #f39c12;
	background: #fff9e6; padding: 0.2rem 0.45rem; border-radius: 4px;
}
.item-vendor {
	font-size: 0.75rem; color: #888; margin: 0.1rem 0 0.25rem;
}
.item-name {
	font-size: 1rem;
	font-weight: 600;
	color: #1a1a2e;
	margin: 0.35rem 0;
	line-height: 1.3;
}
.item-desc {
	font-size: 0.82rem;
	color: #888;
	line-height: 1.5;
	display: -webkit-box;
	-webkit-line-clamp: 2;
	line-clamp: 2;
	-webkit-box-orient: vertical;
	overflow: hidden;
	margin-bottom: 0.5rem;
}
.item-price {
	font-size: 1.05rem;
	font-weight: 700;
	color: #5b4fcf;
	margin-bottom: 0.25rem;
	flex: 1;
}
.item-price-na {
	font-size: 0.78rem;
	color: #bbb;
	font-weight: 400;
}
.item-uom {
	font-size: 0.72rem;
	color: #999;
	background: #f5f6fa;
	padding: 0.18rem 0.45rem;
	border-radius: 4px;
}
.item-footer {
	display: flex;
	align-items: center;
	gap: 0.5rem;
	margin-top: 1rem;
}
.buy-now-btn {
	flex: 1;
	background: #fff;
	color: #5b4fcf;
	border: 1.5px solid #5b4fcf;
	padding: 0.45rem 0;
	border-radius: 8px;
	font-size: 0.82rem;
	font-weight: 700;
	cursor: pointer;
	transition:
		background 0.15s,
		color 0.15s;
}
.buy-now-btn:hover {
	background: #5b4fcf;
	color: #fff;
}
.add-btn {
	flex: 1;
	background: #5b4fcf;
	color: #fff;
	border: none;
	padding: 0.45rem 0;
	border-radius: 8px;
	font-size: 0.82rem;
	font-weight: 600;
	cursor: pointer;
	transition: background 0.2s;
}
.add-btn:hover { background: #4a3fbe; }
.add-btn.adding {
	background: #27ae60;
	transform: scale(0.97);
}

/* Lazy image skeleton */
.item-img-skeleton {
	width: 100%;
	height: 100%;
	background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
	background-size: 200% 100%;
	animation: shimmer 1.4s infinite;
}

/* Toast */
.toast-notification {
	position: fixed;
	bottom: 1.5rem;
	right: 1.5rem;
	background: #1a1a2e;
	color: #fff;
	border-radius: 14px;
	padding: 0.85rem 1.1rem;
	display: flex;
	align-items: center;
	gap: 0.75rem;
	box-shadow: 0 8px 30px rgba(0,0,0,0.25);
	z-index: 99999;
	min-width: 260px;
	max-width: 340px;
}
.toast-icon { font-size: 1.4rem; flex-shrink: 0; }
.toast-title { font-size: 0.88rem; font-weight: 700; }
.toast-sub {
	font-size: 0.78rem;
	color: #a78bfa;
	margin-top: 2px;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
	max-width: 200px;
}
.toast-close {
	background: none;
	border: none;
	color: #888;
	cursor: pointer;
	font-size: 0.9rem;
	margin-left: auto;
	flex-shrink: 0;
	padding: 0;
}
.toast-enter-active { animation: toast-in 0.3s ease; }
.toast-leave-active { animation: toast-in 0.25s ease reverse; }
@keyframes toast-in {
	from { opacity: 0; transform: translateY(16px) scale(0.95); }
	to   { opacity: 1; transform: translateY(0) scale(1); }
}

/* Skeleton */
.loading-grid {
	max-width: 1200px;
	margin: 2rem auto;
	padding: 0 2rem;
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
	gap: 1.25rem;
}
.skeleton-card {
	background: #fff;
	border-radius: 14px;
	overflow: hidden;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.skeleton-img {
	height: 160px;
	background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
	background-size: 200% 100%;
	animation: shimmer 1.4s infinite;
}
.skeleton-line {
	height: 14px;
	margin: 1rem 1rem 0.5rem;
	border-radius: 6px;
	background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
	background-size: 200% 100%;
	animation: shimmer 1.4s infinite;
}
.skeleton-line.long {
	width: 70%;
}
.skeleton-line.short {
	width: 45%;
}
.skeleton-btn {
	height: 34px;
	width: 90px;
	margin: 0.75rem 1rem 1rem auto;
	border-radius: 8px;
	background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
	background-size: 200% 100%;
	animation: shimmer 1.4s infinite;
}
@keyframes shimmer {
	0% {
		background-position: 200% 0;
	}
	100% {
		background-position: -200% 0;
	}
}

/* States */
.empty-state,
.error-state {
	text-align: center;
	padding: 5rem 2rem;
	color: #888;
}
.empty-icon,
.error-icon {
	font-size: 3rem;
	margin-bottom: 1rem;
}
.retry-btn {
	margin-top: 1rem;
	padding: 0.5rem 1.5rem;
	background: #5b4fcf;
	color: #fff;
	border: none;
	border-radius: 8px;
	cursor: pointer;
	font-size: 0.9rem;
}

@media (max-width: 600px) {
	.items-grid,
	.loading-grid {
		padding: 0 1rem 2rem;
	}
	.shop-header {
		padding: 1rem;
	}
	.search-box {
		min-width: 100%;
	}
}

/* Image zoom hint */
.item-img-wrap {
	position: relative;
	cursor: zoom-in;
}
.img-zoom-hint {
	position: absolute;
	bottom: 8px;
	right: 8px;
	background: rgba(0, 0, 0, 0.45);
	color: #fff;
	border-radius: 50%;
	width: 28px;
	height: 28px;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 0.75rem;
	opacity: 0;
	transition: opacity 0.2s;
}
.item-card:hover .img-zoom-hint {
	opacity: 1;
}

/* Lightbox */
.lightbox-overlay {
	position: fixed;
	inset: 0;
	background: rgba(10, 10, 20, 0.92);
	z-index: 9999;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 1.5rem;
	animation: lb-fade 0.2s ease;
}
@keyframes lb-fade {
	from {
		opacity: 0;
	}
	to {
		opacity: 1;
	}
}
.lb-content {
	background: #fff;
	border-radius: 18px;
	overflow: hidden;
	max-width: 860px;
	width: 100%;
	display: flex;
	max-height: 90vh;
	animation: lb-up 0.25s ease;
}
@keyframes lb-up {
	from {
		transform: translateY(30px);
		opacity: 0;
	}
	to {
		transform: translateY(0);
		opacity: 1;
	}
}
.lb-img-wrap {
	flex: 0 0 420px;
	background: #f0f1f6;
	display: flex;
	align-items: center;
	justify-content: center;
	min-height: 340px;
}
.lb-img {
	width: 100%;
	height: 100%;
	object-fit: cover;
	display: block;
}
.lb-img-placeholder {
	font-size: 5rem;
	font-weight: 800;
	color: #fff;
	background: linear-gradient(135deg, #667eea, #764ba2);
	width: 100%;
	height: 100%;
	display: flex;
	align-items: center;
	justify-content: center;
	text-transform: uppercase;
	min-height: 340px;
}
.lb-info {
	padding: 2rem;
	display: flex;
	flex-direction: column;
	flex: 1;
	overflow-y: auto;
}
.lb-badges {
	display: flex;
	align-items: center;
	gap: 0.5rem;
	margin-bottom: 0.75rem;
}
.lb-name {
	font-size: 1.4rem;
	font-weight: 700;
	color: #1a1a2e;
	margin: 0 0 0.75rem;
	line-height: 1.3;
}
.lb-desc {
	font-size: 0.88rem;
	color: #666;
	line-height: 1.7;
	flex: 1;
	margin-bottom: 1.5rem;
}
.lb-actions {
	display: flex;
	gap: 0.75rem;
}
.lb-close {
	position: fixed;
	top: 1.25rem;
	right: 1.5rem;
	background: rgba(255, 255, 255, 0.15);
	border: none;
	color: #fff;
	font-size: 1.25rem;
	width: 40px;
	height: 40px;
	border-radius: 50%;
	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: background 0.2s;
	z-index: 10000;
}
.lb-close:hover {
	background: rgba(255, 255, 255, 0.3);
}
.lb-prev,
.lb-next {
	position: fixed;
	top: 50%;
	transform: translateY(-50%);
	background: rgba(255, 255, 255, 0.15);
	border: none;
	color: #fff;
	font-size: 2rem;
	width: 46px;
	height: 46px;
	border-radius: 50%;
	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: background 0.2s;
	z-index: 10000;
}
.lb-prev {
	left: 1rem;
}
.lb-next {
	right: 1rem;
}
.lb-prev:hover,
.lb-next:hover {
	background: rgba(255, 255, 255, 0.3);
}
.lb-counter {
	position: fixed;
	bottom: 1.25rem;
	left: 50%;
	transform: translateX(-50%);
	color: rgba(255, 255, 255, 0.6);
	font-size: 0.85rem;
}
@media (max-width: 680px) {
	.lb-content {
		flex-direction: column;
	}
	.lb-img-wrap {
		flex: 0 0 220px;
		min-height: 220px;
	}
	.lb-img-placeholder {
		min-height: 220px;
	}
}

.pagination {
	display: flex; align-items: center; justify-content: center;
	gap: 1rem; padding: 2rem 0;
}
.page-btn {
	background: #fff; border: 1px solid #ddd; border-radius: 8px;
	width: 36px; height: 36px; font-size: 1.2rem; cursor: pointer;
	display: flex; align-items: center; justify-content: center;
	transition: background 0.15s;
}
.page-btn:disabled { opacity: 0.35; cursor: not-allowed; }
.page-btn:not(:disabled):hover { background: #f0eeff; }
.page-info { font-size: 0.9rem; color: #555; font-weight: 600; }
</style>
