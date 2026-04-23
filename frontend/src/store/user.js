import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  // 清理之前错误保存的"undefined" token
  let savedToken = localStorage.getItem('token')
  if (!savedToken || savedToken === 'undefined' || savedToken.length < 10) {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    savedToken = ''
  }
  const token = ref(savedToken || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role_id === 1)
  const isReader = computed(() => user.value?.role_id === 2)
  const isAuditor = computed(() => user.value?.role_id === 3)

  function setAuth(newToken, userData) {
    token.value = newToken
    user.value = userData
    localStorage.setItem('token', newToken)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return {
    token,
    user,
    isAuthenticated,
    isAdmin,
    isReader,
    isAuditor,
    setAuth,
    logout
  }
})
