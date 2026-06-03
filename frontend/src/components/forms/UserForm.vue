<template>
  <form @submit.prevent="submitForm" class="flex flex-col max-h-[65vh] sm:max-h-[75vh] select-none">
    
    <h2 class="text-lg sm:text-xl font-black text-primary uppercase tracking-widest border-b border-border/40 pb-4 shrink-0">
      {{ user ? 'Редактировать сотрудника' : 'Новый сотрудник' }}
    </h2>

    <div class="flex-grow overflow-y-auto py-4 pr-1.5 space-y-6">
      <div class="space-y-4">
        <BaseInput 
          v-model="formData.username" 
          label="Логин (Англ. буквы без пробелов) *" 
          placeholder="ivan_manager" 
          required 
          :disabled="!!user" 
        />
        
        <BaseInput 
          v-model="formData.password" 
          type="password" 
          :label="user ? 'Новый пароль (оставьте пустым, если не меняется)' : 'Пароль *'" 
          placeholder="••••••••" 
          :required="!user" 
        />

        <BaseInput 
          v-model="formData.telegram_username" 
          label="Никнейм в Telegram (строго без знака @)" 
          placeholder="ivan_agro_tg" 
        />
        
        <div v-if="formData.role !== ROLES.SUPERADMIN" class="flex flex-col gap-1.5">
          <label class="text-[10px] text-text-muted uppercase tracking-widest font-extrabold">Роль доступа *</label>
          <select v-model="formData.role" class="w-full bg-bg border border-border/60 text-text-main px-4 py-3 rounded-xl text-sm font-sans outline-none focus:border-accent focus:bg-surface transition-all cursor-pointer">
            <option :value="ROLES.MANAGER">Менеджер (Только заявки)</option>
            <option :value="ROLES.EDITOR">Редактор (Только техника)</option>
            <option :value="ROLES.ADMIN">Администратор (Заявки + Техника)</option>
          </select>
        </div>

        <div v-if="user && user.id !== currentUser?.id" class="flex items-center justify-between bg-surface/50 border border-border/30 rounded-2xl p-4 transition-all duration-300">
          <div>
            <span class="block text-xs font-bold text-text-main">Статус учетной записи</span>
            <span class="block text-[10px] text-text-muted mt-0.5">
              {{ formData.is_active ? 'Активен (Сотрудник имеет доступ в панель)' : 'Заблокирован (Доступ закрыт)' }}
            </span>
          </div>
          
          <button 
            type="button" 
            @click="formData.is_active = !formData.is_active"
            class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
            :class="[formData.is_active ? 'bg-primary' : 'bg-danger']"
          >
            <span 
              class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out"
              :class="[formData.is_active ? 'translate-x-5' : 'translate-x-0']"
            />
          </button>
        </div>
      </div>
    </div>

    <div class="pt-4 border-t border-border/40 flex justify-end gap-3 shrink-0">
      <BaseButton type="button" variant="secondary" class="w-1/2 sm:w-auto" @click="$emit('cancel')">Отмена</BaseButton>
      <BaseButton type="submit" :loading="isExecuting" class="w-1/2 sm:w-auto">Сохранить</BaseButton>
    </div>
  </form>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { authApi } from '@/services/auth.api'
import { useApi } from '@/composables/useApi'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'
import { ROLES } from '@/constants/roles'
import { userDomain } from '@/domain/user.domain'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const props = defineProps({
  user: { type: Object, default: null }
})

const emit = defineEmits(['success', 'cancel'])
const toast = useToast()
const { currentUser } = useAuth()

const { execute: executeCreate, isLoading: isCreating } = useApi(authApi.createUser)
const { execute: executeUpdate, isLoading: isUpdating } = useApi(authApi.updateUser)

const isExecuting = computed(() => isCreating.value || isUpdating.value)

const formData = ref({
  username: '',
  password: '',
  role: ROLES.MANAGER,
  telegram_username: '',
  is_active: true
})

onMounted(() => {
  if (props.user) {
    formData.value = {
      username: props.user.username || '',
      password: '', 
      role: props.user.role || ROLES.MANAGER,
      telegram_username: props.user.telegram_username || '',
      is_active: props.user.is_active !== false
    }
  }
})

async function submitForm() {
  const validation = userDomain.validateForm(
    formData.value.username, 
    formData.value.password, 
    formData.value.role, 
    !!props.user
  )
  
  if (!validation.isValid) {
    return toast.error(validation.error)
  }

  if (formData.value.telegram_username) {
    formData.value.telegram_username = formData.value.telegram_username.trim().replace('@', '')
  }

  try {
    if (props.user) {
      const payload = { ...formData.value }
      if (!payload.password.trim()) {
        delete payload.password
      }
      await executeUpdate(props.user.id, payload)
      toast.success('Профиль сотрудника успешно обновлен')
    } else {
      await executeCreate(formData.value)
      toast.success('Пользователь успешно создан')
    }
    emit('success')
  } catch (err) {
    // Ошибки ловит useApi
  }
}
</script>