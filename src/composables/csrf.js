// START_FEATURE vue
import { onMounted, ref } from "vue"

export function useCSRF() {
  const csrf = ref(null)
  onMounted(() => {
    csrf.value = window.csrfmiddlewaretoken
  })
  return { csrf }
}
// END_FEATURE vue
