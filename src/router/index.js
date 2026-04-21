import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '@/pages/Home.vue'
import Login from '@/pages/Login.vue'
import Signup from '@/pages/Signup.vue'
import Shop from '@/pages/Shop.vue'
import ProductDetail from '@/pages/ProductDetail.vue'
import Cart from '@/pages/Cart.vue'
import Orders from '@/pages/Orders.vue'
import PrivacyPolicy from '@/pages/PrivacyPolicy.vue'
import VendorRegister from '@/pages/VendorRegister.vue'
import Profile from '@/pages/Profile.vue'
import { api } from '@/api/frappe'

const routes = [
  { path: '/', component: Home },
  { path: '/login', component: Login, meta: { guestOnly: true } },
  { path: '/signup', component: Signup, meta: { guestOnly: true } },
  { path: '/items', component: Shop, meta: { requiresAuth: true } },
  { path: '/product/:id', component: ProductDetail, meta: { requiresAuth: true } },
  { path: '/cart', component: Cart, meta: { requiresAuth: true } },
  { path: '/orders', component: Orders, meta: { requiresAuth: true } },
  { path: '/become-vendor', component: VendorRegister, meta: { requiresAuth: true } },
  { path: '/profile', component: Profile, meta: { requiresAuth: true } },
  { path: '/privacy-policy', component: PrivacyPolicy },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

let _authChecked = false
let _isLoggedIn = false
let _userRoles = []
let _authPromise = null

const DESK_ROLES = ['Vendor', 'Supplier', 'System Manager', 'Administrator']

async function checkAuth() {
  if (_authChecked) return _isLoggedIn
  if (_authPromise) return _authPromise
  _authPromise = api.getSessionProfile()
    .then(data => {
      if (data.message?.authenticated) {
        _isLoggedIn = true
        _userRoles = data.message.roles || []
      } else {
        _isLoggedIn = false
        _userRoles = []
      }
    })
    .catch(() => { _isLoggedIn = false; _userRoles = [] })
    .finally(() => { _authChecked = true; _authPromise = null })
  await _authPromise
  return _isLoggedIn
}

function isVendorUser() {
  return DESK_ROLES.some(r => _userRoles.includes(r)) && !_userRoles.includes('Customer')
}

router.beforeEach(async (to) => {
  const loggedIn = await checkAuth()

  if (!loggedIn) {
    if (to.meta.requiresAuth) {
      _authChecked = false
      return { path: '/login' }
    }
    return true
  }

  if (to.meta.guestOnly) {
    return { path: '/' }
  }

  // Vendor/Supplier/System Manager → redirect to Frappe desk
  if (isVendorUser()) {
    window.location.href = '/desk'
    return false
  }
})

export function invalidateAuthCache() {
  _authChecked = false
  _isLoggedIn = false
}

// Navbar use kare — agar cache warm hai to no API call
export function checkAuthState() {
  return checkAuth()
}

export default router
