<template>
  <transition 
    enter-active-class="transition duration-200 ease-out" 
    enter-from-class="opacity-0 scale-95" 
    enter-to-class="opacity-100 scale-100" 
    leave-active-class="transition duration-150 ease-in" 
    leave-from-class="opacity-100 scale-100" 
    leave-to-class="opacity-0 scale-95"
  >
    <div v-if="show" class="fixed inset-0 z-[1200] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-fade-in" @click="$emit('cancel')">
      <div class="relative bg-surface border border-border/50 max-w-sm w-full p-8 rounded-3xl shadow-2xl space-y-6" @click.stop>
        
        <div class="mx-auto w-16 h-16 rounded-2xl bg-danger/5 border border-danger/20 flex items-center justify-center text-danger">
          <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
        </div>

        <div class="text-center space-y-2">
          <h3 class="text-base font-black text-primary uppercase tracking-wider">{{ title }}</h3>
          <p class="text-xs text-text-muted leading-relaxed max-w-xs mx-auto">{{ message }}</p>
        </div>

        <div class="flex gap-3 pt-2">
          <BaseButton type="button" variant="secondary" class="w-1/2" @click="$emit('cancel')">
            {{ cancelText }}
          </BaseButton>
          <BaseButton 
            type="button" 
            variant="primary" 
            class="w-1/2 bg-danger hover:bg-red-600 border-danger hover:border-red-600 text-white shadow-sm hover:shadow-md transition-all active:scale-95" 
            @click="$emit('confirm')"
          >
            {{ confirmText }}
          </BaseButton>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import BaseButton from '@/components/ui/BaseButton.vue'

defineProps({
  show: { type: Boolean, required: true },
  title: { type: String, default: 'Подтвердите действие' },
  message: { type: String, default: 'Вы действительно хотите выполнить это действие? Оно может быть необратимым.' },
  confirmText: { type: String, default: 'Да, удалить' },
  cancelText: { type: String, default: 'Отмена' }
})
defineEmits(['confirm', 'cancel'])
</script>