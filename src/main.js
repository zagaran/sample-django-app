import directives from "./directives"
import components from "./components"

const MainVue = {
  install: (app, options) => {
    app.config.compilerOptions.whitespace = "preserve"

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
export default MainVue