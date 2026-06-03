<template>
  <div class="min-h-screen bg-bg flex items-center justify-center p-6">
    <div class="w-full max-w-md bg-surface p-10 rounded-3xl shadow-2xl border border-border/40 space-y-8">
      
      <div class="text-center space-y-4">
        <div class="w-16 h-16 bg-primary rounded-xl mx-auto flex items-center justify-center shadow-lg">
          <svg class="w-8 h-8 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M6 16h12M8 16V10h6v6M14 10l2 3h2v3M10 10V8h1" stroke-linecap="round" />
            <circle cx="18" cy="18" r="3" /><circle cx="6" cy="18" r="2" />
          </svg>
        </div>
        <h1 class="text-2xl font-black text-primary uppercase tracking-[4px]">AgroPanel</h1>
        <p class="text-xs text-text-muted font-mono uppercase tracking-widest">Авторизация сотрудников</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-5">
        <BaseInput 
          v-model="username" 
          label="Имя пользователя (Логин)" 
          placeholder="admin" 
          :disabled="isLoading"
        />
        <BaseInput 
          v-model="password" 
          type="password" 
          label="Пароль" 
          placeholder="••••••••" 
          :disabled="isLoading"
        />

        <BaseButton type="submit" :loading="isLoading" class="w-full mt-4">
          Войти в систему
        </BaseButton>
      </form>

    </div>
    
    <BaseToast />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseToast from '@/components/ui/BaseToast.vue'
import { ROUTE_NAMES } from '@/constants/routes'

const router = useRouter()
const { login } = useAuth()

const username = ref('')
const password = ref('')
const isLoading = ref(false)

async function handleLogin() {
  if (!username.value || !password.value) return

  isLoading.value = true
  const success = await login(username.value, password.value)
  isLoading.value = false

  if (success) {
    router.push({ name: ROUTE_NAMES.ADMIN }) 
  }
}
</script>