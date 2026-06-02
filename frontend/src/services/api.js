import axios from 'axios'
import { config } from '@/config'
import { useAuthStore } from '@/stores/auth.store'

const api = axios.create({
  baseURL: config.apiUrl,
  withCredentials: true,
})

let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

api.interceptors.request.use(
  (requestConfig) => {
    const authStore = useAuthStore()
    if (authStore.accessToken) {
      requestConfig.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    return requestConfig
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const authStore = useAuthStore()

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (originalRequest.url.includes('/auth/login') || originalRequest.url.includes('/auth/refresh')) {
        authStore.clearSession()
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return api(originalRequest)
          })
          .catch((err) => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const res = await axios.post(`${config.apiUrl}/api/v1/auth/refresh`, {}, { withCredentials: true })
        const newAccess = res.data.data.access_token
        
        const payload = JSON.parse(atob(newAccess.split('.')[1]))
        authStore.setSession(newAccess, { id: payload.sub, role: payload.role })

        processQueue(null, newAccess)

        originalRequest.headers.Authorization = `Bearer ${newAccess}`
        return api(originalRequest)

      } catch (refreshError) {
        processQueue(refreshError, null)
        authStore.clearSession()
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default api