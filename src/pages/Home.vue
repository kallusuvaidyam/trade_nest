<template>
  <div class="home">
    <!-- Hero -->
    <section class="hero">
      <div class="hero-inner">
        <div class="hero-content">
          <span class="hero-badge">Multi-Vendor Marketplace</span>
          <h1 class="hero-title">Shop Everything<br><span>You Need</span></h1>
          <p class="hero-sub">Discover products from trusted vendors. Quality guaranteed, delivered fast.</p>
          <div class="hero-actions">
            <RouterLink to="/items" class="btn-primary">Browse Products</RouterLink>
            <RouterLink to="/orders" class="btn-outline">My Orders</RouterLink>
          </div>
        </div>
        <div class="hero-visual">
          <div class="visual-blob">
            <div class="blob-icon">🛍️</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section class="features">
      <div class="features-inner">
        <div class="feature-card" v-for="f in features" :key="f.icon">
          <div class="feature-icon">{{ f.icon }}</div>
          <h3>{{ f.title }}</h3>
          <p>{{ f.desc }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'

const features = [
  { icon: '🏪', title: 'Multi-Vendor', desc: 'Shop from multiple verified vendors in one place.' },
  { icon: '🔒', title: 'Secure Payments', desc: 'Your transactions are protected end-to-end.' },
  { icon: '🚚', title: 'Fast Delivery', desc: 'Quick dispatch and real-time order tracking.' },
  { icon: '↩️', title: 'Easy Returns', desc: 'Hassle-free return policy on all products.' },
]
</script>

<style scoped>
.home { min-height: 100vh; background: #f5f6fa; }

/* Hero */
.hero {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
  padding: 5rem 1.5rem;
}
.hero-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 3rem;
}
.hero-badge {
  display: inline-block;
  background: rgba(91,79,207,0.25);
  color: #a78bfa;
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.3rem 0.85rem;
  border-radius: 20px;
  border: 1px solid rgba(167,139,250,0.3);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: 1.2rem;
}
.hero-title {
  font-size: 3rem;
  font-weight: 800;
  color: #fff;
  line-height: 1.2;
  margin-bottom: 1rem;
}
.hero-title span { color: #a78bfa; }
.hero-sub { color: #94a3b8; font-size: 1.05rem; line-height: 1.7; max-width: 420px; margin-bottom: 2rem; }
.hero-actions { display: flex; gap: 1rem; flex-wrap: wrap; }
.btn-primary {
  background: linear-gradient(135deg, #5b4fcf, #764ba2);
  color: #fff;
  padding: 0.75rem 1.75rem;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
  transition: opacity 0.2s, transform 0.2s;
}
.btn-primary:hover { opacity: 0.9; transform: translateY(-1px); }
.btn-outline {
  background: transparent;
  color: #fff;
  padding: 0.75rem 1.75rem;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
  border: 1.5px solid rgba(255,255,255,0.25);
  transition: border-color 0.2s;
}
.btn-outline:hover { border-color: #a78bfa; }
.hero-visual { flex-shrink: 0; }
.visual-blob {
  width: 220px;
  height: 220px;
  background: linear-gradient(135deg, rgba(91,79,207,0.4), rgba(118,75,162,0.4));
  border-radius: 40% 60% 60% 40% / 50% 40% 60% 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: morph 6s ease-in-out infinite;
}
@keyframes morph {
  0%, 100% { border-radius: 40% 60% 60% 40% / 50% 40% 60% 50%; }
  50%       { border-radius: 60% 40% 40% 60% / 40% 60% 40% 60%; }
}
.blob-icon { font-size: 5rem; }

/* Features */
.features { padding: 4rem 1.5rem; }
.features-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.25rem;
}
.feature-card {
  background: #fff;
  border-radius: 14px;
  padding: 1.75rem 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  transition: transform 0.2s;
}
.feature-card:hover { transform: translateY(-4px); }
.feature-icon { font-size: 2rem; margin-bottom: 0.75rem; }
.feature-card h3 { font-size: 1rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0.4rem; }
.feature-card p { font-size: 0.85rem; color: #888; line-height: 1.6; }

@media (max-width: 768px) {
  .hero-inner { flex-direction: column; text-align: center; }
  .hero-title { font-size: 2.2rem; }
  .hero-sub { margin: 0 auto 2rem; }
  .hero-actions { justify-content: center; }
  .hero-visual { display: none; }
}
</style>
