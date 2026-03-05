<template>
  <div class="d-flex flex-column gap-4">
    <file-upload-direct v-bind="$attrs" v-model:files="files"></file-upload-direct>
    <table class="table">
      <thead>
        <th>Filename</th>
        <th>Uploaded By</th>
        <th>Uploaded On</th>
        <th>File Size</th>
        <th>Actions</th>
      </thead>
      <tbody>
        <tr v-for="file in files">
          <td>{{ file.name }}</td>
          <td>{{ file.user }}</td>
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
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { onMounted } from "vue"

defineOptions({ inheritAttrs: false })

const props = defineProps({
  initial: String,
})

const files = defineModel("attachments", { default: [] })

onMounted(() => {
  const jsonData = document.getElementById(props.fieldId)
  if (jsonData) files.value = JSON.parse(jsonData.innerText)
})
</script>
