import http from './http'

export const macrosApi = {
  list() { return http.get('/v1/macros') },
  create(payload) { return http.post('/v1/macros', payload) },
  remove(id) { return http.delete(`/v1/macros/${id}`) },
}
