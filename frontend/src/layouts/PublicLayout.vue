<template>
  <div class="min-h-screen flex flex-col bg-bg text-text-main relative overflow-x-hidden">
    <Header />
    

    <main class="flex-grow pt-[64px] relative">
      
      <div v-if="route.path !== '/' && route.name !== 'detail'" class="max-w-[1600px] mx-auto px-6 pt-6 text-left relative">
        <div class="xl:fixed xl:top-24 xl:left-14 z-40">
          <router-link 
            to="/" 
            class="group inline-flex items-center gap-2.5 px-4 py-2 rounded-xl border border-border/60 bg-surface/80 backdrop-blur-sm text-[10px] font-mono uppercase tracking-widest text-text-muted hover:text-primary hover:border-primary/40 hover:bg-surface transition-all duration-200 select-none shadow-sm"
          >
            <svg class="w-4 h-4 transition-transform duration-200 group-hover:-translate-x-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="19" y1="12" x2="5" y2="12"></line>
              <polyline points="12 19 5 12 12 5"></polyline>
            </svg>
            Вернуться на главную
          </router-link>
        </div>
      </div>

      <slot />
    </main>
    
    <Footer />
    
    <BaseToast />
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import Header from '@/components/public/Header.vue'
import Footer from '@/components/public/Footer.vue'
import BaseToast from '@/components/ui/BaseToast.vue'

const route = useRoute()
</script>