<template>
  <div class="relative w-full flex flex-col gap-1">
    <label v-if="label" class="text-[10px] text-text-muted uppercase tracking-widest font-bold">
      {{ label }}
    </label>
    
    <input
      :type="type"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :placeholder="placeholder"
      :disabled="disabled"
      class="w-full bg-[#05101a] border text-text-main px-4 py-3 rounded-lg text-sm font-mono tracking-wide outline-none transition-all duration-200 focus:border-accent focus:shadow-[0_0_15px_rgba(205,161,95,0.15)] disabled:opacity-50"
      :class="[error ? 'border-danger' : 'border-border']"
    >
    
    <transition enter-active-class="transition duration-200 ease-out" enter-from-class="transform -translate-y-1 opacity-0" enter-to-class="transform translate-y-0 opacity-100">
      <span v-if="error" class="text-[10px] text-danger font-mono uppercase tracking-wider">
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