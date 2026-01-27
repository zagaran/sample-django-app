<template>
  <div>
    <div ref="container" :id="fieldId + '-uppy'" />
    <input type="hidden" required :id="fieldId + '-id'" :name="fieldName" :value="taskFileIds" />
  </div>
</template>

<script setup>
import { onMounted, ref, onBeforeUnmount, useTemplateRef, computed } from "vue"

import Uppy from "@uppy/core"
import Dashboard from "@uppy/dashboard"
import XHRUpload from "@uppy/xhr-upload"
import AwsS3 from "@uppy/aws-s3"

import "@uppy/core/css/style.min.css"
import "@uppy/dashboard/css/style.min.css"

const rootRef = useTemplateRef("container")

const props = defineProps({
  fieldId: String,
  fieldName: String,
  uploadStartUrl: String,
  allowedFileTypes: Array, // Allow all file types if unspecified
  backend: String,
  taskFiles: Array, // Used to pre-fill the widget
  allowMultiple: Boolean,
})

let uppy = null
const taskFiles = ref([])
const taskFileIds = computed(() => {
  return taskFiles.value.map(task_file => task_file.id)
})

onMounted(() => {
  const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value

  // Set Multi or Single-File
  let restrictions = {}
  if (!props.allowMultiple) {
    restrictions["minNumberOfFiles"] = 1
    restrictions["maxNumberOfFiles"] = 1
  }
  if (props.allowedFileTypes) {
    restrictions["allowedFileTypes"] = props.allowedFileTypes.map(s => "." + s)
  }

  uppy = new Uppy({
    autoProceed: true,
    restrictions: restrictions,
  })

  // Prefill files
  uppy.opts.autoProceed = false
  props.taskFiles.forEach(taskFileDict => {
    const uppyId = uppy.addFile({
      name: taskFileDict.name,
      data: {},
    })
    uppy.setFileState(uppyId, {
      progress: { uploadComplete: true, uploadStarted: true },
    })
    taskFiles.value.push({
      ...taskFileDict,
      uppyId: uppyId,
    })
  })
  uppy.opts.autoProceed = true

  uppy.use(Dashboard, {
    height: 257,
    inline: true,
    proudlyDisplayPoweredByUppy: false,
    singleFileFullScreen: true,
    showProgressDetails: true,
    doneButtonHandler: null,
    showRemoveButtonAfterComplete: true,
    target: rootRef.value,
    width: "100%",
  })

  if (props.backend == "s3") {
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
      endpoint: props.uploadStartUrl,
      headers: { "X-CSRFToken": csrftoken },
      shouldRetry: false,
      limit: 1,
    })
  }

  if (props.backend == "s3") {
    uppy.addPreProcessor(async fileIds => {
      for (const fileId of fileIds) {
        const file = uppy.getFile(fileId)

        if (file.attachmentData) return

        const formData = new FormData()
        formData.set("name", file.name)

        const response = await fetch(props.uploadStartUrl, {
          body: formData,
          method: "POST",
          headers: { "X-CSRFToken": csrftoken },
        })
        file.attachmentData = await response.json()
      }
    })

    uppy.addPostProcessor(async fileIds => {
      for (const fileId of fileIds) {
        const file = uppy.getFile(fileId)

        if (props.backend == "s3") {
          const response = await fetch(file.attachmentData.upload_complete_url, {
            method: "POST",
            headers: { "X-CSRFToken": csrftoken },
          })
        }
      }
    })
  }

  uppy.on("upload-success", async (file, response) => {
    if (props.backend == "s3") {
      taskFiles.value.push({
        ...file.attachmentData,
        uppyId: file.id,
      })
    } else {
      taskFiles.value.push({
        ...response.body,
        uppyId: file.id,
      })
    }
  })

  uppy.on("file-removed", async file => {
    taskFiles.value = taskFiles.value.filter(taskFile => taskFile.uppyId !== file.id)
  })

  return uppy
})

onBeforeUnmount(() => {
  uppy?.close()
})
</script>
