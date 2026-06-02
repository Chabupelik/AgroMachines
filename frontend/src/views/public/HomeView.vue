<template>
  <PublicLayout>
    <div class="space-y-0">
      <HeroSection />

      <AboutSection />

      <section id="machines" class="py-24 px-6 max-w-[1200px] mx-auto text-center space-y-6">
        <span class="text-[10px] text-accent font-bold uppercase tracking-widest font-mono">Каталог</span>
        <h2 class="text-3xl font-extrabold text-primary uppercase tracking-widest">Популярные модели</h2>
        <div class="w-12 h-0.5 bg-accent mx-auto mb-12"></div>
        <div class="p-12 border border-border border-dashed rounded-2xl text-text-muted text-xs font-mono">
          Здесь будут выводиться карточки тракторов на следующем этапе.
        </div>
      </section>

      <section id="contact" class="bg-bg py-24 px-6 border-t border-border/50">
        <div class="max-w-[1200px] mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div class="space-y-4 text-left">
            <span class="text-[10px] text-accent font-bold uppercase tracking-widest font-mono">Свяжитесь с нами</span>
            <h2 class="text-3xl font-extrabold text-primary uppercase tracking-widest leading-tight">Остались вопросы?</h2>
            <p class="text-text-muted text-sm max-w-md normal-case leading-relaxed">
              Оставьте свои контакты в форме справа. Наш ведущий специалист перезвонит вам в течение 24 часов для подробной консультации и подбора лучших условий.
            </p>
          </div>
          
          <LeadForm />
        </div>
      </section>
    </div>
  </PublicLayout>
</template>

<script setup>
import PublicLayout from '@/layouts/PublicLayout.vue'
import HeroSection from '@/components/public/HeroSection.vue'
import AboutSection from '@/components/public/AboutSection.vue'
import LeadForm from '@/components/forms/LeadForm.vue'
</script>