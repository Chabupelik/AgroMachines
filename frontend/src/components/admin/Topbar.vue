<template>
  <header class="w-full h-[64px] bg-surface/80 backdrop-blur-md border-b border-border/50 px-6 flex justify-between items-center select-none shrink-0">
    <div class="flex items-center gap-4">
      <button @click="$emit('toggle-sidebar')" class="md:hidden text-2xl text-primary hover:text-text-main transition-colors cursor-pointer">
        ☰
      </button>
      <h2 class="text-xs text-text-muted hidden sm:block font-medium">
        Система управления Агропром
      </h2>
    </div>

    <div class="flex items-center gap-3">
      <div class="text-right">
        <b class="text-xs text-text-main block">Администратор</b>
        <span class="text-[10px] text-accent font-bold tracking-wider uppercase">SUPERADMIN</span>
      </div>
      <div class="w-8 h-8 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-primary font-bold text-xs">
        A
      </div>
    </div>
  </header>
</template>

<script setup>
defineEmits(['toggle-sidebar'])
</script>