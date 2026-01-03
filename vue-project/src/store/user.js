import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
    state: () => ({
        name: 'admin'
    }),
    actions: {
        setName(newName) {
            this.name = newName
        }
    }
})
