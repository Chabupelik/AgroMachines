import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    tailwindcss(),
  ],
  // 🔥 ДОБАВЛЯЕМ ЭТОТ БЛОК НАСТРОЕК ПРОКСИ:
  server: {
    proxy: {
      '/api': {
        target: 'https://agromachines.chabupelik.su',
        changeOrigin: true,
        secure: true,
      },
      '/media': {
        target: 'https://agromachines.chabupelik.su',
        changeOrigin: true,
        secure: true,
      }
    }
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})