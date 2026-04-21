<template>
  <div class="pd-page">
    <button class="back-btn" @click="$router.back()">← Back</button>

    <div v-if="loading" class="pd-skeleton">
      <div class="sk-img"></div>
      <div class="sk-body">
        <div class="sk-line long"></div>
        <div class="sk-line short"></div>
        <div class="sk-line medium"></div>
      </div>
    </div>

    <div v-else-if="error" class="pd-error">
      <p>⚠️ {{ error }}</p>
      <button @click="fetchItem" class="retry-btn">Retry</button>
    </div>

    <div v-else-if="item" class="pd-layout">
      <!-- Left: Image -->
      <div class="pd-img-col">
        <div class="pd-img-wrap">
          <img v-if="item.image" :src="item.image" :alt="item.item_name" class="pd-img" @click="lightbox = true" />
          <div v-else class="pd-img-placeholder">{{ (item.item_name || '?').charAt(0) }}</div>
          <div v-if="item.image" class="pd-img-zoom" @click="lightbox = true">🔍 View</div>
        </div>

        <div v-if="item.vendor_name" class="vendor-card">
          <img v-if="item.store_logo" :src="item.store_logo" class="vendor-logo" />
          <div v-else class="vendor-logo-ph">{{ (item.vendor_name || 'V').charAt(0) }}</div>
          <div class="vendor-info">
            <div class="vendor-store">{{ item.store_name || item.vendor_name }}</div>
            <div class="vendor-label">Official Store</div>
          </div>
        </div>
      </div>

      <!-- Right: Info -->
      <div class="pd-info-col">
        <div class="pd-badges">
          <span v-if="item.item_group" class="pd-cat">{{ item.item_group }}</span>
          <span v-if="item.stock_qty > 0" class="pd-instock">In Stock ({{ item.stock_qty }})</span>
          <span v-else-if="item.stock_qty === 0" class="pd-outstock">Out of Stock</span>
        </div>

        <h1 class="pd-title">{{ item.item_name }}</h1>

        <div class="pd-rating" v-if="item.avg_rating > 0">
          <span class="stars">{{ '★'.repeat(Math.round(item.avg_rating)) }}{{ '☆'.repeat(5 - Math.round(item.avg_rating)) }}</span>
          <span class="rating-val">{{ item.avg_rating.toFixed(1) }}</span>
          <span class="rating-count">({{ item.review_count || 0 }} reviews)</span>
        </div>

        <div class="pd-price">
          <span v-if="item.price > 0">₹{{ Number(item.price).toLocaleString('en-IN') }}</span>
          <span v-else class="pd-price-na">Price on request</span>
        </div>

        <div class="pd-desc" v-if="item.description" v-html="item.description"></div>

        <div class="pd-qty-row">
          <label class="pd-qty-label">Qty:</label>
          <div class="qty-control">
            <button @click="qty > 1 ? qty-- : null" class="qty-btn">−</button>
            <span class="qty-val">{{ qty }}</span>
            <button @click="qty++" class="qty-btn">+</button>
          </div>
        </div>

        <div class="pd-actions">
          <button class="add-cart-btn" @click="addToCart">🛒 Add to Cart</button>
          <button class="buy-now-btn" @click="buyNow">⚡ Buy Now</button>
        </div>

        <div v-if="addedMsg" class="added-toast">✓ {{ addedMsg }}</div>
      </div>
    </div>

    <!-- Reviews -->
    <div v-if="item && !loading" class="reviews-section">
      <h2 class="reviews-title">Customer Reviews</h2>

      <div class="write-review">
        <h3 class="wr-title">Write a Review</h3>
        <div class="star-picker">
          <button v-for="n in 5" :key="n" @click="review.rating = n"
            :class="['star-btn', n <= review.rating ? 'filled' : '']">★</button>
        </div>
        <input v-model="review.title" placeholder="Review title" class="wr-input" />
        <textarea v-model="review.text" placeholder="Share your experience..." class="wr-textarea" rows="3"></textarea>
        <button @click="submitReview" :disabled="submittingReview || !review.rating" class="wr-submit">
          {{ submittingReview ? 'Submitting...' : 'Submit Review' }}
        </button>
        <p v-if="reviewMsg" class="review-msg">{{ reviewMsg }}</p>
      </div>

      <div v-if="reviews.length === 0" class="no-reviews">No reviews yet. Be the first!</div>
      <div v-else class="reviews-list">
        <div v-for="r in reviews" :key="r.creation" class="review-card">
          <div class="review-header">
            <div class="reviewer-avatar">{{ (r.customer_name || '?').charAt(0) }}</div>
            <div class="reviewer-info">
              <span class="reviewer-name">{{ r.customer_name }}</span>
              <span v-if="r.is_verified_purchase" class="verified-badge">✓ Verified</span>
            </div>
            <div class="review-rating">{{ '★'.repeat(r.rating) }}{{ '☆'.repeat(5 - r.rating) }}</div>
          </div>
          <p v-if="r.title" class="review-title-text">{{ r.title }}</p>
          <p class="review-text">{{ r.review_text }}</p>
          <span class="review-date">{{ formatDate(r.creation) }}</span>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="lightbox" class="lightbox" @click="lightbox = false">
        <img v-if="item.image" :src="item.image" class="lb-img" />
        <button class="lb-close" @click="lightbox = false">✕</button>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api/frappe'
import { useCartStore } from '@/stores/cart'

const route = useRoute()
const router = useRouter()
const cart = useCartStore()

const item = ref(null)
const loading = ref(true)
const error = ref('')
const qty = ref(1)
const lightbox = ref(false)
const addedMsg = ref('')
const reviews = ref([])
const submittingReview = ref(false)
const reviewMsg = ref('')
const review = ref({ rating: 0, title: '', text: '' })

async function fetchItem() {
  loading.value = true; error.value = ''
  try {
    const res = await api.getItem(route.params.id, route.query.vendor || '')
    item.value = res.message
    const rRes = await api.getReviews(route.params.id)
    reviews.value = (rRes.message || {}).reviews || []
  } catch (e) { error.value = e.message || 'Product load failed' }
  finally { loading.value = false }
}

function addToCart() {
  if (!item.value) return
  for (let i = 0; i < qty.value; i++) {
    cart.addItem({
      item_code: item.value.item_code,
      item_name: item.value.item_name,
      vendor_item_id: item.value.vendor_item_id,
      vendor: item.value.vendor,
      price: item.value.price || 0,
      image: item.value.image,
    })
  }
  addedMsg.value = `${item.value.item_name} (×${qty.value}) cart mein add!`
  setTimeout(() => addedMsg.value = '', 3000)
}

function buyNow() { addToCart(); router.push('/cart') }

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
}

async function submitReview() {
  if (!review.value.rating) return
  submittingReview.value = true; reviewMsg.value = ''
  try {
    await api.submitReview({
      item_code: item.value.item_code,
      order: '',
      rating: review.value.rating,
      title: review.value.title,
      review_text: review.value.text,
    })
    reviewMsg.value = '✓ Review submit ho gaya! Approval ke baad dikhega.'
    review.value = { rating: 0, title: '', text: '' }
  } catch (e) { reviewMsg.value = 'Error: ' + e.message }
  finally { submittingReview.value = false }
}

onMounted(fetchItem)
</script>

<style scoped>
.pd-page { min-height:100vh; background:#f5f6fa; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; padding:1.5rem 1.5rem 4rem; max-width:1100px; margin:0 auto; }
.back-btn { background:none; border:none; color:#5b4fcf; font-size:0.9rem; font-weight:600; cursor:pointer; padding:0 0 1rem; display:block; }
.back-btn:hover { text-decoration:underline; }

.pd-skeleton { display:flex; gap:2rem; }
.sk-img { width:400px; height:400px; border-radius:18px; background:linear-gradient(90deg,#f0f0f0 25%,#e8e8e8 50%,#f0f0f0 75%); background-size:200% 100%; animation:shimmer 1.4s infinite; flex-shrink:0; }
.sk-body { flex:1; display:flex; flex-direction:column; gap:1rem; padding-top:1rem; }
.sk-line { height:18px; border-radius:6px; background:linear-gradient(90deg,#f0f0f0 25%,#e8e8e8 50%,#f0f0f0 75%); background-size:200% 100%; animation:shimmer 1.4s infinite; }
.sk-line.long{width:80%}.sk-line.short{width:40%}.sk-line.medium{width:60%}
@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}

.pd-error { text-align:center; padding:4rem; }
.retry-btn { padding:0.6rem 1.5rem; background:linear-gradient(135deg,#5b4fcf,#764ba2); color:#fff; border:none; border-radius:10px; cursor:pointer; font-weight:600; }

.pd-layout { display:grid; grid-template-columns:1fr 1fr; gap:2.5rem; align-items:start; }
.pd-img-col { position:sticky; top:80px; }
.pd-img-wrap { border-radius:18px; overflow:hidden; background:#fff; box-shadow:0 4px 20px rgba(0,0,0,0.08); cursor:zoom-in; position:relative; }
.pd-img { width:100%; max-height:420px; object-fit:cover; display:block; }
.pd-img-placeholder { width:100%; height:360px; display:flex; align-items:center; justify-content:center; background:linear-gradient(135deg,#667eea,#764ba2); color:#fff; font-size:5rem; font-weight:800; }
.pd-img-zoom { position:absolute; bottom:0.75rem; right:0.75rem; background:rgba(0,0,0,0.55); color:#fff; font-size:0.75rem; padding:0.3rem 0.65rem; border-radius:8px; }

.vendor-card { margin-top:1rem; background:#fff; border-radius:14px; box-shadow:0 2px 8px rgba(0,0,0,0.06); padding:1rem; display:flex; align-items:center; gap:0.75rem; }
.vendor-logo { width:44px; height:44px; border-radius:10px; object-fit:cover; }
.vendor-logo-ph { width:44px; height:44px; border-radius:10px; background:linear-gradient(135deg,#5b4fcf,#764ba2); color:#fff; display:flex; align-items:center; justify-content:center; font-size:1.2rem; font-weight:800; flex-shrink:0; }
.vendor-store { font-weight:700; font-size:0.9rem; color:#1a1a2e; }
.vendor-label { font-size:0.72rem; color:#888; }

.pd-badges { display:flex; gap:0.5rem; flex-wrap:wrap; margin-bottom:0.75rem; }
.pd-cat { background:#ede9ff; color:#5b4fcf; font-size:0.72rem; font-weight:700; padding:0.2rem 0.6rem; border-radius:6px; text-transform:uppercase; }
.pd-instock { background:#e8f8f0; color:#27ae60; font-size:0.72rem; font-weight:700; padding:0.2rem 0.6rem; border-radius:6px; }
.pd-outstock { background:#fff0f0; color:#e74c3c; font-size:0.72rem; font-weight:700; padding:0.2rem 0.6rem; border-radius:6px; }
.pd-title { font-size:1.6rem; font-weight:800; color:#1a1a2e; margin:0 0 0.75rem; line-height:1.3; }
.pd-rating { display:flex; align-items:center; gap:0.4rem; margin-bottom:0.75rem; }
.stars { color:#f39c12; font-size:1.1rem; }
.rating-val { font-weight:700; color:#1a1a2e; }
.rating-count { font-size:0.8rem; color:#888; }
.pd-price { font-size:2rem; font-weight:800; color:#5b4fcf; margin-bottom:1rem; }
.pd-price-na { font-size:1rem; color:#bbb; font-weight:400; }
.pd-desc { font-size:0.88rem; color:#555; line-height:1.6; margin-bottom:1.25rem; }

.pd-qty-row { display:flex; align-items:center; gap:1rem; margin-bottom:1.25rem; }
.pd-qty-label { font-size:0.9rem; font-weight:600; color:#555; }
.qty-control { display:flex; align-items:center; gap:0.5rem; background:#f5f6fa; border-radius:10px; padding:0.3rem 0.5rem; }
.qty-btn { background:none; border:none; font-size:1.2rem; cursor:pointer; color:#5b4fcf; font-weight:700; width:28px; height:28px; display:flex; align-items:center; justify-content:center; border-radius:6px; }
.qty-btn:hover { background:#ede9ff; }
.qty-val { font-weight:700; min-width:28px; text-align:center; }

.pd-actions { display:flex; gap:0.75rem; margin-bottom:1rem; }
.add-cart-btn,.buy-now-btn { flex:1; padding:0.85rem; border:none; border-radius:12px; font-size:0.95rem; font-weight:700; cursor:pointer; transition:opacity 0.2s; }
.add-cart-btn { background:#f0eeff; color:#5b4fcf; }
.buy-now-btn { background:linear-gradient(135deg,#5b4fcf,#764ba2); color:#fff; }
.add-cart-btn:hover,.buy-now-btn:hover { opacity:0.85; }
.added-toast { background:#e8f8f0; color:#27ae60; padding:0.5rem 1rem; border-radius:8px; font-size:0.85rem; font-weight:600; }

.reviews-section { margin-top:3rem; }
.reviews-title { font-size:1.2rem; font-weight:800; color:#1a1a2e; margin-bottom:1.5rem; }
.write-review { background:#fff; border-radius:16px; box-shadow:0 2px 10px rgba(0,0,0,0.07); padding:1.5rem; margin-bottom:1.5rem; }
.wr-title { font-size:1rem; font-weight:700; margin:0 0 1rem; color:#1a1a2e; }
.star-picker { display:flex; gap:0.25rem; margin-bottom:0.75rem; }
.star-btn { background:none; border:none; font-size:1.8rem; cursor:pointer; color:#ddd; transition:color 0.15s; padding:0; }
.star-btn.filled { color:#f39c12; }
.wr-input { width:100%; box-sizing:border-box; border:1.5px solid #e8eaed; border-radius:10px; padding:0.65rem 0.85rem; font-size:0.88rem; margin-bottom:0.75rem; font-family:inherit; }
.wr-textarea { width:100%; box-sizing:border-box; border:1.5px solid #e8eaed; border-radius:10px; padding:0.65rem 0.85rem; font-size:0.88rem; margin-bottom:0.75rem; font-family:inherit; resize:vertical; }
.wr-input:focus,.wr-textarea:focus { outline:none; border-color:#5b4fcf; }
.wr-submit { padding:0.65rem 1.5rem; background:linear-gradient(135deg,#5b4fcf,#764ba2); color:#fff; border:none; border-radius:10px; font-size:0.9rem; font-weight:700; cursor:pointer; }
.wr-submit:disabled { opacity:0.5; cursor:not-allowed; }
.review-msg { margin-top:0.75rem; font-size:0.85rem; color:#27ae60; }
.no-reviews { text-align:center; color:#aaa; padding:2rem; background:#fff; border-radius:14px; }
.reviews-list { display:flex; flex-direction:column; gap:1rem; }
.review-card { background:#fff; border-radius:14px; box-shadow:0 2px 8px rgba(0,0,0,0.06); padding:1.25rem; }
.review-header { display:flex; align-items:center; gap:0.75rem; margin-bottom:0.5rem; }
.reviewer-avatar { width:36px; height:36px; border-radius:50%; background:linear-gradient(135deg,#5b4fcf,#764ba2); color:#fff; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:0.95rem; flex-shrink:0; }
.reviewer-info { flex:1; }
.reviewer-name { font-weight:700; font-size:0.88rem; color:#1a1a2e; display:block; }
.verified-badge { font-size:0.7rem; color:#27ae60; font-weight:600; background:#e8f8f0; padding:0.1rem 0.4rem; border-radius:4px; }
.review-rating { color:#f39c12; font-size:0.95rem; }
.review-title-text { font-weight:700; font-size:0.88rem; color:#1a1a2e; margin:0 0 0.35rem; }
.review-text { font-size:0.85rem; color:#555; line-height:1.55; margin:0 0 0.35rem; }
.review-date { font-size:0.72rem; color:#aaa; }

.lightbox { position:fixed; inset:0; background:rgba(0,0,0,0.88); z-index:9999; display:flex; align-items:center; justify-content:center; }
.lb-img { max-width:90vw; max-height:90vh; border-radius:12px; object-fit:contain; }
.lb-close { position:fixed; top:1.25rem; right:1.25rem; background:rgba(255,255,255,0.15); border:none; color:#fff; font-size:1.3rem; width:40px; height:40px; border-radius:50%; cursor:pointer; display:flex; align-items:center; justify-content:center; }

@media(max-width:700px) {
  .pd-layout { grid-template-columns:1fr; }
  .pd-img-col { position:static; }
}
</style>
