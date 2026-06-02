<template>
  <header class="fixed top-0 left-0 w-full z-50 bg-surface/90 backdrop-blur-md border-b border-border/40 shadow-sm transition-all duration-300">
    <div class="max-w-[1600px] mx-auto px-6 py-3.5 flex justify-between items-center">
      
      <router-link to="/" class="flex items-center gap-3 cursor-pointer select-none group">
        <div class="w-10 h-10 rounded-xl bg-primary/5 flex items-center justify-center text-accent border border-primary/10 group-hover:bg-primary/10 group-hover:scale-102 transition-all duration-300">
          <svg class="w-5 h-5 transition-transform duration-300 group-hover:rotate-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="18" cy="18" r="3" />
            <circle cx="6" cy="18" r="2" />
            <path d="M6 16h12" />
            <path d="M8 16V10h6v6" />
            <path d="M14 10l2 3h2v3" />
            <path d="M10 10V8h1" />
          </svg>
        </div>
        <span class="font-black text-primary tracking-[2.5px] uppercase text-sm sm:text-base group-hover:text-accent transition-colors duration-300">
          {{ config.siteName }}
        </span>
      </router-link>

      <nav class="hidden md:flex items-center gap-8 text-[10px] font-mono uppercase tracking-widest">
        <router-link 
          to="/" 
          class="nav-link" 
          :class="{ 'active': route.path === '/' && !route.hash }"
        >
          Главная
        </router-link>
        
        <a 
          v-if="route.path === '/'" 
          href="#about" 
          class="nav-link"
        >
          О нас
        </a>
        <router-link 
          v-else 
          :to="{ path: '/', hash: '#about' }" 
          class="nav-link"
        >
          О нас
        </router-link>

        <router-link 
          to="/machines" 
          class="nav-link" 
          :class="{ 'active': route.path.startsWith('/machines') }"
        >
          Каталог
        </router-link>

        <a 
          v-if="route.path === '/'" 
          href="#contact" 
          class="cta-button ml-2"
        >
          Заказать звонок
        </a>
        <router-link 
          v-else 
          :to="{ path: '/', hash: '#contact' }" 
          class="cta-button ml-2"
        >
          Заказать звонок
        </router-link>
      </nav>

      <button 
        @click="toggleMenu" 
        class="md:hidden text-primary hover:text-text-main transition-colors cursor-pointer select-none focus:outline-none"
        aria-label="Переключить меню"
      >
        <svg v-if="!isMenuOpen" class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="3" y1="12" x2="21" y2="12"></line>
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
        <svg v-else class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>

    <transition 
      enter-active-class="transition duration-300 ease-out" 
      enter-from-class="transform -translate-y-full" 
      enter-to-class="transform translate-y-0" 
      leave-active-class="transition duration-200 ease-in" 
      leave-from-class="transform translate-y-0" 
      leave-to-class="transform -translate-y-full"
    >
      <div v-if="isMenuOpen" class="md:hidden fixed top-[60px] left-0 w-full bg-surface/95 backdrop-blur-md border-b border-border/80 flex flex-col items-center gap-6 py-10 font-mono text-xs uppercase tracking-widest text-text-muted shadow-2xl">
        <router-link v-if="route.path !== '/'" to="/" @click="closeMenu" class="text-accent hover:text-primary transition-colors font-bold">
          ← На главную
        </router-link>
        
        <a v-if="route.path === '/'" href="#about" @click="closeMenu" class="hover:text-primary transition-colors">О нас</a>
        <router-link v-else :to="{ path: '/', hash: '#about' }" @click="closeMenu" class="hover:text-primary transition-colors">О нас</router-link>

        <router-link to="/machines" @click="closeMenu" class="hover:text-primary transition-colors">Каталог</router-link>

        <a v-if="route.path === '/'" href="#contact" @click="closeMenu" class="cta-button">Заказать звонок</a>
        <router-link v-else :to="{ path: '/', hash: '#contact' }" @click="closeMenu" class="cta-button">Заказать звонок</router-link>
      </div>
    </transition>
  </header>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { config } from '@/config'

const route = useRoute()
const isMenuOpen = ref(false)

const toggleMenu = () => { isMenuOpen.value = !isMenuOpen.value }
const closeMenu = () => { isMenuOpen.value = false }
</script>

<style scoped>
.nav-link {
  position: relative;
  padding: 0.4rem 0;
  font-weight: 700;
  color: var(--color-text-muted);
  transition: color 0.25s ease;
}

.nav-link:hover, .nav-link.active {
  color: var(--color-primary);
}

.nav-link::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: var(--color-accent);
  transform: scale-x(0);
  transform-origin: right;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-link:hover::after, .nav-link.active::after {
  transform: scale-x(1);
  transform-origin: left;
}

.cta-button {
  display: inline-block;
  padding: 0.55rem 1.25rem;
  border: 1px solid var(--color-border);
  color: var(--color-text-main);
  border-radius: 0.75rem;
  font-weight: 800;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.cta-button:hover {
  background-color: var(--color-accent);
  border-color: var(--color-accent);
  color: var(--color-surface);
  transform: translateY(-1.5px);
  box-shadow: 0 4px 12px rgba(234, 179, 8, 0.2);
}

.cta-button:active {
  transform: translateY(0);
}
</style>