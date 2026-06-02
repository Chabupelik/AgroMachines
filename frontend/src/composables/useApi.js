import { ref } from 'vue'
import { mapApiError } from '@/utils/apiErrors'
import { logger } from '@/utils/logger'

export function useApi(apiFunc) {
  const isLoading = ref(false)
  const error = ref(null)

  async function execute(...args) {
    isLoading.value = true
    error.value = null
    try {
      const res = await apiFunc(...args)
      return res
    } catch (err) {
      const mappedMessage = mapApiError(err)
      error.value = mappedMessage
      logger.logError(err, 'useApi Exec')
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return { execute, isLoading, error }
}