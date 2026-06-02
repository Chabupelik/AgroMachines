<template>
  <PublicLayout>
    <div class="space-y-0">
      <HeroSection />

      <AboutSection />

      <section id="machines" class="relative bg-surface border-y border-border/50 py-24 px-6 overflow-hidden">
        <div class="absolute inset-0 opacity-[0.02] pointer-events-none bg-[linear-gradient(to_right,#000_1px,transparent_1px),linear-gradient(to_bottom,#000_1px,transparent_1px)] bg-[size:4rem_4rem]"></div>
        
        <div class="relative max-w-[1400px] mx-auto text-center space-y-16">
          
          <div class="space-y-4">
            <div class="font-mono text-[10px] text-accent font-extrabold tracking-widest uppercase">
              02 / КАТАЛОГ ТЕХНИКИ
            </div>
            <h2 class="text-3xl sm:text-4xl font-extrabold text-primary uppercase tracking-widest">Популярные модели</h2>
            <div class="w-12 h-0.5 bg-accent mx-auto"></div>
          </div>

          <div v-if="isLoading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div v-for="i in 4" :key="i" class="flex flex-col gap-4">
              <BaseSkeleton height="xl" class="rounded-2xl aspect-[4/3]" />
              <BaseSkeleton height="sm" class="w-3/4" />
            </div>
          </div>
          
          <div v-else-if="machines.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 text-left">
            <MachineCard v-for="machine in machines" :key="machine.id" :machine="machine" />
          </div>
          
          <div v-else class="flex flex-col items-center justify-center text-center border border-dashed border-border/80 rounded-2xl p-12 max-w-lg mx-auto bg-bg/40 backdrop-blur-sm">
            <div class="w-12 h-12 rounded-full bg-primary/5 flex items-center justify-center text-accent mb-4 border border-primary/10">
              <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
            </div>
            <h4 class="text-base font-bold text-primary mb-1">Каталог обновляется</h4>
            <p class="text-text-muted text-xs leading-relaxed max-w-sm">
              В данный момент мы обновляем список техники на сайте. Вы можете связаться с нами напрямую, чтобы получить актуальный прайс-лист со всеми моделями.
            </p>
          </div>

          <div class="pt-4">
            <router-link to="/machines">
              <BaseButton variant="secondary" class="mx-auto border-accent text-accent hover:bg-accent hover:text-surface">
                Показать весь каталог
              </BaseButton>
            </router-link>
          </div>
        </div>
      </section>

      <section id="contact" class="bg-bg py-24 px-6 relative">
        <div class="max-w-[1200px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-16 items-center">
          
          <div class="lg:col-span-6 space-y-10 text-left">
            <div class="space-y-4">
              <div class="font-mono text-[10px] text-accent font-extrabold tracking-widest uppercase">
                03 / СВЯЗЬ С НАМИ
              </div>
              <h2 class="text-3xl sm:text-4xl font-extrabold text-primary uppercase tracking-widest leading-tight">Остались вопросы?</h2>
              <p class="text-text-muted text-sm sm:text-base max-w-md normal-case leading-relaxed">
                Оставьте свои контакты в форме справа. Наш ведущий специалист перезвонит вам в течение 15 минут для подробной консультации и подбора лучших условий.
              </p>
            </div>

            <div class="space-y-5 pt-8 border-t border-border/50 max-w-md">
              <div class="flex items-center gap-4">
                <div class="w-10 h-10 rounded-xl bg-surface flex items-center justify-center text-accent border border-border/80 shadow-sm">
                  <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
                  </svg>
                </div>
                <div>
                  <p class="text-[10px] text-text-muted font-bold uppercase tracking-wider">Отдел продаж (РФ)</p>
                  <p class="text-sm font-black text-primary hover:text-accent transition-colors">
                    <a :href="`tel:${config.supportPhone}`">{{ config.supportPhone }}</a>
                  </p>
                </div>
              </div>

              <div class="flex items-center gap-4">
                <div class="w-10 h-10 rounded-xl bg-surface flex items-center justify-center text-accent border border-border/80 shadow-sm">
                  <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                    <polyline points="22,6 12,13 2,6"/>
                  </svg>
                </div>
                <div>
                  <p class="text-[10px] text-text-muted font-bold uppercase tracking-wider">Электронная почта</p>
                  <p class="text-sm font-black text-primary hover:text-accent transition-colors">
                    <a :href="`mailto:${config.supportEmail}`">{{ config.supportEmail }}</a>
                  </p>
                </div>
              </div>

              <div class="flex items-center gap-4">
                <div class="w-10 h-10 rounded-xl bg-surface flex items-center justify-center text-accent border border-border/80 shadow-sm">
                  <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                  </svg>
                </div>
                <div>
                  <p class="text-[10px] text-text-muted font-bold uppercase tracking-wider">Режим приема заявок</p>
                  <p class="text-sm font-black text-primary">Пн–Пт: 09:00 — 18:00 (МСК)</p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="lg:col-span-6 flex justify-center lg:justify-end">
            <LeadForm />
          </div>

        </div>
      </section>
    </div>
  </PublicLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { config } from '@/config'
import { machinesApi } from '@/services/machines.api'
import { useApi } from '@/composables/useApi'

import PublicLayout from '@/layouts/PublicLayout.vue'
import HeroSection from '@/components/public/HeroSection.vue'
import AboutSection from '@/components/public/AboutSection.vue'
import LeadForm from '@/components/forms/LeadForm.vue'
import MachineCard from '@/components/public/MachineCard.vue'
import BaseSkeleton from '@/components/ui/BaseSkeleton.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const machines = ref([])
const { execute, isLoading } = useApi(machinesApi.getMachines)

onMounted(async () => {
  const res = await execute(4, 0)
  if (res?.status === 'ok') machines.value = res.data
})
</script>