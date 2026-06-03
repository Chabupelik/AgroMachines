<template>
  <div class="w-full overflow-x-auto border border-border/60 rounded-2xl bg-surface shadow-sm">
    <table class="w-full text-left border-collapse font-sans text-xs">
      <thead>
        <tr class="border-b border-border/50 text-text-muted bg-primary/[0.03] uppercase tracking-wider text-[10px] font-bold">
          <th v-for="col in headers" :key="col.key" class="p-4 font-extrabold" :class="col.class">
            {{ col.label }}
          </th>
        </tr>
      </thead>
      <tbody class="divide-y divide-border/20">
        <tr v-if="items.length === 0">
          <td :colspan="headers.length" class="p-12 text-center text-text-muted font-medium">
            Нет данных для отображения
          </td>
        </tr>
        <tr 
          v-for="(item, idx) in items" 
          :key="item.id || idx" 
          class="even:bg-surface/30 hover:bg-primary/[0.03] transition-colors duration-150"
        >
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
  headers: { type: Array, required: true },
  items: { type: Array, required: true }
})
</script>