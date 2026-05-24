import http from './http'

export const authApi = {
  login(username, password) {
    const fd = new URLSearchParams()
    fd.append('username', username)
    fd.append('password', password)
    return http.post('/v1/auth/login', fd, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
  },
  register(username, password, role = 'user') {
    return http.post('/v1/auth/register', { username, password, role })
  },
  me() {
    return http.get('/v1/auth/me')
  },
}
