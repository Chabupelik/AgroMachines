<template>
  <teleport to="body">
    <transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="show" class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-bg/90 backdrop-blur-md" @click.self="$emit('close')">
        
        <transition
          enter-active-class="transition duration-300 ease-out-quad"
          enter-from-class="transform scale-95 translate-y-4 opacity-0"
          enter-to-class="transform scale-100 translate-y-0 opacity-100"
          leave-active-class="transition duration-200 ease-in-quad"
          leave-from-class="transform scale-100 translate-y-0 opacity-100"
          leave-to-class="transform scale-95 translate-y-4 opacity-0"
        >
          <div v-if="show" class="w-full max-w-lg bg-surface border border-border p-6 sm:p-8 rounded-2xl shadow-2xl relative">
            <button @click="$emit('close')" class="absolute top-4 right-4 text-text-muted hover:text-text-main transition-colors cursor-pointer text-xl">
              ✕
            </button>
            
            <slot />
          </div>
        </transition>

      </div>
    </transition>
  </teleport>
</template>

<script setup>
defineProps({
  show: { type: Boolean, default: false }
})
defineEmits(['close'])
</script>