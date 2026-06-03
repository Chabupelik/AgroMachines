<template>
  <AdminLayout>
    <div class="space-y-6 max-w-[1400px] mx-auto">

      <div class="flex justify-between items-center bg-surface p-6 rounded-2xl border border-border/50 shadow-sm">
        <h1 class="text-2xl font-black uppercase tracking-widest text-primary">Обработка заявок</h1>
        <span class="text-xs font-mono text-text-muted uppercase tracking-wider bg-bg px-3 py-1 rounded-md border border-border/50">
          Всего заявок: {{ total }}
        </span>
      </div>

      <div v-if="isLoading" class="space-y-4">
        <BaseSkeleton height="md" v-for="i in 5" :key="i" class="rounded-xl" />
      </div>

      <div v-else>
        <DataTable :headers="dynamicColumns" :items="sortedLeads">
          
          <template #status="{ item }">
            <div class="flex items-center gap-3">
              <StatusBadge :status="item.status" />
              
              <div class="flex gap-1.5" v-if="item.status !== 'DONE'">
                <button 
                  v-if="leadDomain.canTakeInProgress(item)"
                  @click="handleStatusChange(item, 'IN_PROGRESS', currentUser.username)"
                  class="inline-flex items-center gap-1.5 px-3 py-1.5 text-[10px] font-mono font-bold uppercase tracking-widest text-primary border border-primary/20 bg-primary/5 rounded-lg hover:bg-primary hover:text-surface hover:-translate-y-[1px] active:translate-y-0 transition-all duration-150 cursor-pointer shadow-sm"
                >
                  <svg class="w-2.5 h-2.5 fill-current shrink-0" viewBox="0 0 24 24">
                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                  </svg>
                  В работу
                </button>

                <button 
                  v-if="leadDomain.canComplete(item, currentUser.username, currentUser.role)"
                  @click="handleStatusChange(item, 'DONE', currentUser.username)"
                  class="inline-flex items-center gap-1.5 px-3 py-1.5 text-[10px] font-mono font-bold uppercase tracking-widest text-success border border-success/20 bg-success/5 rounded-lg hover:bg-success hover:text-white hover:-translate-y-[1px] active:translate-y-0 transition-all duration-150 cursor-pointer shadow-sm"
                >
                  <svg class="w-2.5 h-2.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                  Завершить
                </button>
              </div>
            </div>
          </template>

          <template #processed_by="{ item }">
            <span v-if="item.processed_by" class="font-bold text-accent">{{ item.processed_by }}</span>
            <span v-else class="text-text-muted opacity-50">—</span>
          </template>

          <template #created_at="{ item }">
            <span class="text-text-muted">{{ formatDate(item.created_at) }}</span>
          </template>

          <template #actions="{ item }">
            <div class="flex justify-end">
              <button 
                @click="removeLead(item.id)" 
                class="text-danger hover:text-red-600 hover:scale-110 transition-all duration-200 cursor-pointer p-2 flex items-center justify-center rounded-lg hover:bg-danger/5"
                title="Удалить заявку"
              >
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                  <line x1="10" y1="11" x2="10" y2="17"></line>
                  <line x1="14" y1="11" x2="14" y2="17"></line>
                </svg>
              </button>
            </div>
          </template>

        </DataTable>

        <Pagination :total="total" :limit="limit" :offset="offset" @change="handlePageChange" class="mt-8" />
      </div>

    </div>
  </AdminLayout>
</template>

<script setup>
import { onMounted, onBeforeUnmount, computed } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { usePagination } from '@/composables/usePagination'
import { useLeads } from '@/composables/useLeads'
import { leadDomain } from '@/domain/lead.domain'

import AdminLayout from '@/layouts/AdminLayout.vue'
import DataTable from '@/components/ui/DataTable.vue'
import StatusBadge from '@/components/admin/StatusBadge.vue'
import BaseSkeleton from '@/components/ui/BaseSkeleton.vue'
import Pagination from '@/components/ui/Pagination.vue'

const { currentUser } = useAuth()
const { limit, offset, total, setTotal, changePage } = usePagination(20)
const { leads, isLoading, fetchLeads, changeStatus, removeLead } = useLeads()

let pollInterval = null

const sortedLeads = computed(() => {
  if (!leads.value) return []
  return [...leads.value].sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
})

const dynamicColumns = computed(() => {
  const base = [
    { key: 'id', label: 'ID' },
    { key: 'client_name', label: 'Имя клиента' },
    { key: 'client_phone', label: 'Телефон' },
    { key: 'status', label: 'Статус' },
    { key: 'processed_by', label: 'Менеджер' },
    { key: 'created_at', label: 'Дата' }
  ]
  if (currentUser.value?.role === 'SUPERADMIN') {
    base.push({ key: 'actions', label: 'Удаление', class: 'text-right' })
  }
  return base
})

async function handleStatusChange(item, newStatus, username) {
  try {
    await changeStatus(item, newStatus, username)
    await fetchLeads(limit.value, offset.value, setTotal)
  } catch (err) {
    console.warn("Возник конфликт при изменении статуса. Перезагружаем данные...", err)
    await fetchLeads(limit.value, offset.value, setTotal)
  }
}

function formatDate(isoString) {
  return new Date(isoString).toLocaleString('ru-RU', { 
    day: '2-digit', 
    month: '2-digit', 
    hour: '2-digit', 
    minute: '2-digit',
    timeZone: 'Europe/Moscow'
  })
}

function handlePageChange(newOffset) {
  changePage(newOffset)
  fetchLeads(limit.value, offset.value, setTotal)
}

onMounted(() => {
  fetchLeads(limit.value, offset.value, setTotal)

  pollInterval = setInterval(() => {
    fetchLeads(limit.value, offset.value, setTotal)
  }, 30000)
})

onBeforeUnmount(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
})
</script>