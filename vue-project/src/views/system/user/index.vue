<template>
  <div>
    <el-card>
      <h2>用户管理页面</h2>
      <el-table :data="users">
        <el-table-column prop="id" label="ID" width="50" />
        <el-table-column prop="name" label="用户名" />
        <el-table-column prop="role" label="角色" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const users = ref([
  { id: 1, name: 'Alice', role: 'Admin' },
  { id: 2, name: 'Bob', role: 'Editor' },
])
</script>
