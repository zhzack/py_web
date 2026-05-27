<script>
export const meta = { title: '设备管理' }
</script>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { devicesApi } from '@/api/devices'

const rows = ref([])
const online = ref([])
const loading = ref(false)
const dialog = reactive({ visible: false, form: { device_uuid: '', name: '', capabilities: [] } })
const editDialog = reactive({ visible: false, form: { id: null, name: '', capabilities: [], owner_user_id: null } })
const capOptions = ['usb_keyboard', 'usb_mouse', 'ble_keyboard', 'ble_mouse']

async function load() {
  loading.value = true
  try {
    rows.value = await devicesApi.list()
    online.value = (await devicesApi.online()).online
  } finally {
    loading.value = false
  }
}

function isOnline(uuid) { return online.value.includes(uuid) }

async function submit() {
  if (!dialog.form.device_uuid) return ElMessage.warning('device_uuid 必填')
  await devicesApi.create(dialog.form)
  ElMessage.success('创建成功')
  dialog.visible = false
  dialog.form = { device_uuid: '', name: '', capabilities: [] }
  load()
}

function openEdit(row) {
  editDialog.form = {
    id: row.id,
    name: row.name,
    capabilities: [...(row.capabilities || [])],
    owner_user_id: row.owner_user_id,
  }
  editDialog.visible = true
}

async function submitEdit() {
  await devicesApi.update(editDialog.form.id, {
    name: editDialog.form.name,
    capabilities: editDialog.form.capabilities,
  })
  ElMessage.success('更新成功')
  editDialog.visible = false
  load()
}

async function claimDevice(row) {
  await devicesApi.claim(row.id)
  ElMessage.success('认领成功')
  load()
}

onMounted(load)
</script>

<template>
  <el-card>
    <div style="display:flex; justify-content:space-between; margin-bottom:12px">
      <el-button @click="load" :loading="loading">刷新</el-button>
      <el-button type="primary" @click="dialog.visible = true">新建设备</el-button>
    </div>
    <el-table :data="rows" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="device_uuid" label="设备 UUID" />
      <el-table-column prop="name" label="名称" />
      <el-table-column label="能力">
        <template #default="{ row }">
          <el-tag v-for="c in row.capabilities" :key="c" size="small" style="margin-right:4px">{{ c }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="归属" width="90">
        <template #default="{ row }">
          <el-tag v-if="row.owner_user_id" type="success" size="small">已认领</el-tag>
          <el-tag v-else type="info" size="small">待认领</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="实时状态" width="110">
        <template #default="{ row }">
          <el-tag :type="isOnline(row.device_uuid) ? 'success' : 'info'" size="small">
            {{ isOnline(row.device_uuid) ? 'online' : (row.status || 'offline') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="last_online_at" label="最后在线" width="180" />
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button v-if="!row.owner_user_id" size="small" type="primary" @click="claimDevice(row)">认领</el-button>
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="dialog.visible" title="新建设备" width="480px">
    <el-form label-width="100px">
      <el-form-item label="device_uuid">
        <el-input v-model="dialog.form.device_uuid" placeholder="esp32_001" />
      </el-form-item>
      <el-form-item label="名称">
        <el-input v-model="dialog.form.name" />
      </el-form-item>
      <el-form-item label="能力">
        <el-checkbox-group v-model="dialog.form.capabilities">
          <el-checkbox v-for="c in capOptions" :key="c" :label="c" :value="c" />
        </el-checkbox-group>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialog.visible = false">取消</el-button>
      <el-button type="primary" @click="submit">保存</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="editDialog.visible" title="编辑设备" width="480px">
    <el-form label-width="100px">
      <el-form-item label="名称">
        <el-input v-model="editDialog.form.name" />
      </el-form-item>
      <el-form-item label="能力">
        <el-checkbox-group v-model="editDialog.form.capabilities">
          <el-checkbox v-for="c in capOptions" :key="c" :label="c" :value="c" />
        </el-checkbox-group>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="editDialog.visible = false">取消</el-button>
      <el-button type="primary" @click="submitEdit">保存</el-button>
    </template>
  </el-dialog>
</template>
