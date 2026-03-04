<template>
  <div class="d-flex flex-column gap-4">
    <file-upload-direct v-bind="$attrs" v-model:attachments="attachments"></file-upload-direct>
    <table class="table">
      <thead>
        <th>Filename</th>
        <th>Uploaded By</th>
        <th>Uploaded On</th>
        <th>File Size</th>
        <th>Actions</th>
      </thead>
      <tbody>
        <tr v-for="attachment in attachments">
          <td>{{ attachment.name }}</td>
          <td>{{ attachment.user }}</td>
          <td>{{ attachment.upload_completed_on }}</td>
          <td>{{ attachment.size }}</td>
          <td>
            <div class="d-flex gap-2">
              <a target="_blank" :href="attachment.view_url">
                <button class="btn btn-sm btn-outline-secondary">View</button>
              </a>
              <a :href="attachment.download_url">
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
defineOptions({ inheritAttrs: false })

const attachments = defineModel("attachments", { default: window.attachments })
</script>
