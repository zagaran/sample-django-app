// START_FEATURE vue
import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import { glob } from "glob"

const SRC_LOCATION = "vue/pages"
const DEST_LOCATION = "static/js/dist"

export default defineConfig(({ mode }) => {
  const DEVELOPMENT = mode === "development"
  return {
    plugins: [vue()],
    base: "/" + DEST_LOCATION,
    resolve: {
      alias: [{ find: /^vue$/, replacement: "vue/dist/vue.esm-bundler.js" }],
      // START_FEATURE direct_upload
      // django-attachments-framework is linked from a local checkout (see package.json), whose node_modules has its
      // own copy of Vue; make sure it uses this project's. Not needed once it is installed from npm.
      dedupe: ["vue"],
      // END_FEATURE direct_upload
    },
    build: {
      sourcemap: true,
      emptyOutDir: DEVELOPMENT,
      outDir: DEST_LOCATION,
      rollupOptions: {
        input: glob.sync(`${SRC_LOCATION}/**/*.js`),
        preserveEntrySignatures: true,
        output: {
          manualChunks(id) {
            if (id.includes("pages") || id.includes("mixins")) {
              // These files are imported by path and must be chunked individually
              return id.split("vue/")[1].split(".js")[0]
            }
            // START_FEATURE direct_upload
            if (id.includes("@zip.js")) {
              // Lazy-loaded by django-attachments-framework when a zip is added; keep it in its own chunk
              return
            }
            // END_FEATURE direct_upload
            // otherwise, add to combined chunk
            return "vue/main"
          },
          entryFileNames(chunkInfo) {
            if (chunkInfo.isEntry) {
              const name = chunkInfo.facadeModuleId.split("vue/")[1]
              if (!name.includes("pages")) {
                // This is not a 'real' entrypoint, should contain hash for cache busting
                const path = name.split(".js")[0]
                return `${path}-[hash].js`
              }
              // This is a real entry point, should not contain hash
              return name
            }
            return `[name]-[hash].js`
          },
          chunkFileNames: `[name]-[hash].js`,
          assetFileNames: `[name].[ext]`,
        },
      },
    },
  }
})
// END_FEATURE vue
