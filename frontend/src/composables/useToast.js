import { useUiStore } from '@/stores/ui.store'

export function useToast() {
  const uiStore = useUiStore()

  const success = (message) => uiStore.addToast(message, 'success')
  const error = (message) => uiStore.addToast(message, 'error')

  return { success, error }
}