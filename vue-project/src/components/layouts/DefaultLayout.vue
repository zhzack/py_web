<template>
  <el-container class="common-layout">
    <el-header class="layout-header">
      <TopMenu />
    </el-header>
    <el-container class="layout-asider">
      <el-aside class="aside" :width="collapsed ? '5vh' : '10vh'">
        <SideMenu :collapsed="collapsed" @toggle="collapsed = !collapsed" />
      </el-aside>
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import SideMenu from '@/components/base/SideMenu.vue'
import TopMenu from '@/components/base/TopMenu.vue';

const collapsed = ref(false)
</script>

<style>
/* 重置默认边距，避免100vh溢出（仅新增） */
html,
body {
  margin: 0;
  padding: 0;
}

.common-layout {
  height: 100vh;
  display: flex;
  /* 新增：让header和下方容器垂直排列 */
  flex-direction: column;
  /* 新增：垂直布局 */
}

/* 下方容器（侧边栏+主内容）：占满剩余高度 */
.common-layout>.el-container.layout-asider {
  flex: 1;
  /* 保留原有，新增display和height确保占满 */
  display: flex;
  /* 新增：让侧边栏和主内容水平排列 */
  height: calc(100% - 5vh);
  /* 新增：总高度 - header的5vh */
}

.el-header.layout-header {
  height: 5vh;
  flex-shrink: 0;
  /* 新增：防止header被压缩 */
}

/* 侧边栏：占满父容器高度（仅改选择器和新增height） */
.aside {
  height: 100%;
  /* 新增：占满父容器高度 */
  transition: width 0.2s ease;
  /* 移到这里，原选择器错误 */
  overflow: hidden;
  /* 新增：防止折叠时内容溢出 */
}

.layout-main {
  padding: 16px;
  overflow: auto;
  flex: 1;
  /* 新增：占满剩余宽度 */
  height: 100%;
  /* 新增：占满父容器高度 */
}
</style>