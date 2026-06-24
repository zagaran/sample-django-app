<!-- START_FEATURE vue -->
<template>
  <div ref="container" />
</template>

<script setup>
import { useFetch } from "../composables/fetch.js"
import { useCSRF } from "../composables/csrf.js"

import { onMounted, useTemplateRef } from "vue"

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
  uploadStartUrl: String,
  storageBackend: String,
  allowedFileTypes: Array,
  maxNumberOfFiles: Number,
  maxFileSize: Number,
  relations: {
    type: Object,
    default: () => ({}),
  },
  autoProceed: {
    type: Boolean,
    default: false,
  },
  required: {
    type: Boolean,
    default: false,
  },
})

let uppy = null

const files = defineModel("files", { type: Array, default: [] })
const selected = defineModel("selected", { type: Array, default: [] })

onMounted(() => {
  let restrictions = {}
  if (props.maxNumberOfFiles) restrictions["maxNumberOfFiles"] = props.maxNumberOfFiles
  if (props.maxFileSize) restrictions["maxFileSize"] = props.maxFileSize
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
          method: "PUT",
          url: file.attachmentData.upload_presigned_url,
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

  // When files are finished uploading and they are successful, add them to the `files` state
  uppy.on("upload-success", async (file, response) => {
    const formData = new FormData()
    formData.set("relations", JSON.stringify(props.relations))
    const completeResponse = await post(file.attachmentData.upload_complete_url, { body: formData })
    const newEntry = {
      ...(await completeResponse.json()),
      uppyId: file.id,
      size: file.size,
    }
    files.value = [newEntry, ...(files.value || [])]
    selected.value = [...selected.value, newEntry.id]
  })

  return uppy
})
</script>
<!-- END_FEATURE vue -->
