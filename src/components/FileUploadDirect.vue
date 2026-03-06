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
    // Step 1: Get upload parameters from the server
    const formData = new FormData()
    formData.set("name", file.name)
    const response = await post(props.uploadStartUrl, { body: formData })
    const attachmentData = await response.json()

    // Step 2: Upload the file to the presigned URL
    if (props.storageBackend === "s3") {
      const s3FormData = new FormData()
      for (const [key, value] of Object.entries(attachmentData.upload_presigned_url.fields)) {
        s3FormData.append(key, value)
      }
      s3FormData.append("file", file)
      await fetch(attachmentData.upload_presigned_url.url, {
        method: "POST",
        body: s3FormData,
      })
    } else {
      const uploadFormData = new FormData()
      uploadFormData.append("file", file)
      await fetch(attachmentData.upload_presigned_url, {
        method: "POST",
        body: uploadFormData,
        headers: { "X-CSRFTOKEN": csrf.value },
      })
    }

    // Step 3: Notify server that upload is complete
    const completeResponse = await post(attachmentData.upload_complete_url)
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
