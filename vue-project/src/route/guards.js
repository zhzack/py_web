// router/guards.js
export function setupGuards(router) {
    router.beforeEach((to) => {
        if (to.meta.requiresAuth && !localStorage.getItem('token')) {
            return '/login'
        }
    })
}
