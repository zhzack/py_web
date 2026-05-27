import http from './http'

export const devicesApi = {
  list() { return http.get('/v1/devices') },
  get(id) { return http.get(`/v1/devices/${id}`) },
  create(payload) { return http.post('/v1/devices', payload) },
  update(id, payload) { return http.put(`/v1/devices/${id}`, payload) },
  claim(id) { return http.post(`/v1/devices/${id}/claim`) },
  online() { return http.get('/v1/devices/online') },
}
