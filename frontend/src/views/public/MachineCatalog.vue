<template>
  <PublicLayout>
    <div class="max-w-[1400px] mx-auto px-6 py-16 sm:py-24">
      
      <div class="text-center space-y-4 mb-16">
        <span class="text-[10px] text-accent font-bold uppercase tracking-widest font-mono">Доступно к заказу</span>
        <h1 class="text-4xl sm:text-5xl font-extrabold text-primary uppercase tracking-widest">Каталог техники</h1>
        <div class="w-16 h-0.5 bg-accent mx-auto"></div>
      </div>

      <div v-if="isLoading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
        <div v-for="i in 8" :key="i" class="flex flex-col gap-4">
          <BaseSkeleton height="xl" class="rounded-2xl aspect-[4/3]" />
          <BaseSkeleton height="sm" class="w-3/4" />
          <BaseSkeleton height="sm" class="w-1/2" />
        </div>
      </div>

      <div v-else-if="error" class="p-8 text-center bg-danger/5 border border-danger/20 rounded-2xl text-danger font-medium max-w-2xl mx-auto">
        {{ error }}
      </div>

      <div v-else>
        <div v-if="machines.length === 0" class="flex flex-col items-center justify-center text-center border border-dashed border-border/80 rounded-2xl p-12 max-w-lg mx-auto bg-surface/50 backdrop-blur-sm">
          <div class="w-12 h-12 rounded-full bg-primary/5 flex items-center justify-center text-accent mb-4 border border-primary/10">
            <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <h4 class="text-base font-bold text-primary mb-1">Каталог временно пуст</h4>
          <p class="text-text-muted text-xs leading-relaxed max-w-sm">
            В данный момент мы обновляем список техники на сайте. Пожалуйста, зайдите позже или свяжитесь с нашим отделом продаж для подбора оборудования.
          </p>
        </div>
        
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
          <MachineCard v-for="machine in machines" :key="machine.id" :machine="machine" />
        </div>

        <Pagination :total="total" :limit="limit" :offset="offset" @change="handlePageChange" class="mt-16" />
      </div>
    </div>
  </PublicLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { machinesApi } from '@/services/machines.api'
import { useApi } from '@/composables/useApi'
import { usePagination } from '@/composables/usePagination'

import PublicLayout from '@/layouts/PublicLayout.vue'
import MachineCard from '@/components/public/MachineCard.vue'
import BaseSkeleton from '@/components/ui/BaseSkeleton.vue'
import Pagination from '@/components/ui/Pagination.vue'

const machines = ref([])
const { execute, isLoading, error } = useApi(machinesApi.getMachines)
const { limit, offset, total, setTotal, changePage } = usePagination(12)

async function fetchMachines() {
  const res = await execute(limit.value, offset.value)
  if (res?.status === 'ok') {
    machines.value = res.data
    setTotal(res.total)
  }
}

function handlePageChange(newOffset) {
  changePage(newOffset)
  fetchMachines()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(fetchMachines)
</script>