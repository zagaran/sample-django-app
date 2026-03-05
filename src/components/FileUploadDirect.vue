<template>
  <div>
    <div ref="container" />
    <input
      v-if="props.showInputs"
      v-for="fileId in fileIds"
      type="hidden"
      required
      :multiple="multiple"
      :name="fieldName"
      :value="fileId"
    />
  </div>
</template>

<script setup>
import { useFetch } from "../composables/fetch.js"
import { useCSRF } from "../composables/csrf.js"

import { onMounted, useTemplateRef, computed, watch } from "vue"

import Uppy from "@uppy/core"
import Dashboard from "@uppy/dashboard"
import XHRUpload from "@uppy/xhr-upload"
import AwsS3 from "@uppy/aws-s3"

import "@uppy/core/css/style.min.css"
import "@uppy/dashboard/css/style.min.css"

const { post } = useFetch()
const { csrf } = useCSRF()

const rootRef = useTemplateRef("container")

const props = defineProps({
  fieldName: String,
  uploadStartUrl: String,
  storageBackend: String,
  minFiles: Number,
  maxFiles: Number,
  allowedFileTypes: Array, // Allow all file types if unspecified
  autoProceed: {
    type: Boolean,
    default: false,
  },
  multiple: {
    type: Boolean,
    default: false,
  },
  showInputs: {
    type: Boolean,
    default: true,
  },
})

let uppy = null

// `attachments` represents all attachments relevant to this dashboard, which
// can include other attachments/files from previous uploads.
const files = defineModel("files", { default: [] })
const fileIds = computed(() => {
  return files.value ? files.value.map(f => f.id) : []
})

watch(files, (newFiles, oldFiles) => {
  const newUppyFiles = newFiles.map(f => f?.uppyId, 0).filter(id => id != null)
  const oldUppyFiles = oldFiles?.map(f => f?.uppyId, 0).filter(id => id != null) || []

  // Determine which uppy files were removed
  const removedIds = oldUppyFiles.filter(id => !newUppyFiles.includes(id))

  // Remove them from uppy
  for (const id of removedIds) uppy.removeFile(id)
})

onMounted(() => {
  let restrictions = {}
  restrictions["maxNumberOfFiles"] = props.multiple ? props?.maxFiles : 1
  if (props.minFiles) {
    restrictions["minNumberOfFiles"] = props.minFiles
  }
  if (props.allowedFileTypes && props.allowedFileTypes?.length) {
    restrictions["allowedFileTypes"] = props.allowedFileTypes
  }

  uppy = new Uppy({
    autoProceed: props.autoProceed,
    restrictions: restrictions,
  })

  uppy.use(Dashboard, {
    height: 300,
    inline: true,
    proudlyDisplayPoweredByUppy: false,
    singleFileFullScreen: true,
    showProgressDetails: true,
    doneButtonHandler: null,
    showRemoveButtonAfterComplete: true,
    target: rootRef.value,
    width: "100%",
  })

  if (props.storageBackend == "s3") {
    uppy.use(AwsS3, {
      shouldUseMultipart: false,
      getUploadParameters: (file, options) => {
        return {
          method: "POST",
          url: file.attachmentData.upload_presigned_url.url,
          fields: file.attachmentData.upload_presigned_url.fields,
        }
      },
    })
  } else {
    uppy.use(XHRUpload, {
      formData: true,
      fieldName: "file",
      endpoint: file => {
        return file.attachmentData.upload_presigned_url
      },
      getResponseData: xhr => {
        return JSON.parse(xhr.responseText)
      },
      withCredentials: true,
      headers: {
        "X-CSRFTOKEN": csrf.value,
      },
      shouldRetry: false,
      limit: 1,
    })
  }

  uppy.addPreProcessor(async fileIds => {
    for (const fileId of fileIds) {
      const file = uppy.getFile(fileId)

      const formData = new FormData()
      formData.set("name", file.name)

      const response = await post(props.uploadStartUrl, { body: formData })
      uppy.setFileState(fileId, { attachmentData: await response.json() })
    }
  })

  uppy.addPostProcessor(async fileIds => {
    for (const fileId of fileIds) {
      const file = uppy.getFile(fileId)
      if (!file["error"]) {
        const response = await post(file.attachmentData.upload_complete_url)
        attachments.value = [await response.json(), ...attachments.value]
      }
    }
  })

  // When files are finished uploading and they are successful, add them to the `files` state
  uppy.on("upload-success", async (file, response) => {
    const newEntry = {
      ...response.body,
      uppyId: file.id,
      size: file.size,
    }
    if (props.multiple) {
      files.value = [newEntry, ...(files.value || [])]
    } else {
      files.value = [newEntry]
    }
  })

  // // When files are removed from the frontend UI, remove them from the `files` state
  // uppy.on("file-removed", async file => {
  //   files.value = files.value.filter(f => f.uppyId !== file.id)
  // })

  return uppy
})
</script>
