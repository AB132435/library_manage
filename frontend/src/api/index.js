import axios from 'axios'
import router from '../router'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  // 过滤掉无效token（比如旧代码保存的"undefined"字符串）
  if (token && token !== 'undefined' && token.length > 10) {
    config.headers.Authorization = `Bearer ${token}`
  } else {
    // 如果token无效，清理localStorage
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
  return config
})

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401 || error.response?.status === 422) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default api
