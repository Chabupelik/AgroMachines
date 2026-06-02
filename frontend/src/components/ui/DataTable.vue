<template>
  <div class="w-full overflow-x-auto border border-border rounded-xl bg-surface">
    <table class="w-full text-left border-collapse font-mono text-xs">
      <thead>
        <tr class="border-b border-border/80 text-text-muted bg-black/20 uppercase tracking-wider">
          <th v-for="col in headers" :key="col.key" class="p-4 font-bold" :class="col.class">
            {{ col.label }}
          </th>
        </tr>
      </thead>
      <tbody class="divide-y divide-border/30">
        <tr v-if="items.length === 0">
          <td :colspan="headers.length" class="p-8 text-center text-text-muted">
            Нет данных для отображения
          </td>
        </tr>
        <tr v-for="(item, idx) in items" :key="item.id || idx" class="hover:bg-primary/5 transition-colors">
          <td v-for="col in headers" :key="col.key" class="p-4 text-text-main" :class="col.class">
            <slot :name="col.key" :item="item" :index="idx">
              {{ item[col.key] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({
  headers: { type: Array, required: true }, // формат: [{ key: 'username', label: 'Логин' }]
  items: { type: Array, required: true }
})
</script>