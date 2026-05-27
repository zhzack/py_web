<script setup>
import { computed } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import {
  House, Cpu, VideoCamera, MagicStick, DocumentCopy, SwitchButton, Grid,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const menus = [
  { path: '/dashboard', title: '总览', icon: House },
  { path: '/devices',   title: '设备', icon: Cpu },
  { path: '/device-groups', title: '设备组', icon: Grid },
  { path: '/console',   title: '实时控制', icon: VideoCamera },
  { path: '/macros',    title: '宏管理', icon: MagicStick },
  { path: '/logs',      title: '动作日志', icon: DocumentCopy },
]

const activePath = computed(() => route.path)

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <el-container style="height:100vh">
    <el-aside width="220px" style="background:#001529">
      <div style="color:#fff; padding:18px; font-size:18px; font-weight:600">HID Gateway</div>
      <el-menu
        :default-active="activePath"
        background-color="#001529"
        text-color="#cfd8e3"
        active-text-color="#409EFF"
        router
      >
        <el-menu-item v-for="m in menus" :key="m.path" :index="m.path">
          <el-icon><component :is="m.icon" /></el-icon>
          <span>{{ m.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header style="background:#fff; border-bottom:1px solid #eee; display:flex; align-items:center; justify-content:space-between">
        <div style="font-size:16px">{{ route.meta?.title || '' }}</div>
        <div>
          <span style="margin-right:12px; color:#666">{{ auth.user?.username }} ({{ auth.user?.role }})</span>
          <el-button size="small" :icon="SwitchButton" @click="logout">退出</el-button>
        </div>
      </el-header>
      <el-main style="background:#f5f7fa">
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>
