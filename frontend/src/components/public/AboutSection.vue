<template>
  <section id="about" class="bg-surface py-32 px-6 border-y border-border">
    <div class="max-w-[1400px] mx-auto">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-20">
        
        <div class="space-y-12">
          <div class="space-y-4">
            <span class="text-xs text-accent font-black uppercase tracking-[4px]">01 / Информация</span>
            <h2 class="text-5xl sm:text-7xl font-black text-primary uppercase leading-none">
              Железные <br>стандарты
            </h2>
          </div>
          
          <div class="grid grid-cols-1 gap-10">
            <div v-for="(item, i) in info" :key="i" class="flex gap-8 items-start p-8 bg-bg rounded-3xl border border-border/40">
               <span class="text-4xl">{{ item.icon }}</span>
               <div class="space-y-2">
                 <h4 class="font-black text-primary uppercase text-sm">{{ item.title }}</h4>
                 <p class="text-text-muted text-sm leading-relaxed font-medium">{{ item.text }}</p>
               </div>
            </div>
          </div>
        </div>

        <div class="space-y-10">
          <div class="p-10 bg-primary text-white rounded-[40px] shadow-2xl relative overflow-hidden">
            <div class="absolute -right-10 -top-10 text-[160px] font-black text-white/5 select-none">24/7</div>
            <h3 class="text-3xl font-black uppercase mb-6">Ваш урожай — <br>наша работа</h3>
            <p class="text-white/80 leading-relaxed text-lg font-medium relative z-10">
              Каждый день простоя техники в сезон стоит миллионы. Мы построили систему логистики запчастей так, чтобы вы получали детали в день обращения. Наши инженеры работают на результат, а не на отчеты.
            </p>
          </div>
          
          <div class="grid grid-cols-2 gap-6">
            <div class="p-8 bg-[#eab308]/10 rounded-3xl border border-[#eab308]/30">
              <div class="text-4xl font-black text-accent">500+</div>
              <div class="text-[10px] font-black uppercase tracking-widest text-primary mt-2">Машин в полях</div>
            </div>
            <div class="p-8 bg-[#eab308]/10 rounded-3xl border border-[#eab308]/30">
              <div class="text-4xl font-black text-accent">12</div>
              <div class="text-[10px] font-black uppercase tracking-widest text-primary mt-2">Лет на рынке</div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </section>
</template>

<script setup>
const info = [
  { icon: '🚜', title: 'Прямой импорт', text: 'Работаем без посредников с заводами-производителями. Минимальные сроки поставки.' },
  { icon: '🛠', title: 'Собственный сервис', text: 'Бригады инженеров в каждом регионе присутствия. Оригинальное диагностическое ПО.' }
]
</script>