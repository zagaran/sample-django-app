import components from "./components"
import directives from "./directives"
import PrimeVue from "primevue/config"
import Aura from "@primevue/themes/aura"

const MainVueApp = {
  install: (app, options) => {
    app.config.compilerOptions.whitespace = "preserve"

    app.use(PrimeVue, {
      theme: {
        preset: Aura,
        options: {
          darkModeSelector: ".dark-mode",
        },
      },
    })

    for (const componentName in components) {
      const component = components[componentName]
      app.component(componentName, component)
    }

    for (const directiveName in directives) {
      const directive = directives[directiveName]
      // arr[0] is name of directive, arr[1] is content
      app.directive(directive[0], directive[1])
    }
  },
}

export * from "./directives"
export * from "./components"
export default MainVueApp