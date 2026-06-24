// START_FEATURE vue
const modules = import.meta.glob("./*.js", { eager: true })
const components = {}

for (const path in modules) {
  // Extract the file name without extension
  const name = path.match(/\.\/(.*)\.js$/)[1]
  components[name] = modules[path].default
}

export default components
// END_FEATURE vue
