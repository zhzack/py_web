<template>
  <router-view />
</template>

<script setup>
// main App，不需要额外逻辑
</script>

<style>
/* ---------- 主题变量 ---------- */
/* 白天主题 */
:root {
  --el-bg-color: #ffffff;
  --el-bg-color-page: #f0f2f5;
  --el-bg-color-overlay: #ffffff;

  --el-text-color-primary: #303133;
  --el-text-color-regular: #606266;

  --el-border-color: #dcdfe6;
  --el-fill-color-light: #f5f7fa;
}
/* 夜间主题 */
[data-theme='dark'] {
  --el-bg-color: #141414;
  --el-bg-color-page: #0f0f0f;
  --el-bg-color-overlay: #1d1e1f;

  --el-text-color-primary: #e5eaf3;
  --el-text-color-regular: #cfd3dc;

  --el-border-color: #303133;
  --el-fill-color-light: #262727;
}

</style>
