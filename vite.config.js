// START_FEATURE vue
import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import { glob } from "glob"

const SRC_LOCATION = "src/pages"
const DEST_LOCATION = "static/js/dist"

export default defineConfig(({ mode }) => {
  const DEVELOPMENT = mode === "development"
  return {
    plugins: [vue()],
    base: "/" + DEST_LOCATION,
    resolve: {
      alias: {
        vue: "vue/dist/vue.esm-bundler.js",
      },
    },
    build: {
      sourcemap: true,
      emptyOutDir: DEVELOPMENT,
      outDir: DEST_LOCATION,
      minify: DEVELOPMENT ? false : "terser",
      rollupOptions: {
        input: glob.sync(`${SRC_LOCATION}/**/*.js`),
        preserveEntrySignatures: true,
        output: {
          manualChunks(id) {
            if (id.includes("pages") || id.includes("mixins")) {
              // These files are imported by path and must be chunked individually
              return id.split("src/")[1].split(".js")[0]
            }
            // otherwise, add to combined chunk
            return "vue/main"
          },
          entryFileNames(chunkInfo) {
            if (chunkInfo.isEntry) {
              const name = chunkInfo.facadeModuleId.split("src/")[1]
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
