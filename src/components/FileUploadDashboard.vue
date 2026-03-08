<template>
  <div class="d-flex flex-column gap-4">
    <file-upload-direct
      v-bind="$attrs"
      v-model:files="files"
      v-model:selected="selected"
      :selectable="props.selectable"
    ></file-upload-direct>
    <table class="table">
      <thead>
        <th v-if="props.selectable"></th>
        <th>Filename</th>
        <th>Uploaded By</th>
        <th>Uploaded On</th>
        <th>File Size</th>
        <th>Actions</th>
      </thead>
      <tbody>
        <tr v-for="file in files">
          <td v-if="props.selectable">
            <input
              type="checkbox"
              v-model="selected"
              :value="file.id"
              @change="console.log(selected)"
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
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue"
import { useFetch } from "../composables/fetch.js"

const { post } = useFetch()
defineOptions({ inheritAttrs: false })

const props = defineProps({
  fieldId: String,
  value: String,
  selectable: {
    type: Boolean,
    default: false,
  },
})

const files = defineModel("files", { type: Array, default: [] })
const selected = ref([])

onMounted(() => {
  if (props.value) files.value = JSON.parse(props.value)
})

const deleteFile = async file => {
  await post(file.delete_url)
  files.value = files.value.filter(f => f.id != file.id)
}
</script>
