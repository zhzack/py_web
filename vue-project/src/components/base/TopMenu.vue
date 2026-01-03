<template>
    <el-menu mode="horizontal" router class="header-menu">
        <el-menu-item index="/dashboard">
            Dashboard
        </el-menu-item>

        <el-menu-item index="/system">
            系统管理
        </el-menu-item>

        <el-menu-item index="/about">
            关于
        </el-menu-item>
        <el-menu-item>
            <el-switch v-model="isDark" inline-prompt active-icon="Moon" inactive-icon="Sunny" />
        </el-menu-item>
        <el-menu-item class="flex items-center gap-3">
            <el-text>{{ userStore.name }}</el-text>
        </el-menu-item>
    </el-menu>
</template>

<script setup>
import { useUserStore } from '@/store/user.js'
const userStore = useUserStore()
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
// 引入 Element Plus 暗色模式核心样式
import 'element-plus/theme-chalk/dark/css-vars.css'

// 1. 核心状态：是否为暗色模式
const isDark = ref(false)
// 2. Element Plus 主题配置
const themeConfig = ref({ name: '' })
// 3. 系统主题监听对象（用于后续移除监听）
let mediaQueryList = null

// 4. 切换主题的核心方法
const updateTheme = (darkMode) => {
    // 更新 Element Plus 主题
    themeConfig.value.name = darkMode ? 'dark' : ''
    // 更新 html 根元素 class（方便自定义样式）
    document.documentElement.classList.toggle('dark', darkMode)
    // 更新本地存储（仅用户手动切换时才存储，跟随系统时清空）
    if (localStorage.getItem('themeSource') === 'manual') {
        localStorage.setItem('isDarkMode', darkMode)
    }
}

// 5. 处理手动切换
const handleThemeChange = (newVal) => {
    // 标记为「手动切换」，不再跟随系统
    localStorage.setItem('themeSource', 'manual')
    updateTheme(newVal)
}

// 6. 监听系统主题变化
const handleSystemThemeChange = (e) => {
    // 只有用户未手动切换过时，才跟随系统
    if (localStorage.getItem('themeSource') !== 'manual') {
        const systemDark = e.matches
        isDark.value = systemDark
        updateTheme(systemDark)
    }
}

// 7. 初始化逻辑
onMounted(() => {
    // 获取系统主题监听对象
    mediaQueryList = window.matchMedia('(prefers-color-scheme: dark)')
    // 监听系统主题变化
    mediaQueryList.addEventListener('change', handleSystemThemeChange)

    // 优先读取用户手动设置
    const themeSource = localStorage.getItem('themeSource')
    const savedDarkMode = localStorage.getItem('isDarkMode')

    if (themeSource === 'manual' && savedDarkMode) {
        // 有手动设置：使用用户选择的模式
        isDark.value = savedDarkMode === 'true'
    } else {
        // 无手动设置：跟随系统
        const systemDark = mediaQueryList.matches
        isDark.value = systemDark
        // 清空手动标记，确保后续能跟随系统
        localStorage.removeItem('themeSource')
    }

    // 初始化主题
    updateTheme(isDark.value)
})

// 8. 组件卸载时移除监听（防止内存泄漏）
onUnmounted(() => {
    if (mediaQueryList) {
        mediaQueryList.removeEventListener('change', handleSystemThemeChange)
    }
})

// 9. 监听 isDark 变化（兜底）
watch(isDark, (newVal) => {
    updateTheme(newVal)
})
</script>

<style scoped>
.app-container {
    padding: 20px;
    min-height: 100vh;
    transition: background-color 0.3s ease;
}

/* 自定义样式适配两种模式 */
.light-mode {
    background-color: #ffffff;
    color: #333333;
}

.dark-mode {
    background-color: #1e1e1e;
    color: #e5e5e5;
}
</style>