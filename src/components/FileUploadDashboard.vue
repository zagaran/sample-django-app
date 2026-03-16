<!-- START_FEATURE vue -->
<template>
  <div class="d-flex flex-column gap-4">
    <file-upload-direct
      v-bind="$attrs"
      v-model:files="files"
      v-model:selected="selected"
      :selectable="selectable"
    ></file-upload-direct>
    <div class="table-responsive">
      <table class="table" v-if="files.length > 0">
        <thead>
          <tr>
            <th v-if="selectable"></th>
            <th>Filename</th>
            <th>Uploaded By</th>
            <th>Uploaded On</th>
            <th>File Size</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="file in files" :class="tableRowClass(file)">
            <td v-if="selectable && fieldName">
              <input
                type="checkbox"
                v-model="selected"
                :value="file.id"
                :name="fieldName"
                :multiple="multiple"
              />
            </td>
            <td>{{ file.name }}</td>
            <td>{{ file.user.email }}</td>
            <td>{{ file.upload_completed_on }}</td>
            <td>{{ fileSize(file.size) }}</td>
            <td>
              <div class="d-flex gap-2">
                <a target="_blank" :href="file.view_url">
                  <button class="btn btn-sm btn-secondary">View</button>
                </a>
                <a :href="file.download_url">
                  <button class="btn btn-sm btn-secondary">Download</button>
                </a>
                <button class="btn btn-sm btn-danger" @click="deleteFile(file)">Delete</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="alert alert-light">
        <i class="bi bi-exclamation-square me-2"></i>
        No Attachments
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from "vue"
import { useFetch } from "../composables/fetch.js"
import { fileSize } from "humanize-plus"

const { post } = useFetch()
defineOptions({ inheritAttrs: false })

const props = defineProps({
  fieldName: String,
  queryset_json: String,
  selectable: {
    type: Boolean,
    default: false,
  },
})

const files = defineModel("files", { type: Array, default: [] })
const selected = defineModel("selected", { type: Array, default: [] })

onMounted(() => {
  if (props.queryset_json) {
    files.value = JSON.parse(props.queryset_json)
  }
})

const tableRowClass = file => {
  const classList = []
  if (selected.value.includes(file.id)) {
    classList.push(props.selectable ? "table-primary" : "table-info")
  }
  return classList
}

const deleteFile = async file => {
  const response = await post(file.delete_url)
  if (response.ok) files.value = files.value.filter(f => f.id != file.id)
}
</script>
<!-- END_FEATURE vue -->
