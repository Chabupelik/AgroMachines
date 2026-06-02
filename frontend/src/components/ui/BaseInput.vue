<template>
  <div class="relative w-full flex flex-col gap-1.5">
    <label v-if="label" class="text-[10px] text-text-muted uppercase tracking-widest font-extrabold">
      {{ label }}
    </label>
    
    <input
      :type="type"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :placeholder="placeholder"
      :disabled="disabled"
      class="w-full bg-bg border border-border text-text-main px-4 py-3 rounded-lg text-sm font-sans tracking-wide outline-none transition-all duration-200 placeholder:text-text-muted/50 focus:border-accent focus:bg-surface focus:shadow-[0_0_15px_rgba(176,141,87,0.12)] disabled:opacity-50"
      :class="[error ? 'border-danger/50 bg-danger/5' : '']"
    >
    
    <transition enter-active-class="transition duration-200 ease-out" enter-from-class="transform -translate-y-1 opacity-0" enter-to-class="transform translate-y-0 opacity-100">
      <span v-if="error" class="text-[10px] text-danger/80 font-bold uppercase tracking-wider mt-0.5">
        {{ error }}
      </span>
    </transition>
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: [String, Number], default: '' },
  type: { type: String, default: 'text' },
  label: { type: String, default: '' },
  placeholder: { type: String, default: '---' },
  error: { type: String, default: '' },
  disabled: { type: Boolean, default: false }
})
defineEmits(['update:modelValue'])
</script>