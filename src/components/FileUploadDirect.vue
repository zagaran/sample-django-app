<template>
  <div>
    <FileUpload
      ref="fileUploadRef"
      :multiple="multiple"
      :accept="acceptTypes"
      :file-limit="effectiveMaxFiles"
      :auto="autoProceed"
      custom-upload
      @uploader="handleUpload"
    />
    <input
      v-if="showInputs"
      v-for="fileId in fileModelIds"
      :key="fileId"
      type="hidden"
      :multiple="multiple"
      :name="fieldName"
      :value="fileId"
    />
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import { useFetch } from "../composables/fetch.js"
import { useCSRF } from "../composables/csrf.js"
import FileUpload from "primevue/fileupload"

const { post } = useFetch()
const { csrf } = useCSRF()

const fileUploadRef = ref(null)

const props = defineProps({
  fieldName: String,
  uploadStartUrl: String,
  storageBackend: String,
  allowedFileTypes: Array, // Allow all file types if unspecified
  maxNumberOfFiles: Number,
  autoProceed: {
    type: Boolean,
    default: false,
  },
  multiple: {
    type: Boolean,
    default: true,
  },
  required: {
    type: Boolean,
    default: false,
  },
  showInputs: {
    type: Boolean,
    default: true,
  },
})

const files = defineModel("files", { type: Array, default: [] })
const fileModelIds = computed(() => (files.value ? files.value.map(f => f.id) : []))

const acceptTypes = computed(() =>
  props.allowedFileTypes?.length ? props.allowedFileTypes.join(",") : undefined,
)

const effectiveMaxFiles = computed(() => {
  if (!props.multiple) return 1
  return props.maxNumberOfFiles
})

async function handleUpload({ files: uploadFiles }) {
  for (const file of uploadFiles) {
    // Get upload parameters from the server
    const uploadStartFormData = new FormData()
    uploadStartFormData.set("name", file.name)
    const response = await post(props.uploadStartUrl, { body: uploadStartFormData })
    const uploadStartData = await response.json()

    // Upload the file to the presigned URL
    const uploadFormData = new FormData()
    uploadFormData.append("file", file)
    if (props.storageBackend === "s3") {
      // Post to S3 bucket
      for (const [key, value] of Object.entries(uploadStartData.upload_presigned_url.fields)) {
        uploadFormData.append(key, value)
      }
      await fetch(uploadStartData.upload_presigned_url.url, {
        method: "POST",
        body: uploadFormData,
      })
    } else {
      // Post directly to database
      await fetch(uploadStartData.upload_presigned_url, {
        method: "POST",
        body: uploadFormData,
        headers: { "X-CSRFTOKEN": csrf.value },
      })
    }

    // Notify server that upload is complete
    const completeResponse = await post(uploadStartData.upload_complete_url)
    const newEntry = {
      ...(await completeResponse.json()),
      size: file.size,
    }
    if (props.multiple) {
      files.value = [newEntry, ...(files.value || [])]
    } else {
      files.value = [newEntry]
    }
  }

  fileUploadRef.value?.clear()
}
</script>
