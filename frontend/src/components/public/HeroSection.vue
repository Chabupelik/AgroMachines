<template>
  <section id="hero" class="relative min-h-[85vh] flex items-center justify-center overflow-hidden bg-bg py-20 px-6">
    <div class="relative z-10 max-w-[1200px] mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
      
      <div class="space-y-6 text-left">
        <div class="inline-block bg-primary/10 border border-primary/20 text-primary px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest font-mono">
          Премиум Сельхозтехника
        </div>
        <h1 class="text-4xl sm:text-6xl font-extrabold text-primary uppercase tracking-[2px] leading-tight">
          Сила земли <br>
          <span class="text-accent">в ваших руках</span>
        </h1>
        <p class="text-text-muted text-sm sm:text-base max-w-md leading-relaxed normal-case">
          Поставляем высокотехнологичные машины и комбайны для эффективного агробизнеса. Только проверенные бренды, профессиональный сервис и оперативная поддержка.
        </p>
        <div class="pt-4 flex flex-wrap gap-4">
          <a href="#contact">
            <BaseButton variant="primary">Оставить заявку</BaseButton>
          </a>
          <router-link to="/machines">
            <BaseButton variant="secondary">Смотреть каталог</BaseButton>
          </router-link>
        </div>
      </div>

      <div class="hidden lg:flex justify-center items-center select-none">
        <svg class="w-80 h-80 text-border/80 animate-[spin_60s_linear_infinite]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="0.5">
          <circle cx="12" cy="12" r="10" stroke-dasharray="2, 2" />
          <circle cx="12" cy="12" r="8" />
          <path d="M12 2v4M12 18v4M2 12h4M18 12h4" />
          <path d="M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
        </svg>
      </div>

    </div>
  </section>
</template>

<script setup>
import BaseButton from '@/components/ui/BaseButton.vue'
</script>