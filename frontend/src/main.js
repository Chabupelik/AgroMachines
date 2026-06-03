import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

import './assets/tailwind.css'
import { logger } from './utils/logger' 
import { useUiStore } from './stores/ui.store' 

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

app.config.errorHandler = (err, instance, info) => {
  logger.logError(err, `Vue Component Error (${info})`)
  
  try {
    const uiStore = useUiStore(pinia)
    uiStore.addToast("Произошла ошибка в интерфейсе. Попробуйте обновить страницу.", "error")
  } catch (e) {
    console.error('Critical UI crash:', err)
  }
}

app.mount('#app')