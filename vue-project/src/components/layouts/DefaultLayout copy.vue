
<template>
  <el-container class="common-layout" height: 100vh>
    <!-- <el-header class="header">
      <HeaderBar />
    </el-header> -->
    <el-header class="header" weight=100vh>
      <TopMenu />
    </el-header>

    <el-container>
      <el-aside class="aside" :width="collapsed ? '64px' : '200px'">
        <SideMenu :collapsed="collapsed" @toggle="collapsed = !collapsed" />
      </el-aside>
      

      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>


<script setup>
import { ref } from 'vue'
import HeaderBar from '@/components/base/HeaderBar.vue'
import SideMenu from '@/components/base/SideMenu.vue'
import TopMenu from '@/components/base/TopMenu.vue';

const collapsed = ref(false)
</script>

<style>
.common-layout {
  height: 100vh;
}

.common-layout>.el-container {
  flex: 1;
}

.header {
  height: 5vh;
}

.aside {
  transition: width 0.2s ease;
  overflow: hidden;
} 

.main {
  padding: 16px;
  overflow: auto;
}
</style>
