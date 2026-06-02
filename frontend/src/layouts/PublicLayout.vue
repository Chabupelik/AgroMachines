<template>
  <div class="min-h-screen flex flex-col bg-bg text-text-main">
    <Header />
    
    <main class="flex-grow pt-[64px]">
      <slot />
    </main>
    
    <Footer />
    
    <BaseToast />
  </div>
</template>

<script setup>
import Header from '@/components/public/Header.vue'
import Footer from '@/components/public/Footer.vue'
import BaseToast from '@/components/ui/BaseToast.vue'
</script>