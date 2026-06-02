<template>
  <form 
    @submit.prevent="handleSubmit" 
    class="space-y-6 w-full mx-auto"
    :class="[
      flat 
        ? 'bg-transparent border-0 p-0 shadow-none' 
        : 'bg-surface border border-border/80 p-8 rounded-2xl shadow-xl max-w-md'
    ]"
  >
    <h3 class="text-lg sm:text-xl font-bold text-primary text-center uppercase tracking-wider mb-6">Заказать обратный звонок</h3>
    
    <BaseInput
      v-model="name"
      label="Ваше имя"
      placeholder="Иван"
      :error="nameError"
      :disabled="isLoading"
    />
    
    <BaseInput
      v-model="phone"
      label="Номер телефона"
      placeholder="+7 (999) 000-00-00"
      :error="phoneError"
      :disabled="isLoading"
    />
    
    <div ref="turnstileContainer" class="flex justify-center my-2"></div>

    <div class="flex items-start gap-3 select-none">
      <input
        id="agreed"
        type="checkbox"
        v-model="agreed"
        :disabled="isLoading"
        class="mt-1 h-4 w-4 rounded border-border text-primary focus:ring-primary/20 accent-primary cursor-pointer"
      >
      <label for="agreed" class="text-xs text-text-muted leading-relaxed normal-case">
        Я соглашаюсь на <router-link to="/terms" class="text-primary hover:underline">обработку персональных данных</router-link> и принимаю <router-link to="/policy" class="text-primary hover:underline">политику конфиденциальности</router-link>.
      </label>
    </div>

    <BaseButton type="submit" :loading="isLoading" class="w-full">
      Отправить заявку
    </BaseButton>
  </form>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { config } from '@/config'
import { leadDomain } from '@/domain/lead.domain'
import { leadsApi } from '@/services/leads.api'
import { useApi } from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import { mapApiError } from '@/utils/apiErrors'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const name = ref('')
const phone = ref('')
const agreed = ref(false)

const nameError = ref('')
const phoneError = ref('')
const toast = useToast()

defineProps({
  flat: { type: Boolean, default: false }
})

const turnstileContainer = ref(null)
let widgetId = null
const captchaToken = ref('')

const { execute, isLoading } = useApi(leadsApi.createLead)

onMounted(() => {
  if (!window.turnstile) {
    const script = document.createElement('script')
    script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit'
    script.async = true
    script.defer = true
    document.head.appendChild(script)
    script.onload = initTurnstile
  } else {
    initTurnstile()
  }
})

onBeforeUnmount(() => {
  if (window.turnstile && widgetId !== null) {
    window.turnstile.remove(widgetId)
  }
})

function initTurnstile() {
  if (window.turnstile && turnstileContainer.value) {
    widgetId = window.turnstile.render(turnstileContainer.value, {
      sitekey: config.turnstileSiteKey, // берет тестовый ключ 1x000... из config
      callback: (token) => {
        captchaToken.value = token
      },
      'error-callback': () => {
        toast.error('Проверка безопасности не пройдена')
      }
    })
  }
}

async function handleSubmit() {
  nameError.value = ''
  phoneError.value = ''

  const validation = leadDomain.validateForm(name.value, phone.value, agreed.value)
  if (!validation.isValid) {
    if (validation.error.includes('имя')) nameError.value = validation.error
    else if (validation.error.includes('телефон')) phoneError.value = validation.error
    else toast.error(validation.error)
    return
  }

  if (!captchaToken.value) {
    toast.error('Пожалуйста, подождите проверки безопасности')
    return
  }

  try {
    const res = await execute(name.value, phone.value, captchaToken.value)
    
    if (res.status === 'ok') {
      toast.success('Заявка успешно отправлена! Ожидайте звонка.')
      name.value = ''
      phone.value = ''
      agreed.value = false
      
      if (window.turnstile && widgetId !== null) {
        window.turnstile.reset(widgetId)
        captchaToken.value = ''
      }
    }
  } catch (err) {
    const message = mapApiError(err)
    toast.error(message)

    if (window.turnstile && widgetId !== null) {
      window.turnstile.reset(widgetId)
      captchaToken.value = ''
    }
  }
}
</script>