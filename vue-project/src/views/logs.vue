<script>
export const meta = { title: '动作日志' }
</script>

<script setup>
import { onMounted, ref } from 'vue'
import { actionsApi } from '@/api/actions'

const rows = ref([])
const loading = ref(false)
const limit = ref(100)

async function load() {
  loading.value = true
  try { rows.value = await actionsApi.recentLogs(limit.value) } finally { loading.value = false }
}
onMounted(load)
</script>

<template>
  <el-card>
    <div style="display:flex; gap:8px; margin-bottom:12px">
      <el-input-number v-model="limit" :min="10" :max="1000" :step="50" />
      <el-button @click="load" :loading="loading">刷新</el-button>
    </div>
    <el-table :data="rows" v-loading="loading" size="small" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="msg_id" label="msg_id" width="300" />
      <el-table-column prop="action_type" label="类型" width="140" />
      <el-table-column prop="device_id" label="设备" width="80" />
      <el-table-column prop="user_id" label="用户" width="80" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'acked' ? 'success' : row.status === 'failed' ? 'danger' : 'info'" size="small">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="exec_time_ms" label="耗时(ms)" width="100" />
      <el-table-column prop="error_code" label="错误码" width="100" />
      <el-table-column prop="error_message" label="错误信息" />
      <el-table-column prop="created_at" label="时间" width="180" />
    </el-table>
  </el-card>
</template>
