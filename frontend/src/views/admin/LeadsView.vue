<template>
  <AdminLayout>
    <div class="space-y-6">
      <div class="flex justify-between items-center">
        <h1 class="text-xl sm:text-2xl font-extrabold uppercase tracking-widest text-text-main">Заявки на звонок</h1>
        <span class="text-[10px] font-mono text-text-muted uppercase tracking-wider">Всего лидов: 0</span>
      </div>
      <div class="p-8 border border-border border-dashed rounded-2xl text-center text-text-muted font-mono text-xs">
        Здесь будет наша интерактивная таблица DataTable со сменой статусов.
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import AdminLayout from '@/layouts/AdminLayout.vue'
</script>