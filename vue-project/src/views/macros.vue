<script>
export const meta = { title: '宏管理' }
</script>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { macrosApi } from '@/api/macros'

const rows = ref([])
const loading = ref(false)
const dialog = reactive({ visible: false, form: { name: '', stepsText: '[]' } })

async function load() {
  loading.value = true
  try { rows.value = await macrosApi.list() } finally { loading.value = false }
}
onMounted(load)

async function submit() {
  let steps
  try { steps = JSON.parse(dialog.form.stepsText) }
  catch { return ElMessage.error('steps 不是合法 JSON') }
  if (!Array.isArray(steps)) return ElMessage.error('steps 必须是数组')
  await macrosApi.create({ name: dialog.form.name, steps })
  ElMessage.success('已创建')
  dialog.visible = false
  dialog.form = { name: '', stepsText: '[]' }
  load()
}

async function remove(row) {
  await ElMessageBox.confirm(`删除宏「${row.name}」？`, '确认', { type: 'warning' })
  await macrosApi.remove(row.id)
  ElMessage.success('已删除')
  load()
}

const sample = JSON.stringify([
  { type: 'keyboard_down', key: 'KEY_CTRL' },
  { type: 'keyboard_tap',  key: 'KEY_C' },
  { type: 'keyboard_up',   key: 'KEY_CTRL' },
], null, 2)
</script>

<template>
  <el-card>
    <div style="display:flex; justify-content:flex-end; margin-bottom:12px">
      <el-button type="primary" @click="dialog.visible = true">新建宏</el-button>
    </div>
    <el-table :data="rows" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="名称" width="200" />
      <el-table-column label="步骤数" width="100">
        <template #default="{ row }">{{ row.content_json?.steps?.length ?? 0 }}</template>
      </el-table-column>
      <el-table-column label="内容预览">
        <template #default="{ row }">
          <code style="font-size:12px">{{ JSON.stringify(row.content_json?.steps?.slice(0,3) || []) }}{{ (row.content_json?.steps?.length || 0) > 3 ? '…' : '' }}</code>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="dialog.visible" title="新建宏" width="640px">
    <el-form label-width="80px">
      <el-form-item label="名称"><el-input v-model="dialog.form.name" /></el-form-item>
      <el-form-item label="steps">
        <el-input v-model="dialog.form.stepsText" type="textarea" :rows="10" :placeholder="sample" />
      </el-form-item>
      <el-alert type="info" :closable="false">JSON 数组，每步含 type / key / x / y / delay_ms 等字段</el-alert>
    </el-form>
    <template #footer>
      <el-button @click="dialog.visible = false">取消</el-button>
      <el-button type="primary" @click="submit">保存</el-button>
    </template>
  </el-dialog>
</template>
