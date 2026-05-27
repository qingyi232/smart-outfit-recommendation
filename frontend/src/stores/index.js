import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')
  const currentCity = computed(() => userInfo.value?.city || '北京')

  function setAuth(t, u) {
    token.value = t
    userInfo.value = u
    localStorage.setItem('token', t)
    localStorage.setItem('user', JSON.stringify(u))
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  function updateUser(u) {
    userInfo.value = u
    localStorage.setItem('user', JSON.stringify(u))
  }

  return { token, userInfo, isLoggedIn, isAdmin, currentCity, setAuth, logout, updateUser }
})
