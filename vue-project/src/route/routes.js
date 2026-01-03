// router/routes.js
import DefaultLayout from '@/components/layouts/DefaultLayout.vue'

export const routes = [
    {
        path: '/',
        component: DefaultLayout,   // 👈 外层
        redirect: '/dashboard',
        children: [
            {
                path: 'dashboard',
                component: () => import('@/views/dashboard/index.vue') // 👈 内层
            },
            {
                path: 'system/user',  // 👈 注册这个路由
                component: () => import('@/views/system/user/index.vue'),
                meta: { title: '用户管理' }
            }
        ]
    }
]