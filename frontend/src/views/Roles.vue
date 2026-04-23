<template>
  <div class="simple-page">
    <el-card :header="title">
      <p style="text-align: center; color: #909399; padding: 40px;">
        {{ content }}
      </p>
    </el-card>
  </div>
</template>

<script setup>
const props = defineProps({
  title: { type: String, default: '页面' },
  content: { type: String, default: '功能开发中...' }
})
</script>

<style scoped>
.simple-page {
  padding: 20px;
}
</style>
