<template>
  <header class="fixed top-0 left-0 w-full z-50 bg-surface/85 backdrop-blur-md border-b border-border/50">
    <div class="max-w-[1600px] mx-auto px-6 py-4 flex justify-between items-center">
      <router-link to="/" class="flex items-center gap-3 cursor-pointer select-none">
        <svg class="w-6 h-6 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="18" cy="18" r="3" />
          <circle cx="6" cy="18" r="2" />
          <path d="M6 16h12" />
          <path d="M8 16V10h6v6" />
          <path d="M14 10l2 3h2v3" />
          <path d="M10 10V8h1" />
        </svg>
        <span class="font-extrabold text-text-main tracking-[2px] uppercase text-sm sm:text-base">AgroMachines</span>
      </router-link>

      <nav class="hidden md:flex items-center gap-8 text-sm text-text-muted font-medium">
        <a href="#about" class="hover:text-primary transition-colors">О нас</a>
        <a href="#machines" class="hover:text-primary transition-colors">Техника</a>
        <a href="#contact" class="hover:text-primary transition-colors">Заказ звонка</a>
      </nav>

      <button @click="toggleMenu" class="md:hidden text-2xl text-primary hover:text-text-main transition-colors cursor-pointer select-none">
        <span v-if="!isMenuOpen">☰</span>
        <span v-else>✕</span>
      </button>
    </div>

    <transition enter-active-class="transition duration-300 ease-out" enter-from-class="transform -translate-y-full" enter-to-class="transform translate-y-0" leave-active-class="transition duration-200 ease-in" leave-from-class="transform translate-y-0" leave-to-class="transform -translate-y-full">
      <div v-if="isMenuOpen" class="md:hidden fixed top-[60px] left-0 w-full bg-surface border-b border-border/80 flex flex-col items-center gap-6 py-10 text-base text-text-muted shadow-2xl">
        <a href="#about" @click="closeMenu" class="hover:text-primary transition-colors">О нас</a>
        <a href="#machines" @click="closeMenu" class="hover:text-primary transition-colors">Техника</a>
        <a href="#contact" @click="closeMenu" class="hover:text-primary transition-colors">Заказ звонка</a>
      </div>
    </transition>
  </header>
</template>

<script setup>
import { ref } from 'vue'

const isMenuOpen = ref(false)

const toggleMenu = () => { isMenuOpen.value = !isMenuOpen.value }
const closeMenu = () => { isMenuOpen.value = false }
</script>