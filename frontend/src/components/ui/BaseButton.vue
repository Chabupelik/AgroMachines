<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    class="relative inline-flex items-center justify-center px-10 py-4 rounded-xl font-black text-[12px] uppercase tracking-[2px] transition-all duration-100 active:translate-y-1 disabled:opacity-50 cursor-pointer select-none"
    :class="[
      variant === 'primary' 
        ? 'bg-primary text-white border-b-4 border-[#122a14] hover:brightness-110 active:border-b-0 shadow-lg' 
        : 'bg-accent text-primary border-b-4 border-[#b48a06] hover:brightness-110 active:border-b-0 shadow-lg'
    ]"
  >
    <span v-if="loading" class="animate-spin mr-3">◌</span>
    <slot />
  </button>
</template>

<script setup>
defineProps({
  type: { type: String, default: 'button' },
  variant: { type: String, default: 'primary' },
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false }
})
</script>