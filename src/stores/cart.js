import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

const STORAGE_KEY = 'tradenest_cart'

function loadFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

export const useCartStore = defineStore('cart', () => {
  const items = ref(loadFromStorage())

  // Persist to localStorage on every change
  watch(items, (val) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(val))
  }, { deep: true })

  const hasPrice = computed(() => items.value.some(i => i.price > 0))

  const total = computed(() =>
    items.value.reduce((sum, i) => sum + (i.price || 0) * i.qty, 0)
  )

  function addItem(item) {
    const existing = items.value.find(i => i.item_code === item.item_code)
    if (existing) existing.qty++
    else items.value.push({ ...item, qty: 1 })
  }

  function removeItem(item_code) {
    items.value = items.value.filter(i => i.item_code !== item_code)
  }

  function incQty(item_code) {
    const item = items.value.find(i => i.item_code === item_code)
    if (item) item.qty++
  }

  function decQty(item_code) {
    const item = items.value.find(i => i.item_code === item_code)
    if (!item) return
    if (item.qty <= 1) removeItem(item_code)
    else item.qty--
  }

  function clearCart() {
    items.value = []
  }

  return { items, total, hasPrice, addItem, removeItem, incQty, decQty, clearCart }
})
