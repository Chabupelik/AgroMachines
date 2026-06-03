<template>
  <AdminLayout>
    <div class="space-y-6 max-w-[1400px] mx-auto">
      
      <div class="flex flex-col sm:flex-row gap-4 justify-between sm:items-center bg-surface p-6 rounded-2xl border border-border/50 shadow-sm">
        <h1 class="text-xl sm:text-2xl font-black uppercase tracking-widest text-primary">Журнал безопасности</h1>
        <span class="text-xs font-mono text-text-muted uppercase tracking-wider bg-bg px-3 py-1 rounded-md border border-border/50 w-full sm:w-auto text-center">
          Всего записей: {{ total }}
        </span>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 bg-surface p-5 rounded-2xl border border-border/50 shadow-sm text-left select-none">
        
        <div class="flex flex-col gap-1.5">
          <label class="text-[10px] text-text-muted uppercase tracking-widest font-extrabold">Фильтр событий</label>
          <select 
            v-model="filters.action" 
            @change="handleFilterChange"
            class="w-full bg-bg border border-border/60 text-text-main px-4 py-2.5 rounded-xl text-xs font-sans outline-none focus:border-accent focus:bg-surface transition-all cursor-pointer font-bold uppercase tracking-wider"
          >
            <option value="">Все события</option>
            <option value="CREATE_MACHINE">CREATE_MACHINE</option>
            <option value="UPDATE_MACHINE">UPDATE_MACHINE</option>
            <option value="DELETE_MACHINE">DELETE_MACHINE</option>
            <option value="CREATE_LEAD">CREATE_LEAD</option>
            <option value="CHANGE_STATUS">CHANGE_STATUS</option>
            <option value="DELETE_LEAD">DELETE_LEAD</option>
          </select>
        </div>

        <div class="flex flex-col gap-1.5">
          <label class="text-[10px] text-text-muted uppercase tracking-widest font-extrabold">Тип объекта</label>
          <select 
            v-model="filters.entity_type" 
            @change="handleFilterChange"
            class="w-full bg-bg border border-border/60 text-text-main px-4 py-2.5 rounded-xl text-xs font-sans outline-none focus:border-accent focus:bg-surface transition-all cursor-pointer font-bold uppercase tracking-wider"
          >
            <option value="">Все типы</option>
            <option value="machine">machine</option>
            <option value="lead">lead</option>
            <option value="user">user</option>
          </select>
        </div>

        <div class="flex flex-col gap-1.5">
          <label class="text-[10px] text-text-muted uppercase tracking-widest font-extrabold">Инициатор</label>
          <select 
            v-model="filters.user_id" 
            @change="handleFilterChange"
            class="w-full bg-bg border border-border/60 text-text-main px-4 py-2.5 rounded-xl text-xs font-sans outline-none focus:border-accent focus:bg-surface transition-all cursor-pointer font-bold uppercase tracking-wider"
          >
            <option value="">Все пользователи</option>
            <option v-for="u in usersList" :key="u.id" :value="u.id">
              @{{ u.username }} ({{ u.role }})
            </option>
          </select>
        </div>

        <div class="flex items-end">
          <button 
            v-if="filters.action || filters.entity_type || filters.user_id"
            @click="resetFilters"
            type="button"
            class="inline-flex items-center gap-1.5 text-xs text-danger hover:text-red-600 font-bold uppercase tracking-wider font-mono transition-colors pb-3 cursor-pointer"
          >
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
            Сбросить фильтры
          </button>
        </div>
      </div>

      <div v-if="isLoading && logs.length === 0" class="space-y-4">
        <BaseSkeleton height="md" v-for="i in 10" :key="i" class="rounded-xl" />
      </div>

      <div v-else>
        <DataTable :headers="columns" :items="logs">
          
          <template #timestamp="{ item }">
            <span class="text-text-muted font-mono text-[10px]">{{ formatDate(item.timestamp) }}</span>
          </template>

          <template #action="{ item }">
            <span class="font-bold text-[10px] font-mono" :class="getActionColor(item.action)">{{ item.action }}</span>
          </template>

          <template #entity="{ item }">
            <span 
              class="border px-2.5 py-0.5 rounded-lg text-[9px] uppercase font-mono font-bold tracking-wider shadow-sm select-none"
              :class="getEntityColor(item.entity_type)"
            >
              {{ item.entity_type }} #{{ item.entity_id }}
            </span>
          </template>

          <template #user_id="{ item }">
            <div class="flex items-center gap-2 group/id relative select-none">
              <span v-if="item.username" class="font-black text-primary text-xs shrink-0">@{{ item.username }}</span>
              
              <div v-else-if="item.user_id" class="flex items-center gap-1.5 opacity-0 group-hover/id:opacity-100 transition-all duration-200">
                <span class="text-[10px] font-mono opacity-60 bg-bg px-2 py-0.5 rounded-md border border-border/30 select-all">
                  {{ item.user_id }}
                </span>
                
                <button 
                  @click="copyToClipboard(item.user_id)"
                  class="p-1 rounded bg-bg hover:bg-border/20 text-text-muted hover:text-primary transition-all cursor-pointer"
                  title="Скопировать полный ID"
                >
                  <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                  </svg>
                </button>
              </div>
              
              <span v-else class="text-[9px] bg-accent/5 border border-accent/20 text-accent px-2 py-0.5 rounded-lg font-bold uppercase tracking-widest font-mono select-none">
                Система / TG Bot
              </span>
            </div>
          </template>
          
        </DataTable>

        <Pagination :total="total" :limit="limit" :offset="offset" @change="handlePageChange" class="mt-8" />
      </div>

    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { auditApi } from '@/services/audit.api'
import { authApi } from '@/services/auth.api' 
import { usePagination } from '@/composables/usePagination'
import { useToast } from '@/composables/useToast'
import { mapApiError } from '@/utils/apiErrors'

import AdminLayout from '@/layouts/AdminLayout.vue'
import DataTable from '@/components/ui/DataTable.vue'
import BaseSkeleton from '@/components/ui/BaseSkeleton.vue'
import Pagination from '@/components/ui/Pagination.vue'

const toast = useToast()
const { limit, offset, total, setTotal, changePage } = usePagination(30)

const logs = ref([])
const usersList = ref([]) 
const isLoading = ref(false)

const filters = ref({
  action: '',
  entity_type: '',
  user_id: ''
})

const columns = [
  { key: 'timestamp', label: 'Дата/Время' },
  { key: 'action', label: 'Событие' },
  { key: 'entity', label: 'Объект' },
  { key: 'user_id', label: 'Инициатор' }
]

function copyToClipboard(text) {
  if (!text) return
  navigator.clipboard.writeText(text)
  toast.success('ID инициатора скопирован в буфер обмена')
}

function getEntityColor(entityType) {
  switch (entityType) {
    case 'machine':
      return 'bg-amber-500/10 border-amber-500/30 text-amber-600 shadow-[0_2px_8px_rgba(245,158,11,0.08)]'
    case 'lead':
      return 'bg-emerald-500/10 border-emerald-500/30 text-emerald-600 shadow-[0_2px_8px_rgba(16,185,129,0.08)]'
    case 'user':
      return 'bg-indigo-500/10 border-indigo-500/30 text-indigo-600 shadow-[0_2px_8px_rgba(99,102,241,0.08)]'
    default:
      return 'bg-gray-500/10 border-gray-500/30 text-gray-600'
  }
}

async function fetchUsersList() {
  try {
    const res = await authApi.getUsers()
    if (res.status === 'ok') {
      usersList.value = res.data
    }
  } catch (err) {
    console.error('Не удалось загрузить список персонала для фильтров:', err)
  }
}

function handleFilterChange() {
  changePage(0)
  fetchLogs()
}

function resetFilters() {
  filters.value.action = ''
  filters.value.entity_type = ''
  filters.value.user_id = ''
  handleFilterChange()
}

function formatDate(isoString) {
  return new Date(isoString).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'Europe/Moscow'
  })
}

function getActionColor(action) {
  if (action.includes('CREATE')) return 'text-success'
  if (action.includes('DELETE')) return 'text-danger'
  if (action.includes('UPDATE') || action.includes('CHANGE')) return 'text-accent'
  return 'text-text-main'
}

async function fetchLogs() {
  isLoading.value = true
  try {
    const activeFilters = {}
    if (filters.value.action) activeFilters.action = filters.value.action
    if (filters.value.entity_type) activeFilters.entity_type = filters.value.entity_type
    if (filters.value.user_id) activeFilters.user_id = filters.value.user_id 

    const res = await auditApi.getLogs(limit.value, offset.value, activeFilters)
    if (res.status === 'ok') {
      logs.value = res.data
      setTotal(res.total)
    }
  } catch (err) { toast.error(mapApiError(err)) } 
  finally { isLoading.value = false }
}

function handlePageChange(newOffset) {
  changePage(newOffset)
  fetchLogs()
}

onMounted(() => {
  fetchLogs()
  fetchUsersList() 
})
</script>