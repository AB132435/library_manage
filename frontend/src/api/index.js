import axios from 'axios'
import { useUserStore } from '../store/user'
import router from '../router'

const api = axios.create({
  // 开发环境优先使用 /api（配合Vite proxy），也可通过环境变量覆盖
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器：自动添加token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token && token !== 'undefined' && token.length > 10) {
    config.headers.Authorization = `Bearer ${token}`
  } else {
    // token无效时清理
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
  return config
}, error => Promise.reject(error))

// 响应拦截器：统一错误处理
api.interceptors.response.use(
  response => response,
  error => {
    const status = error.response?.status
    const msg = error.response?.data?.msg || error.response?.data?.message || error.message || '请求失败'
    
    if (status === 401) {
      console.error('[401 Unauthorized] Token无效或已过期，请重新登录')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    } else if (status === 301 || status === 302) {
      console.error(`[${status} Redirect] URL重定向导致请求失败，请检查后端strict_slashes配置`)
    } else if (status >= 500) {
      console.error(`[${status} Server Error]`, msg)
    } else if (status === 422) {
      console.error(`[422 Validation Error]`, msg)
    }
    
    return Promise.reject(error)
  }
)

export default api
