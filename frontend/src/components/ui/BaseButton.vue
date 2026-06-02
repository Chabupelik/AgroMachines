<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    class="relative flex items-center justify-center px-6 py-3 rounded-lg font-bold text-xs uppercase tracking-widest transition-all duration-200 outline-none select-none active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none cursor-pointer"
    :class="[
      variant === 'primary' 
        ? 'bg-accent text-bg hover:brightness-110 hover:shadow-[0_0_20px_rgba(205,161,95,0.3)]' 
        : 'bg-transparent border border-border text-text-muted hover:text-text-main hover:border-text-muted'
    ]"
  >
    <span v-if="loading" class="absolute inset-0 flex items-center justify-center bg-inherit rounded-lg">
      <svg class="animate-spin h-5 w-5 text-current" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </span>
    
    <span :class="{ 'opacity-0': loading }">
      <slot />
    </span>
  </button>
</template>

<script setup>
defineProps({
  type: { type: String, default: 'button' },
  variant: { type: String, default: 'primary' }, // 'primary' | 'secondary'
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false }
})
</script>