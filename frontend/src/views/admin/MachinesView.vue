<!-- src/views/admin/MachinesView.vue -->
<template>
  <AdminLayout>
    <div class="space-y-6 max-w-[1400px] mx-auto">
      
      <div class="flex flex-col sm:flex-row gap-4 justify-between sm:items-center bg-surface p-6 rounded-2xl border border-border/50 shadow-sm">
        <h1 class="text-xl sm:text-2xl font-black uppercase tracking-widest text-primary">База техники</h1>
        
        <BaseButton @click="createNewMachine" class="inline-flex items-center justify-center gap-1.5 w-full sm:w-auto">
          <svg class="w-4 h-4 fill-current shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Добавить модель
        </BaseButton>
      </div>

      <div v-if="isLoading && machines.length === 0" class="space-y-4">
        <BaseSkeleton height="md" v-for="i in 5" :key="i" class="rounded-xl" />
      </div>

      <div v-else>
        <DataTable :headers="columns" :items="machines">
          
          <template #image_url="{ item }">
            <div class="w-20 h-14 bg-bg rounded-xl overflow-hidden flex items-center justify-center border border-border/50 shadow-inner shrink-0">
              <img v-if="item.image_urls?.length" :src="item.image_urls[0]" class="w-full h-full object-cover">
              
              <div class="text-border/40" v-else>
                <svg class="w-6 h-6 stroke-current" viewBox="0 0 24 24" fill="none" stroke-width="1.8">
                  <circle cx="18" cy="18" r="3" />
                  <circle cx="6" cy="18" r="2" />
                  <path d="M6 16h12" />
                  <path d="M8 16V10h6v6" />
                  <path d="M14 10l2 3h2v3" />
                  <path d="M10 10V8h1" />
                </svg>
              </div>
            </div>
          </template>
          
          <template #price="{ item }">
            <span v-if="item.price" class="font-mono text-accent font-bold">{{ formatPrice(item.price) }}</span>
            <span v-else class="text-text-muted opacity-50 font-mono">—</span>
          </template>

          <template #actions="{ item }">
            <div class="flex justify-end items-center gap-1">
              
              <button 
                @click="editExistingMachine(item)" 
                class="text-primary hover:text-accent hover:scale-110 transition-all duration-200 cursor-pointer p-2 flex items-center justify-center rounded-lg hover:bg-primary/5"
                title="Редактировать модель"
              >
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4z"></path>
                </svg>
              </button>

              <button 
                @click="triggerDeleteMachine(item)" 
                class="text-danger hover:text-red-600 hover:scale-110 transition-all duration-200 cursor-pointer p-2 flex items-center justify-center rounded-lg hover:bg-danger/5"
                title="Удалить модель"
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

    <BaseModal :show="isVisible" @close="close">
      <MachineEditForm :machine="selectedMachine" @cancel="close" @success="handleSuccess" />
    </BaseModal>

    <BaseConfirmModal 
      :show="isConfirmVisible" 
      title="Удаление техники"
      :message="`Вы действительно хотите безвозвратно удалить модель '${confirmMachineName}'? Все файлы изображений будут стерты из облачного хранилища MinIO.`"
      @cancel="isConfirmVisible = false"
      @confirm="confirmDelete"
    />

  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { machinesApi } from '@/services/machines.api'
import { usePagination } from '@/composables/usePagination'
import { useModal } from '@/composables/useModal'
import { useToast } from '@/composables/useToast'
import { mapApiError } from '@/utils/apiErrors'

import AdminLayout from '@/layouts/AdminLayout.vue'
import DataTable from '@/components/ui/DataTable.vue'
import BaseSkeleton from '@/components/ui/BaseSkeleton.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import Pagination from '@/components/ui/Pagination.vue'
import MachineEditForm from '@/components/forms/MachineEditForm.vue'
import BaseConfirmModal from '@/components/ui/BaseConfirmModal.vue'

const toast = useToast()
const { isVisible, open: openModal, close } = useModal()
const { limit, offset, total, setTotal, changePage } = usePagination(10)

const machines = ref([])
const isLoading = ref(false)
const selectedMachine = ref(null) 

const isConfirmVisible = ref(false)
const confirmMachineId = ref(null)
const confirmMachineName = ref('')

const columns = [
  { key: 'image_url', label: 'Фото' },
  { key: 'id', label: 'ID' },
  { key: 'title', label: 'Название' },
  { key: 'price', label: 'Стоимость' },
  { key: 'actions', label: 'Действия', class: 'text-right' }
]

function formatPrice(val) { return new Intl.NumberFormat('ru-RU').format(val) + ' ₽' }

async function fetchMachines() {
  isLoading.value = true
  try {
    const res = await machinesApi.getMachines(limit.value, offset.value)
    if (res.status === 'ok') {
      machines.value = res.data
      setTotal(res.total)
    }
  } catch (err) { toast.error(mapApiError(err)) } 
  finally { isLoading.value = false }
}

function createNewMachine() {
  selectedMachine.value = null
  openModal()
}

function editExistingMachine(item) {
  selectedMachine.value = item
  openModal()
}

function handlePageChange(newOffset) {
  changePage(newOffset)
  fetchMachines()
}

function handleSuccess() {
  close()
  fetchMachines() 
}

function triggerDeleteMachine(item) {
  confirmMachineId.value = item.id
  confirmMachineName.value = item.title
  isConfirmVisible.value = true
}

async function confirmDelete() {
  isConfirmVisible.value = false
  try {
    await machinesApi.deleteMachine(confirmMachineId.value)
    machines.value = machines.value.filter(m => m.id !== confirmMachineId.value)
    toast.success('Техника удалена')
  } catch (err) { toast.error(mapApiError(err)) }
}

onMounted(fetchMachines)
</script>