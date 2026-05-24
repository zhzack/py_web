/**
 * 通用 WebSocket composable：自动重连 + envelope 协议封装。
 *
 * useWs('/ws/client', { token })
 *   .onMessage(handler)
 *   .send({ header: { type: 'action', msg_id: ..., timeout_ms: 2000 }, routing: {...}, payload: {...} })
 */
import { onUnmounted, ref } from 'vue'

export function useWs(path, { token, autoReconnect = true, reconnectMs = 3000 } = {}) {
  const status = ref('idle')         // idle | connecting | open | closed
  const lastError = ref(null)
  const messageHandlers = []
  let ws = null
  let reconnectTimer = null
  let stopped = false

  function buildUrl() {
    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = location.host
    const t = token?.value ?? token
    const q = t ? `?token=${encodeURIComponent(t)}` : ''
    return `${proto}//${host}${path}${q}`
  }

  function connect() {
    if (stopped) return
    status.value = 'connecting'
    ws = new WebSocket(buildUrl())
    ws.onopen = () => { status.value = 'open' }
    ws.onmessage = (e) => {
      let data
      try { data = JSON.parse(e.data) } catch { data = e.data }
      messageHandlers.forEach((fn) => fn(data))
    }
    ws.onerror = (e) => { lastError.value = e }
    ws.onclose = () => {
      status.value = 'closed'
      ws = null
      if (autoReconnect && !stopped) {
        reconnectTimer = setTimeout(connect, reconnectMs)
      }
    }
  }

  function send(obj) {
    if (ws && ws.readyState === 1) {
      ws.send(typeof obj === 'string' ? obj : JSON.stringify(obj))
      return true
    }
    return false
  }

  function close() {
    stopped = true
    if (reconnectTimer) clearTimeout(reconnectTimer)
    if (ws) ws.close()
  }

  function onMessage(fn) {
    messageHandlers.push(fn)
    return api
  }

  onUnmounted(close)

  const api = { status, lastError, send, close, onMessage, connect }
  connect()
  return api
}
