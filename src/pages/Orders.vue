<template>
  <div class="orders-page">
    <div class="orders-container">

      <h1 class="orders-title">📦 My Orders</h1>

      <!-- Loading -->
      <div v-if="loading" class="orders-loading">
        <div v-for="n in 3" :key="n" class="order-skeleton">
          <div class="sk-header"></div>
          <div class="sk-body"></div>
        </div>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="orders-error">
        <div class="err-icon">⚠️</div>
        <p>{{ error }}</p>
        <button @click="fetchOrders" class="retry-btn">Retry</button>
      </div>

      <!-- Empty -->
      <div v-else-if="orders.length === 0" class="orders-empty">
        <div class="empty-icon">🛍️</div>
        <p>Koi order nahi mila</p>
        <RouterLink to="/items" class="browse-btn">Shopping Karein</RouterLink>
      </div>

      <!-- Orders List -->
      <div v-else class="orders-list">
        <div
          v-for="order in orders"
          :key="order.name"
          class="order-card"
          @click="toggleOrder(order.name)"
        >
          <!-- Order Header -->
          <div class="order-header">
            <div class="order-meta">
              <span class="order-id">{{ order.name }}</span>
              <span :class="['status-badge', statusClass(order.status)]">
                {{ statusLabel(order.status) }}
              </span>
              <span :class="['pay-badge', order.payment_status === 'Paid' ? 'paid' : 'unpaid']">
                {{ order.payment_status === 'Paid' ? '✓ Paid' : (order.payment_method === 'COD' ? '💵 COD' : '⏳ Pending') }}
              </span>
            </div>
            <div class="order-right">
              <span class="order-total" v-if="order.grand_total > 0">
                ₹{{ Number(order.grand_total).toLocaleString('en-IN') }}
              </span>
              <span class="order-date">{{ formatDate(order.transaction_date) }}</span>
              <span class="order-chevron" :class="{ open: expanded === order.name }">▾</span>
            </div>
          </div>

          <!-- Status Timeline -->
          <div class="order-timeline">
            <div
              v-for="(step, i) in getTimeline(order)"
              :key="i"
              :class="['timeline-step', step.done ? 'done' : '', step.active ? 'active' : '']"
            >
              <div class="tl-dot">
                <svg v-if="step.done" width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <circle cx="7" cy="7" r="7" fill="#27ae60"/>
                  <path d="M4 7l2 2 4-4" stroke="#fff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <div v-else class="tl-dot-inner"></div>
              </div>
              <div class="tl-line" v-if="i < getTimeline(order).length - 1"></div>
              <span class="tl-label">{{ step.label }}</span>
            </div>
          </div>

          <!-- Expanded Items -->
          <transition name="expand">
            <div v-show="expanded === order.name" class="order-items">
              <div v-for="item in order.items" :key="item.item_code + (item.vendor || '')" class="oi-row">
                <img v-if="item.image" :src="item.image" class="oi-img" />
                <div v-else class="oi-img-ph">{{ (item.item_name || '?').charAt(0) }}</div>
                <div class="oi-info">
                  <span class="oi-name">{{ item.item_name }}</span>
                  <span class="oi-vendor" v-if="item.vendor_name">by {{ item.vendor_name }}</span>
                </div>
                <span class="oi-qty">× {{ item.qty }}</span>
                <span class="oi-amount">
                  {{ item.rate > 0 ? '₹' + Number(item.amount).toLocaleString('en-IN') : '—' }}
                </span>
              </div>
              <div class="oi-footer">
                <span>Expected: {{ formatDate(order.expected_delivery_date) }}</span>
                <span class="oi-total" v-if="order.grand_total > 0">
                  Total: ₹{{ Number(order.grand_total).toLocaleString('en-IN') }}
                </span>
              </div>
              <!-- Cancel button -->
              <div v-if="['Placed', 'Processing'].includes(order.status)" class="oi-cancel-row">
                <button @click.stop="cancelOrder(order)" class="cancel-order-btn" :disabled="cancelling === order.name">
                  {{ cancelling === order.name ? 'Cancelling...' : 'Cancel Order' }}
                </button>
              </div>
            </div>
          </transition>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
        <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1" class="page-btn">‹</button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages" class="page-btn">›</button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '@/api/frappe'

const PAGE_SIZE = 10

const orders = ref([])
const loading = ref(true)
const error = ref('')
const expanded = ref(null)
const currentPage = ref(1)
const total = ref(0)
const cancelling = ref(null)
const totalPages = computed(() => Math.ceil(total.value / PAGE_SIZE))

async function fetchOrders() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.getOrders(currentPage.value, PAGE_SIZE)
    const data = res.message || {}
    orders.value = data.orders || []
    total.value = data.total || 0
  } catch (e) {
    error.value = e.message || 'Orders load karne mein error'
  } finally {
    loading.value = false
  }
}

function changePage(p) {
  if (p < 1 || p > totalPages.value) return
  currentPage.value = p
  expanded.value = null
  fetchOrders()
}

function toggleOrder(name) {
  expanded.value = expanded.value === name ? null : name
}

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
}

function statusLabel(status) {
  const map = {
    'Draft': 'Draft',
    'Placed': 'Placed',
    'Processing': 'Processing',
    'Shipped': 'Shipped',
    'Delivered': 'Delivered',
    'Cancelled': 'Cancelled',
    'Refunded': 'Refunded',
  }
  return map[status] || status
}

function statusClass(status) {
  if (status === 'Delivered') return 'green'
  if (['Cancelled', 'Refunded'].includes(status)) return 'red'
  if (['Shipped', 'Processing'].includes(status)) return 'blue'
  return 'orange'
}

function getTimeline(order) {
  const status = order.status
  const statusOrder = ['Placed', 'Processing', 'Shipped', 'Delivered']
  const idx = statusOrder.indexOf(status)
  const steps = [
    { label: 'Placed',     done: idx >= 0 },
    { label: 'Processing', done: idx >= 1 },
    { label: 'Shipped',    done: idx >= 2 },
    { label: 'Delivered',  done: idx >= 3 },
  ]
  const firstPending = steps.findIndex(s => !s.done)
  if (firstPending > -1) steps[firstPending].active = true
  return steps
}

async function cancelOrder(order) {
  if (!confirm(`Order ${order.name} cancel karna chahte hain?`)) return
  cancelling.value = order.name
  try {
    await api.cancelOrder(order.name, 'Customer request')
    order.status = 'Cancelled'
  } catch (e) {
    alert('Cancel failed: ' + e.message)
  } finally {
    cancelling.value = null
  }
}

onMounted(fetchOrders)
</script>

<style scoped>
.orders-page {
  min-height: 100vh; background: #f5f6fa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  padding: 2rem 1.5rem 4rem;
}
.orders-container { max-width: 820px; margin: 0 auto; }
.orders-title { font-size: 1.5rem; font-weight: 800; color: #1a1a2e; margin: 0 0 1.5rem; }

/* Skeleton */
.orders-loading { display: flex; flex-direction: column; gap: 1rem; }
.order-skeleton { background: #fff; border-radius: 14px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.sk-header {
  height: 56px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
  background-size: 200% 100%; animation: shimmer 1.4s infinite;
}
.sk-body {
  height: 36px; margin: 1rem;
  background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
  background-size: 200% 100%; animation: shimmer 1.4s infinite;
  border-radius: 6px;
}
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

/* Error / Empty */
.orders-error, .orders-empty {
  text-align: center; padding: 4rem 2rem;
  background: #fff; border-radius: 18px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.err-icon, .empty-icon { font-size: 3rem; margin-bottom: 0.75rem; }
.orders-error p, .orders-empty p { color: #888; margin-bottom: 1.25rem; }
.retry-btn, .browse-btn {
  display: inline-block; padding: 0.6rem 1.5rem; border-radius: 10px;
  font-weight: 600; font-size: 0.9rem; cursor: pointer; text-decoration: none;
  background: linear-gradient(135deg, #5b4fcf, #764ba2); color: #fff; border: none;
}

/* Orders List */
.orders-list { display: flex; flex-direction: column; gap: 1rem; }
.order-card {
  background: #fff; border-radius: 14px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  overflow: hidden; cursor: pointer;
  transition: box-shadow 0.2s, transform 0.15s;
  will-change: transform;
}
.order-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.1); }

/* Header */
.order-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 1.25rem; gap: 1rem; flex-wrap: wrap;
}
.order-meta { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.order-id { font-size: 0.85rem; font-weight: 700; color: #1a1a2e; }
.status-badge {
  font-size: 0.72rem; font-weight: 700; padding: 0.2rem 0.55rem; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.04em;
}
.status-badge.green  { background: #e8f8f0; color: #27ae60; }
.status-badge.blue   { background: #e8f0ff; color: #3b82f6; }
.status-badge.orange { background: #fff7e6; color: #e67e22; }
.status-badge.red    { background: #fff0f0; color: #e74c3c; }

.pay-badge {
  font-size: 0.72rem; font-weight: 600; padding: 0.2rem 0.5rem; border-radius: 20px;
}
.pay-badge.paid   { background: #e8f8f0; color: #27ae60; }
.pay-badge.unpaid { background: #f5f6fa; color: #888; }

.order-right { display: flex; align-items: center; gap: 0.75rem; flex-shrink: 0; }
.order-total { font-size: 0.95rem; font-weight: 700; color: #5b4fcf; }
.order-date { font-size: 0.78rem; color: #aaa; }
.order-chevron { font-size: 0.85rem; color: #aaa; transition: transform 0.2s; }
.order-chevron.open { transform: rotate(180deg); }

/* Timeline */
.order-timeline {
  display: flex; align-items: flex-start;
  padding: 0 1.25rem 1rem; gap: 0; position: relative;
}
.timeline-step {
  display: flex; flex-direction: column; align-items: center;
  flex: 1; position: relative;
}
.tl-dot {
  width: 22px; height: 22px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  background: #f0f0f0; z-index: 1; flex-shrink: 0;
}
.timeline-step.done .tl-dot { background: transparent; }
.timeline-step.active .tl-dot-inner {
  width: 12px; height: 12px; border-radius: 50%;
  background: #5b4fcf; animation: pulse 1.5s infinite;
}
.tl-dot-inner { width: 10px; height: 10px; border-radius: 50%; background: #ddd; }
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(91,79,207,0.4); }
  50% { box-shadow: 0 0 0 5px rgba(91,79,207,0); }
}
.tl-line {
  position: absolute; top: 11px; left: 50%; width: 100%;
  height: 2px; background: #e8e8e8; z-index: 0;
}
.timeline-step.done .tl-line { background: #27ae60; }
.tl-label {
  font-size: 0.68rem; color: #aaa; margin-top: 0.35rem; text-align: center;
  white-space: nowrap;
}
.timeline-step.done .tl-label { color: #27ae60; font-weight: 600; }
.timeline-step.active .tl-label { color: #5b4fcf; font-weight: 600; }

/* Expanded items */
.order-items {
  border-top: 1px solid #f0f0f0;
  padding: 0.85rem 1.25rem 1rem;
}
.oi-row {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.4rem 0; border-bottom: 1px dashed #f5f5f5; font-size: 0.85rem;
}
.oi-img { width: 40px; height: 40px; border-radius: 8px; object-fit: cover; flex-shrink: 0; }
.oi-img-ph {
  width: 40px; height: 40px; border-radius: 8px; flex-shrink: 0;
  background: linear-gradient(135deg, #667eea, #764ba2); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 1rem;
}
.oi-info { flex: 1; min-width: 0; }
.oi-name { display: block; color: #333; font-weight: 500; font-size: 0.85rem; }
.oi-vendor { font-size: 0.72rem; color: #888; }
.oi-qty { color: #888; font-size: 0.8rem; white-space: nowrap; }
.oi-amount { font-weight: 700; color: #5b4fcf; font-size: 0.88rem; white-space: nowrap; }
.oi-cancel-row { margin-top: 0.75rem; text-align: right; }
.cancel-order-btn {
  padding: 0.45rem 1rem; border: 1.5px solid #e74c3c; border-radius: 8px;
  background: none; color: #e74c3c; font-size: 0.82rem; font-weight: 600;
  cursor: pointer; transition: background 0.15s, color 0.15s;
}
.cancel-order-btn:hover:not(:disabled) { background: #e74c3c; color: #fff; }
.cancel-order-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.oi-footer {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 0.75rem; font-size: 0.8rem; color: #aaa;
}
.oi-total { font-size: 0.95rem; font-weight: 800; color: #1a1a2e; }

/* Expand animation */
.expand-enter-active {
  transition: grid-template-rows 0.28s ease, opacity 0.28s ease;
  display: grid;
  grid-template-rows: 1fr;
}
.expand-leave-active {
  transition: grid-template-rows 0.22s ease, opacity 0.22s ease;
  display: grid;
  grid-template-rows: 1fr;
}
.expand-enter-from,
.expand-leave-to {
  grid-template-rows: 0fr;
  opacity: 0;
}
.order-items {
  overflow: hidden;
}

@media (max-width: 600px) {
  .order-header { flex-direction: column; align-items: flex-start; }
  .order-right { width: 100%; justify-content: space-between; }
}

.pagination {
  display: flex; align-items: center; justify-content: center;
  gap: 1rem; margin-top: 1.5rem;
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
