import { createApp, ref } from "vue"
import MainVue from "../main"

createApp({
  data() {
    return {
      fields: {}, // For form field rendering
    }
  },
})
  .use(MainVue)
  .mount("#app")
