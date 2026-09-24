// START_FEATURE vue
import components from "./components"
import directives from "./directives"

// START_FEATURE direct_upload
import AttachmentsFramework from "attachments-framework"
// END_FEATURE direct_upload

import "bootstrap"
import "bootstrap-icons/font/bootstrap-icons.css"

const MainVueApp = {
  install: (app, options) => {
    app.config.compilerOptions.whitespace = "preserve"

    // START_FEATURE direct_upload
    // Registers <attachment-manager>, <attachment-uploader>, and <attachment-table>
    app.use(AttachmentsFramework)
    // END_FEATURE direct_upload

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
// END_FEATURE vue