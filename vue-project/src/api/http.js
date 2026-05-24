import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'

const http = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

http.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) config.headers.Authorization = `Bearer ${auth.token}`
  return config
})

http.interceptors.response.use(
  (resp) => resp.data,
  (err) => {
    const status = err.response?.status
    const detail = err.response?.data?.detail || err.message
    if (status === 401) {
      const auth = useAuthStore()
      auth.logout()
      const current = router.currentRoute.value
      if (current.path !== '/login') {
        const redirect = current.query.redirect || current.fullPath
        router.push({ path: '/login', query: { redirect } })
      }
    }
    ElMessage.error(`[${status || 'NET'}] ${detail}`)
    return Promise.reject(err)
  },
)

export default http
