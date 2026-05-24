/**
 * 自动路由：
 *   - 扫描 src/views/**\/*.vue
 *   - 文件路径 → URL 路径
 *     views/dashboard.vue          → /dashboard
 *     views/devices/index.vue      → /devices
 *     views/devices/[id].vue       → /devices/:id
 *     views/login.vue   + meta layout='blank' → /login
 *   - 通过 <script>defineOptions({ meta: { layout: 'blank', title: '...' } })</script>
 *     或 export const meta = {...}（推荐）配置 layout / title / requiresAuth
 *   - layout='blank' 走空白布局；其他默认走 DefaultLayout（带侧栏）
 */
import { createRouter, createWebHistory } from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import BlankLayout from '@/layouts/BlankLayout.vue'
import { useAuthStore } from '@/stores/auth'

const pages = import.meta.glob('@/views/**/*.vue', { eager: true })

function toRoutePath(filePath) {
  // /src/views/devices/[id].vue → /devices/:id
  let p = filePath
    .replace(/.*\/src\/views/, '')
    .replace(/\.vue$/, '')
    .replace(/\/index$/, '')
    .replace(/\[(\w+)\]/g, ':$1')
  if (p === '') p = '/'
  if (!p.startsWith('/')) p = '/' + p
  return p
}

const defaultChildren = []
const blankChildren = []

for (const [filePath, mod] of Object.entries(pages)) {
  const path = toRoutePath(filePath)
  const meta = mod.meta || mod.default?.meta || {}
  const route = {
    path: path === '/' ? '' : path.replace(/^\//, ''),
    component: mod.default,
    meta: { title: meta.title, requiresAuth: meta.requiresAuth !== false, ...meta },
  }
  if (meta.layout === 'blank') blankChildren.push({ ...route, path })
  else defaultChildren.push(route)
}

const routes = [
  { path: '/', component: DefaultLayout, redirect: '/dashboard', children: defaultChildren },
  ...blankChildren.map((r) => ({ ...r, component: BlankLayout, children: [{ path: '', component: r.component, meta: r.meta }] })),
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.title) document.title = `${to.meta.title} · HID Gateway`
  if (to.meta.requiresAuth && !auth.token) {
    // 避免 redirect 链式嵌套：只保留最初始的目标路径
    const redirect = to.query.redirect || (to.path === '/login' ? '/dashboard' : to.fullPath)
    return { path: '/login', query: { redirect } }
  }
  if (to.path === '/login' && auth.token) return { path: '/dashboard' }
})

export default router
