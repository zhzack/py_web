import http from './http'

export const deviceGroupsApi = {
  list() { return http.get('/v1/device-groups') },
  get(id) { return http.get(`/v1/device-groups/${id}`) },
  create(payload) { return http.post('/v1/device-groups', payload) },
  update(id, payload) { return http.put(`/v1/device-groups/${id}`, payload) },
  delete(id) { return http.delete(`/v1/device-groups/${id}`) },
  getDevices(id) { return http.get(`/v1/device-groups/${id}/devices`) },
  addDevices(id, device_ids) { return http.post(`/v1/device-groups/${id}/members`, { device_ids }) },
  removeDevice(id, device_id) { return http.delete(`/v1/device-groups/${id}/members/${device_id}`) },
  dispatch(id, payload, timeout_ms = 2000) {
    return http.post(`/v1/device-groups/${id}/dispatch`, { payload, timeout_ms })
  },
}
