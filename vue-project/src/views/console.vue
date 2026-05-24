<script>
export const meta = { title: '实时控制' }
</script>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { devicesApi } from '@/api/devices'
import { actionsApi } from '@/api/actions'

const devices = ref([])
const online = ref([])
const selected = ref('')
const text = ref('')
const sending = ref(false)
const lastResult = ref(null)

const KEYS = ['KEY_A','KEY_B','KEY_C','KEY_ENTER','KEY_SPACE','KEY_TAB','KEY_ESC','KEY_BACKSPACE',
  'KEY_UP','KEY_DOWN','KEY_LEFT','KEY_RIGHT']

async function load() {
  devices.value = await devicesApi.list()
  online.value = (await devicesApi.online()).online
  if (!selected.value && online.value.length) selected.value = online.value[0]
}
onMounted(load)

async function send(payload) {
  if (!selected.value) return ElMessage.warning('请先选择目标设备')
  sending.value = true
  try {
    lastResult.value = await actionsApi.send({ device_id: selected.value, payload, timeout_ms: 3000 })
    const r = lastResult.value.results?.[0]
    if (r?.status === 'acked') ElMessage.success(`成功 ${r.exec_time_ms}ms`)
    else ElMessage.warning(`${r?.status} ${r?.error_message || ''}`)
  } finally {
    sending.value = false
  }
}

function sendKey(k)   { send({ type: 'keyboard_tap', key: k }) }
function sendText()   { if (text.value) send({ type: 'text', content: text.value, interval_ms: 10 }) }
function mouseMove(x, y) { send({ type: 'mouse_move', x, y }) }
function mouseClick(b)   { send({ type: 'mouse_click', button: b }) }
</script>

<template>
  <el-row :gutter="16">
    <el-col :span="8">
      <el-card header="设备">
        <el-select v-model="selected" placeholder="选择设备" style="width:100%">
          <el-option v-for="d in devices" :key="d.id" :label="`${d.name || d.device_uuid} ${online.includes(d.device_uuid) ? '🟢' : '⚪'}`" :value="d.device_uuid" />
        </el-select>
        <el-button @click="load" style="margin-top:8px" size="small">刷新</el-button>
      </el-card>

      <el-card header="最近结果" style="margin-top:16px">
        <pre style="max-height:300px; overflow:auto; margin:0; font-size:12px">{{ JSON.stringify(lastResult, null, 2) }}</pre>
      </el-card>
    </el-col>

    <el-col :span="16">
      <el-card header="键盘">
        <el-button v-for="k in KEYS" :key="k" :loading="sending" size="small" style="margin:4px" @click="sendKey(k)">{{ k }}</el-button>
      </el-card>

      <el-card header="文本输入" style="margin-top:16px">
        <el-input v-model="text" placeholder="输入要发送的文本" @keyup.enter="sendText">
          <template #append>
            <el-button @click="sendText" :loading="sending">发送</el-button>
          </template>
        </el-input>
      </el-card>

      <el-card header="鼠标" style="margin-top:16px">
        <el-space wrap>
          <el-button @click="mouseMove(0, -20)">↑ 20</el-button>
          <el-button @click="mouseMove(0,  20)">↓ 20</el-button>
          <el-button @click="mouseMove(-20, 0)">← 20</el-button>
          <el-button @click="mouseMove( 20, 0)">→ 20</el-button>
          <el-divider direction="vertical" />
          <el-button type="primary" @click="mouseClick(1)">左键</el-button>
          <el-button type="warning" @click="mouseClick(2)">右键</el-button>
        </el-space>
      </el-card>
    </el-col>
  </el-row>
</template>
