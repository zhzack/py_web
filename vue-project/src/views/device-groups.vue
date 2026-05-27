<script>
export const meta = { title: '设备组管理' }
</script>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { deviceGroupsApi } from '@/api/device-groups'
import { devicesApi } from '@/api/devices'

const groups = ref([])
const allDevices = ref([])
const loading = ref(false)

const createDialog = reactive({ visible: false, name: '' })
const editDialog = reactive({ visible: false, id: null, name: '' })
const devicesDialog = reactive({ visible: false, groupId: null, groupName: '', deviceIds: [] })
const addDevicesDialog = reactive({ visible: false, groupId: null, selectedIds: [] })
const dispatchDialog = reactive({ visible: false, groupId: null, payload: '{}', timeout: 2000 })
const resultsDialog = reactive({ visible: false, results: [], summary: {} })

async function loadGroups() {
  loading.value = true
  try {
    groups.value = await deviceGroupsApi.list()
  } finally {
    loading.value = false
  }
}

async function loadAllDevices() {
  allDevices.value = await devicesApi.list()
}

async function createGroup() {
  if (!createDialog.name) return ElMessage.warning('请输入分组名称')
  await deviceGroupsApi.create({ name: createDialog.name })
  ElMessage.success('创建成功')
  createDialog.visible = false
  createDialog.name = ''
  loadGroups()
}

function openEdit(row) {
  editDialog.id = row.id
  editDialog.name = row.name
  editDialog.visible = true
}

async function submitEdit() {
  await deviceGroupsApi.update(editDialog.id, { name: editDialog.name })
  ElMessage.success('更新成功')
  editDialog.visible = false
  loadGroups()
}

async function deleteGroup(row) {
  await ElMessageBox.confirm(`确认删除分组「${row.name}」？`, '提示', { type: 'warning' })
  await deviceGroupsApi.delete(row.id)
  ElMessage.success('删除成功')
  loadGroups()
}

async function viewDevices(row) {
  const res = await deviceGroupsApi.getDevices(row.id)
  devicesDialog.groupId = row.id
  devicesDialog.groupName = row.name
  devicesDialog.deviceIds = res.devices
  devicesDialog.visible = true
}

function openAddDevices(row) {
  addDevicesDialog.groupId = row.id
  addDevicesDialog.selectedIds = []
  addDevicesDialog.visible = true
}

async function submitAddDevices() {
  if (addDevicesDialog.selectedIds.length === 0) return ElMessage.warning('请选择设备')
  await deviceGroupsApi.addDevices(addDevicesDialog.groupId, addDevicesDialog.selectedIds)
  ElMessage.success('添加成功')
  addDevicesDialog.visible = false
  if (devicesDialog.visible) viewDevices({ id: devicesDialog.groupId, name: devicesDialog.groupName })
}

async function removeDeviceFromGroup(deviceId) {
  await deviceGroupsApi.removeDevice(devicesDialog.groupId, deviceId)
  ElMessage.success('移除成功')
  viewDevices({ id: devicesDialog.groupId, name: devicesDialog.groupName })
}

function openDispatch(row) {
  dispatchDialog.groupId = row.id
  dispatchDialog.payload = JSON.stringify({ type: 'test', data: {} }, null, 2)
  dispatchDialog.timeout = 2000
  dispatchDialog.visible = true
}

async function submitDispatch() {
  try {
    const payload = JSON.parse(dispatchDialog.payload)
    const res = await deviceGroupsApi.dispatch(dispatchDialog.groupId, payload, dispatchDialog.timeout)
    dispatchDialog.visible = false
    resultsDialog.results = res.results
    resultsDialog.summary = res.summary
    resultsDialog.visible = true
  } catch (e) {
    ElMessage.error('JSON 格式错误或请求失败')
  }
}

onMounted(() => {
  loadGroups()
  loadAllDevices()
})
</script>

<template>
  <el-card>
    <div style="display:flex; justify-content:space-between; margin-bottom:12px">
      <el-button @click="loadGroups" :loading="loading">刷新</el-button>
      <el-button type="primary" @click="createDialog.visible = true">新建分组</el-button>
    </div>
    <el-table :data="groups" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="分组名称" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="360">
        <template #default="{ row }">
          <el-button size="small" @click="viewDevices(row)">查看设备</el-button>
          <el-button size="small" @click="openAddDevices(row)">添加设备</el-button>
          <el-button size="small" @click="openDispatch(row)">批量下发</el-button>
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteGroup(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="createDialog.visible" title="新建分组" width="400px">
    <el-input v-model="createDialog.name" placeholder="分组名称" />
    <template #footer>
      <el-button @click="createDialog.visible = false">取消</el-button>
      <el-button type="primary" @click="createGroup">创建</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="editDialog.visible" title="编辑分组" width="400px">
    <el-input v-model="editDialog.name" placeholder="分组名称" />
    <template #footer>
      <el-button @click="editDialog.visible = false">取消</el-button>
      <el-button type="primary" @click="submitEdit">保存</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="devicesDialog.visible" :title="`分组设备 - ${devicesDialog.groupName}`" width="600px">
    <el-table :data="allDevices.filter(d => devicesDialog.deviceIds.includes(d.id))">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="device_uuid" label="UUID" />
      <el-table-column prop="name" label="名称" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button size="small" type="danger" @click="removeDeviceFromGroup(row.id)">移除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-dialog>

  <el-dialog v-model="addDevicesDialog.visible" title="添加设备到分组" width="600px">
    <el-checkbox-group v-model="addDevicesDialog.selectedIds">
      <div v-for="dev in allDevices" :key="dev.id" style="margin-bottom:8px">
        <el-checkbox :label="dev.id" :value="dev.id">
          {{ dev.name }} ({{ dev.device_uuid }})
        </el-checkbox>
      </div>
    </el-checkbox-group>
    <template #footer>
      <el-button @click="addDevicesDialog.visible = false">取消</el-button>
      <el-button type="primary" @click="submitAddDevices">添加</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="dispatchDialog.visible" title="批量下发指令" width="600px">
    <el-form label-width="100px">
      <el-form-item label="Payload">
        <el-input v-model="dispatchDialog.payload" type="textarea" :rows="8" />
      </el-form-item>
      <el-form-item label="超时 (ms)">
        <el-input-number v-model="dispatchDialog.timeout" :min="500" :max="10000" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dispatchDialog.visible = false">取消</el-button>
      <el-button type="primary" @click="submitDispatch">发送</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="resultsDialog.visible" title="批量下发结果" width="700px">
    <el-alert :title="`总计: ${resultsDialog.summary.total}, 成功: ${resultsDialog.summary.success}, 失败: ${resultsDialog.summary.failed}`" type="info" style="margin-bottom:12px" />
    <el-table :data="resultsDialog.results" max-height="400">
      <el-table-column prop="device_id" label="设备 UUID" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'acked' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="exec_time_ms" label="耗时 (ms)" width="100" />
      <el-table-column prop="error_message" label="错误信息" />
    </el-table>
  </el-dialog>
</template>
