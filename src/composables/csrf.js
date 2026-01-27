import { onMounted, ref } from "vue"

export function useCSRF() {
  const csrf = ref(null)
  onMounted(() => {
    csrf.value = window.csrfmiddlewaretoken
  })
  return { csrf }
}
