<script setup lang="ts">
defineProps<{ files: { id: string; name: string }[]; compact?: boolean }>()
</script>

<template>
  <el-form-item label="Attachments">
    <ul v-if="compact" class="attachments attachments--compact">
      <li v-for="file in files" :key="file.id" class="attachment">
        <span class="attachment__name">{{ file.name }}</span>
        <el-button link size="small">Remove</el-button>
      </li>
    </ul>
    <ul v-else class="attachments">
      <li v-for="file in files" :key="file.id" class="attachment">
        <span class="attachment__name text-lg">{{ file.name }}</span>
        <el-button link>Download</el-button>
      </li>
    </ul>
  </el-form-item>
</template>

<style scoped>
.attachments {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.attachments--compact {
  gap: 8px;
}

.attachment {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
}
</style>
