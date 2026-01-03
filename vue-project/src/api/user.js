// api/user.js
import request from '@/utils/request'

export function getUserList() {
    return request.get('/users')
}
