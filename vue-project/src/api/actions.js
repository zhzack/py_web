import http from './http'

export const actionsApi = {
  send(payload) { return http.post('/v2/action', payload) },
  recentLogs(limit = 100) { return http.get('/v2/logs', { params: { limit } }) },
}
