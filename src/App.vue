<template>
  <Navbar />
  <RouterView />
</template>

<script setup>
import { RouterView } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
</script>

<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #f5f6fa; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
</style>
