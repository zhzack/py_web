import './assets/css/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import axios from 'axios'

// 指向你的 FastAPI 后端地址
axios.defaults.baseURL = "http://127.0.0.1:8000"

const app = createApp(App)
app.config.globalProperties.$axios = axios  // 可全局使用 this.$axios
app.mount('#app')
