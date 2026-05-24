<script>
export const meta = { layout: 'blank', requiresAuth: false, title: '登录' }
</script>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const form = reactive({ username: '', password: '' })
const loading = ref(false)
const mode = ref('login')   // 'login' | 'register'

async function submit() {
  if (!form.username || !form.password) {
    ElMessage.warning('用户名密码不能为空')
    return
  }
  loading.value = true
  try {
    if (mode.value === 'register') {
      await authApi.register(form.username, form.password)
      ElMessage.success('注册成功，请登录')
      mode.value = 'login'
    } else {
      await auth.login(form.username, form.password)
      ElMessage.success('登录成功')
      router.push(route.query.redirect || '/dashboard')
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <el-card style="width:380px">
    <h2 style="margin:0 0 18px; text-align:center">HID Gateway</h2>
    <el-form @submit.prevent="submit" label-position="top">
      <el-form-item label="用户名">
        <el-input v-model="form.username" autocomplete="username" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="form.password" type="password" show-password autocomplete="current-password" />
      </el-form-item>
      <el-button type="primary" :loading="loading" style="width:100%" @click="submit">
        {{ mode === 'login' ? '登录' : '注册' }}
      </el-button>
      <div style="text-align:center; margin-top:12px">
        <el-link type="primary" @click="mode = mode === 'login' ? 'register' : 'login'">
          {{ mode === 'login' ? '没有账号？去注册' : '已有账号？去登录' }}
        </el-link>
      </div>
    </el-form>
  </el-card>
</template>
