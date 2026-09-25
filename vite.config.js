// START_FEATURE vue
import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import { glob } from "glob"
// START_FEATURE direct_upload
import { execSync } from "node:child_process"
// END_FEATURE direct_upload

const SRC_LOCATION = "vue/pages"
const DEST_LOCATION = "static/js/dist"

// START_FEATURE direct_upload
// The Vue sources ship inside the installed django-attachments-framework Python package
// TODO: remove this when development is done
const ATTACHMENTS_FRAMEWORK_LOCATION = execSync(
  `${process.env.PYTHON || "uv run python"} -c "import attachments_framework, os; print(os.path.join(os.path.dirname(attachments_framework.__file__), 'frontend'))"`,
)
  .toString()
  .trim()
// END_FEATURE direct_upload

export default defineConfig(({ mode }) => {
  const DEVELOPMENT = mode === "development"
  return {
    plugins: [vue()],
    base: "/" + DEST_LOCATION,
    resolve: {
      alias: [
        { find: /^vue$/, replacement: "vue/dist/vue.esm-bundler.js" },
        // START_FEATURE direct_upload
        { find: "attachments-framework", replacement: ATTACHMENTS_FRAMEWORK_LOCATION },
        // END_FEATURE direct_upload
      ],
      // START_FEATURE direct_upload
      // The attachments sources live outside this project, so make sure they use this project's copy of Vue
      dedupe: ["vue"],
      // END_FEATURE direct_upload
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
              return id.split("vue/")[1].split(".js")[0]
            }
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
