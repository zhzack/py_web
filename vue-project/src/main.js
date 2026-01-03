import router from './route/index.js'
import { createApp } from 'vue'
import App from './App.vue'
import axios from 'axios'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'

import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 关键：永远只用 /api
axios.defaults.baseURL = '/api'

const app = createApp(App)
const pinia = createPinia()
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}

app.use(pinia)   // 👈 必须在组件 setup 执行之前注入
app.use(ElementPlus)

app.use(router)
app.config.globalProperties.$axios = axios
app.mount('#app')
