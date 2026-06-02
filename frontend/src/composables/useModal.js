import { ref } from 'vue'

export function useModal() {
  const isVisible = ref(false)

  const open = () => { isVisible.value = true }
  const close = () => { isVisible.value = false }
  const toggle = () => { isVisible.value = !isVisible.value }

  return { isVisible, open, close, toggle }
}