<script>
export const meta = { title: '总览' }
</script>

<script setup>
import { onMounted, ref } from 'vue'
import { devicesApi } from '@/api/devices'
import { actionsApi } from '@/api/actions'

const devices = ref([])
const online = ref([])
const logs = ref([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    devices.value = await devicesApi.list()
    online.value = (await devicesApi.online()).online
    logs.value = await actionsApi.recentLogs(20)
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>

<template>
  <div>
    <el-row :gutter="16">
      <el-col :span="6">
        <el-card>
          <div style="color:#999">设备总数</div>
          <div style="font-size:32px; font-weight:600">{{ devices.length }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div style="color:#999">在线设备</div>
          <div style="font-size:32px; font-weight:600; color:#67C23A">{{ online.length }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div style="color:#999">最近 Action</div>
          <div style="font-size:32px; font-weight:600">{{ logs.length }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div style="color:#999">成功率</div>
          <div style="font-size:32px; font-weight:600">
            {{ logs.length ? Math.round(logs.filter(l => l.status === 'acked').length / logs.length * 100) : 0 }}%
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top:16px" header="最近 Action 日志">
      <el-table :data="logs" v-loading="loading" size="small">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="action_type" label="类型" width="140" />
        <el-table-column prop="device_id" label="设备ID" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'acked' ? 'success' : row.status === 'failed' ? 'danger' : 'info'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="exec_time_ms" label="耗时(ms)" width="100" />
        <el-table-column prop="error_message" label="错误" />
        <el-table-column prop="created_at" label="时间" width="180" />
      </el-table>
    </el-card>
  </div>
</template>
