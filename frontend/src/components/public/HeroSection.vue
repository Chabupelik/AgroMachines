<template>
  <section id="hero" class="relative min-h-[90vh] flex items-center bg-transparent px-6 py-12">
    <div class="max-w-[1400px] mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-16 items-center">
      
      <div class="lg:col-span-7 space-y-10">
        
        <div class="flex items-center gap-6">
          <div class="w-20 h-20 bg-primary rounded-2xl flex items-center justify-center shadow-2xl border-2 border-white/10">
             <svg class="w-12 h-12 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M6 16h12M8 16V10h6v6M14 10l2 3h2v3M10 10V8h1" stroke-linecap="round" />
                <circle cx="18" cy="18" r="3" /><circle cx="6" cy="18" r="2" />
             </svg>
          </div>
          <div>
            <h2 class="text-primary font-black uppercase tracking-[6px] text-lg">AgroMachines</h2>
            <p class="text-accent font-bold text-xs uppercase tracking-[3px]">Официальный дилер в РФ</p>
          </div>
        </div>

        <div class="space-y-6">
          <div class="inline-flex items-center gap-2 bg-primary/5 border border-primary/10 rounded-full px-4 py-1.5 text-xs font-semibold text-primary uppercase tracking-wider">
            <span class="w-2 h-2 rounded-full bg-accent animate-pulse"></span>
            Прямые поставки с заводов
          </div>

          <h1 class="text-6xl sm:text-8xl font-black text-primary leading-[0.9] tracking-tighter uppercase">
            Техника <br>высшей <br><span class="text-accent">мощности</span>
          </h1>
          <p class="text-text-muted text-lg sm:text-xl max-w-2xl font-medium leading-relaxed">
            Поставляем тяговые машины классов 3–8 для решения любых задач. Гарантируем ввод в эксплуатацию за 48 часов и пожизненную сервисную поддержку.
          </p>
        </div>

        <div class="flex flex-wrap gap-4 pt-4">
          <a href="#contact">
            <BaseButton variant="primary">
              Получить консультацию
            </BaseButton>
          </a>
          
          <router-link to="/machines">
            <BaseButton variant="secondary" class="border-accent text-accent hover:bg-accent hover:text-surface">
              Каталог моделей
            </BaseButton>
          </router-link>
        </div>

        <div class="pt-8 border-t border-border/40 grid grid-cols-3 gap-6">
          <div>
            <p class="text-2xl sm:text-3xl font-black text-primary">48 ч</p>
            <p class="text-xs text-text-muted uppercase tracking-wider font-semibold">Ввод в работу</p>
          </div>
          <div>
            <p class="text-2xl sm:text-3xl font-black text-primary">6 классов</p>
            <p class="text-xs text-text-muted uppercase tracking-wider font-semibold">Тяговой мощности</p>
          </div>
          <div>
            <p class="text-2xl sm:text-3xl font-black text-primary">24/7</p>
            <p class="text-xs text-text-muted uppercase tracking-wider font-semibold">Сервисная поддержка</p>
          </div>
        </div>

      </div>

      <div class="lg:col-span-5 relative">
        <div class="relative rounded-[40px] overflow-hidden shadow-2xl border-[12px] border-white bg-white">
          <img 
            src="https://images.unsplash.com/photo-1530267981375-f0de937f5f13?auto=format&fit=crop&q=80&w=1000" 
            class="w-full aspect-[4/5] object-cover"
            alt="Agro Power"
          />
        </div>
      </div>

    </div>
  </section>
</template>

<script setup>
import BaseButton from '@/components/ui/BaseButton.vue'
</script>

<style scoped>
@keyframes marquee {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
</style>