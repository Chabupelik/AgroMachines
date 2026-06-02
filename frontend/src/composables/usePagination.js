import { ref } from 'vue'

export function usePagination(defaultLimit = 10) {
  const limit = ref(defaultLimit)
  const offset = ref(0)
  const total = ref(0)

  function setTotal(newTotal) {
    total.value = newTotal
  }

  function changePage(newOffset) {
    offset.value = newOffset
  }

  function resetPagination() {
    offset.value = 0
    total.value = 0
  }

  return { limit, offset, total, setTotal, changePage, resetPagination }
}