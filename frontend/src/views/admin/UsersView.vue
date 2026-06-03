<!-- src/views/admin/UsersView.vue -->
<template>
  <AdminLayout>
    <div class="space-y-6 max-w-[1400px] mx-auto">
      
      <div class="flex flex-col sm:flex-row gap-4 justify-between sm:items-center bg-surface p-6 rounded-2xl border border-border/50 shadow-sm">
        <h1 class="text-xl sm:text-2xl font-black uppercase tracking-widest text-primary">Персонал</h1>
        
        <BaseButton @click="createNewUser" class="inline-flex items-center justify-center gap-1.5 w-full sm:w-auto">
          <svg class="w-4 h-4 fill-current shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Добавить сотрудника
        </BaseButton>
      </div>

      <div v-if="isLoading && users.length === 0" class="space-y-4">
        <BaseSkeleton height="md" v-for="i in 3" :key="i" class="rounded-xl" />
      </div>

      <div class="table-container" v-else>
        <DataTable :headers="columns" :items="users">
          
          <template #telegram_username="{ item }">
            <span v-if="item.telegram_username" class="font-bold text-accent">@{{ item.telegram_username }}</span>
            <span class="text-text-muted opacity-40 font-mono">—</span>
          </template>

          <template #role="{ item }">
            <span 
              class="px-2.5 py-0.5 rounded-lg text-[9px] font-bold tracking-widest uppercase border select-none shadow-sm"
              :class="[
                item.role === 'SUPERADMIN' ? 'bg-red-500/10 border-red-500/30 text-red-600 shadow-[0_2px_8px_rgba(239,68,68,0.08)]' :
                item.role === 'ADMIN' ? 'bg-indigo-500/10 border-indigo-500/30 text-indigo-600 shadow-[0_2px_8px_rgba(99,102,241,0.08)]' : 
                item.role === 'EDITOR' ? 'bg-amber-500/10 border-amber-500/30 text-amber-600 shadow-[0_2px_8px_rgba(245,158,11,0.08)]' :
                'bg-emerald-500/10 border-emerald-500/30 text-emerald-600 shadow-[0_2px_8px_rgba(16,185,129,0.08)]'
              ]"
            >
              {{ item.role }}
            </span>
          </template>

          <template #is_active="{ item }">
            <span 
              class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold border select-none"
              :class="[
                item.is_active 
                  ? 'bg-success/10 border-success/30 text-success' 
                  : 'bg-danger/10 border-danger/30 text-danger'
              ]"
            >
              <span class="w-1.5 h-1.5 rounded-full animate-pulse" :class="item.is_active ? 'bg-success' : 'bg-danger'"></span>
              {{ item.is_active ? 'АКТИВЕН' : 'ЗАБЛОК' }}
            </span>
          </template>

          <template #actions="{ item }">
            <div class="flex justify-end items-center gap-1">
              <button 
                v-if="userDomain.canEditUser(item, currentUser)"
                @click="editExistingUser(item)" 
                class="text-primary hover:text-accent hover:scale-110 transition-all duration-200 cursor-pointer p-2 flex items-center justify-center rounded-lg hover:bg-primary/5"
                title="Редактировать профиль"
              >
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4z"></path>
                </svg>
              </button>

              <button 
                v-if="userDomain.canDeleteUser(item, currentUser)"
                @click="triggerDeleteUser(item)" 
                class="text-danger hover:text-red-600 hover:scale-110 transition-all duration-200 cursor-pointer p-2 flex items-center justify-center rounded-lg hover:bg-danger/5"
                title="Безвозвратно удалить"
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
      </div>

    </div>

    <BaseModal :show="isVisible" @close="close">
      <UserForm :user="selectedUser" @cancel="close" @success="handleSuccess" />
    </BaseModal>

    <BaseConfirmModal 
      :show="isConfirmVisible" 
      title="Удаление сотрудника"
      :message="`Вы действительно хотите безвозвратно удалить сотрудника ${confirmUsername}? Все логи его действий в журнале безопасности будут сохранены.`"
      @cancel="isConfirmVisible = false"
      @confirm="confirmDelete"
    />

  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { authApi } from '@/services/auth.api'
import { useAuth } from '@/composables/useAuth'
import { useModal } from '@/composables/useModal'
import { useToast } from '@/composables/useToast'
import { mapApiError } from '@/utils/apiErrors'
import { userDomain } from '@/domain/user.domain'

import AdminLayout from '@/layouts/AdminLayout.vue'
import DataTable from '@/components/ui/DataTable.vue'
import BaseSkeleton from '@/components/ui/BaseSkeleton.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import UserForm from '@/components/forms/UserForm.vue'
import BaseConfirmModal from '@/components/ui/BaseConfirmModal.vue'

const toast = useToast()
const { currentUser } = useAuth()
const { isVisible, open: openModal, close } = useModal()

const users = ref([])
const isLoading = ref(false)
const selectedUser = ref(null) 

const isConfirmVisible = ref(false)
const confirmUserId = ref(null)
const confirmUsername = ref('')

const columns = [
  { key: 'username', label: 'Логин' },
  { key: 'telegram_username', label: 'Привязка Telegram' },
  { key: 'role', label: 'Роль доступа' },
  { key: 'is_active', label: 'Статус' },
  { key: 'actions', label: 'Действия', class: 'text-right' }
]

async function fetchUsers() {
  isLoading.value = true
  try {
    const res = await authApi.getUsers()
    if (res.status === 'ok') users.value = res.data
  } catch (err) { toast.error(mapApiError(err)) } 
  finally { isLoading.value = false }
}

function createNewUser() {
  selectedUser.value = null
  openModal()
}

function editExistingUser(item) {
  selectedUser.value = item
  openModal()
}

function handleSuccess() {
  close()
  fetchUsers() 
}

function triggerDeleteUser(item) {
  confirmUserId.value = item.id
  confirmUsername.value = item.username
  isConfirmVisible.value = true
}

async function confirmDelete() {
  isConfirmVisible.value = false
  try {
    await authApi.deleteUser(confirmUserId.value)
    users.value = users.value.filter(u => u.id !== confirmUserId.value)
    toast.success('Сотрудник успешно удален')
  } catch (err) { toast.error(mapApiError(err)) }
}

onMounted(fetchUsers)
</script>