import axios from 'axios'

const api = axios.create({ timeout: 120000 })
let backendBase = ''

export async function configureApi() {
  if (window.desktop?.backendConfig) {
    const config = await window.desktop.backendConfig()
    backendBase = config.url
    api.defaults.baseURL = config.url
    if (config.token) api.defaults.headers.common['X-StoreX-Token'] = config.token
  }
  return api
}

export function apiError(error, fallback = '操作失败') {
  const detail = error?.response?.data?.detail
  if (Array.isArray(detail)) return detail.map(item => item?.msg || String(item)).join('；')
  return detail || error?.response?.data?.message || error?.message || fallback
}

export function outputUrl(relative) {
  if (!relative) return ''
  if (/^https?:/i.test(relative)) return relative
  return `${backendBase}${relative}`
}

export default api
