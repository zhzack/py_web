
<template>
  <el-row justify="space-between" >
    
    <el-col>
      <el-text size="large" tag="b">My Admin</el-text>
    </el-col>

    <el-col class="flex items-center gap-3">
      <el-text>{{ userStore.name }}</el-text>

      <el-switch v-model="isDark" active-text="夜间" inactive-text="白天" @change="toggleTheme" />
    </el-col>
   
  </el-row>

</template>



<script setup>
import { useUserStore } from '@/store/user.js'
const userStore = useUserStore()

</script>


