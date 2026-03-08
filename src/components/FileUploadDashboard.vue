<template>
  <div class="d-flex flex-column gap-4">
    <file-upload-direct
      v-bind="$attrs"
      v-model:files="files"
      v-model:selected="selected"
      :selectable="props.selectable"
    ></file-upload-direct>
    <div class="table-responsive">
      <table class="table" v-if="files.length > 0">
        <thead>
          <th v-if="props.selectable"></th>
          <th>Filename</th>
          <th>Uploaded By</th>
          <th>Uploaded On</th>
          <th>File Size</th>
          <th>Actions</th>
        </thead>
        <tbody>
          <tr v-for="file in files" :class="selected.includes(file.id) ? ['table-primary'] : []">
            <td v-if="props.selectable">
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
            <td>{{ file.size }}</td>
            <td>
              <div class="d-flex gap-2">
                <a target="_blank" :href="file.view_url">
                  <button class="btn btn-sm btn-outline-secondary">View</button>
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
import { onMounted, watch } from "vue"
import { useFetch } from "../composables/fetch.js"

const { post } = useFetch()
defineOptions({ inheritAttrs: false })

const props = defineProps({
  fieldId: String,
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

const deleteFile = async file => {
  await post(file.delete_url)
  files.value = files.value.filter(f => f.id != file.id)
}
</script>
