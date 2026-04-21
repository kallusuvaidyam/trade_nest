<template>
  <div class="pp-page">
    <div class="pp-container">
      <div class="pp-header">
        <span class="pp-icon">🔒</span>
        <h1>Privacy Policy</h1>
        <p>Last updated: April 2025</p>
      </div>

      <div class="pp-body">
        <section v-for="section in sections" :key="section.title" class="pp-section">
          <h2>{{ section.title }}</h2>
          <p>{{ section.content }}</p>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
const sections = [
  {
    title: '1. Information We Collect',
    content: 'We collect information you provide directly, such as your name, email address, shipping address, and payment details when you register or place an order on TradeNest.',
  },
  {
    title: '2. How We Use Your Information',
    content: 'We use your information to process orders, communicate with you about your purchases, improve our services, and send you relevant updates. We do not sell your personal data to third parties.',
  },
  {
    title: '3. Data Sharing',
    content: 'We share your information only with vendors fulfilling your orders and trusted service providers (payment gateways, logistics) necessary to complete your purchase.',
  },
  {
    title: '4. Data Security',
    content: 'We implement industry-standard security measures including encryption, secure servers, and access controls to protect your personal information from unauthorized access.',
  },
  {
    title: '5. Cookies',
    content: 'TradeNest uses cookies to maintain your session, remember your cart, and improve your browsing experience. You can disable cookies in your browser settings, though some features may not function properly.',
  },
  {
    title: '6. Your Rights',
    content: 'You have the right to access, update, or delete your personal data at any time. To exercise these rights, contact us through your account settings or email us at support@tradenest.com.',
  },
  {
    title: '7. Changes to This Policy',
    content: 'We may update this Privacy Policy periodically. We will notify you of significant changes via email or a notice on our platform. Continued use of TradeNest after changes constitutes acceptance.',
  },
  {
    title: '8. Contact Us',
    content: 'If you have questions about this Privacy Policy or how we handle your data, please contact our support team at support@tradenest.com.',
  },
]
</script>

<style scoped>
.pp-page {
  min-height: 100vh;
  background: #f5f6fa;
  padding: 3rem 1.5rem;
}
.pp-container {
  max-width: 780px;
  margin: 0 auto;
}
.pp-header {
  text-align: center;
  margin-bottom: 2.5rem;
}
.pp-icon { font-size: 2.5rem; display: block; margin-bottom: 0.75rem; }
.pp-header h1 {
  font-size: 2rem;
  font-weight: 800;
  color: #1a1a2e;
  margin-bottom: 0.35rem;
}
.pp-header p { color: #888; font-size: 0.88rem; }

.pp-body {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  overflow: hidden;
}
.pp-section {
  padding: 1.75rem 2rem;
  border-bottom: 1px solid #f0f0f0;
}
.pp-section:last-child { border-bottom: none; }
.pp-section h2 {
  font-size: 0.95rem;
  font-weight: 700;
  color: #5b4fcf;
  margin-bottom: 0.6rem;
}
.pp-section p {
  font-size: 0.88rem;
  color: #555;
  line-height: 1.8;
}
</style>
