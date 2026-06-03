<template>
  <div class="min-h-screen bg-bg text-text-main flex flex-col items-center justify-center p-6 font-sans">
    <div class="text-center space-y-8 max-w-md bg-surface border border-border/40 p-12 rounded-3xl shadow-xl relative overflow-hidden">
      <div class="absolute inset-0 opacity-[0.01] pointer-events-none bg-[linear-gradient(to_right,#000_1px,transparent_1px),linear-gradient(to_bottom,#000_1px,transparent_1px)] bg-[size:2rem_2rem]"></div>
      
      <div class="relative flex flex-col items-center space-y-6">
        <div class="w-20 h-20 rounded-2xl bg-danger/5 border border-danger/20 flex items-center justify-center text-danger">
          <svg class="w-10 h-10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            <circle cx="12" cy="11" r="3"></circle>
            <path d="M12 14v4"></path>
          </svg>
        </div>
        
        <div class="space-y-3">
          <h1 class="text-5xl font-black text-danger tracking-widest font-mono">403</h1>
          <h2 class="text-sm font-bold text-primary uppercase tracking-widest">Доступ ограничен</h2>
          <p class="text-text-muted text-xs leading-relaxed max-w-sm mx-auto">
            У вашей учетной записи недостаточно прав для просмотра этого секретного терминала управления. Пожалуйста, обратитесь к системному администратору.
          </p>
        </div>

        <router-link :to="{ name: ROUTE_NAMES.ADMIN  }">
          <button class="inline-flex items-center gap-2 bg-transparent border border-border/80 hover:border-accent hover:text-accent px-6 py-3 rounded-xl font-bold text-xs uppercase tracking-widest active:scale-95 transition-all cursor-pointer">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="9 14 4 9 9 4"></polyline>
              <path d="M20 20v-7a4 4 0 0 0-4-4H4"></path>
            </svg>
            Вернуться на панель
          </button>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ROUTE_NAMES } from '@/constants/routes'
</script>