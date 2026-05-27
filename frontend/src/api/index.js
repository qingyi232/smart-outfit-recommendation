import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  res => res.data,
  err => {
    const msg = err.response?.data?.msg || '请求失败'
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    } else {
      ElMessage.error(msg)
    }
    return Promise.reject(err)
  }
)

export const authApi = {
  login: data => api.post('/auth/login', data),
  register: data => api.post('/auth/register', data),
  getProfile: () => api.get('/auth/profile'),
  updateProfile: data => api.put('/auth/profile', data),
  changePassword: data => api.post('/auth/change-password', data),
}

export const weatherApi = {
  getCurrent: city => api.get('/weather/now', { params: { city } }),
  getForecast: (city, days = 7) => api.get('/weather/forecast', { params: { city, days } }),
  getCities: () => api.get('/weather/cities'),
  getComfort: (temp, humidity, wind) => api.get('/weather/comfort', { params: { temp, humidity, wind } }),
}

export const recommendApi = {
  generate: data => api.post('/recommend/generate', data),
  getToday: (city, scene, model_type = 'standard') => api.get('/recommend/today', { params: { city, scene, model_type } }),
  getHistory: (page = 1, per_page = 10) => api.get('/recommend/history', { params: { page, per_page } }),
  feedback: data => api.post('/recommend/feedback', data),
  getScenes: () => api.get('/recommend/scenes'),
  getModels: () => api.get('/recommend/models'),
  deleteHistory: id => api.delete(`/recommend/history/${id}`),
}

export const clothingApi = {
  getCategories: () => api.get('/clothing/categories'),
  getList: (params) => api.get('/clothing/list', { params }),
  getDetail: id => api.get(`/clothing/${id}`),
}

export const userApi = {
  getDashboard: () => api.get('/user/dashboard'),
  getPreferences: () => api.get('/user/preferences'),
  updatePreference: data => api.post('/user/preferences', data),
}

export const adminApi = {
  getDashboard: () => api.get('/admin/dashboard'),
  getUsers: params => api.get('/admin/users', { params }),
  toggleUser: uid => api.put(`/admin/users/${uid}/toggle`),
  getClothing: params => api.get('/admin/clothing', { params }),
  addClothing: data => api.post('/admin/clothing', data),
  updateClothing: (id, data) => api.put(`/admin/clothing/${id}`, data),
  deleteClothing: id => api.delete(`/admin/clothing/${id}`),
  getWeatherRecords: params => api.get('/admin/weather/records', { params }),
  getRecommendations: params => api.get('/admin/recommendations', { params }),
  getStatsTrend: (days = 30) => api.get('/admin/stats/trend', { params: { days } }),
  getUserActivity: (top = 10) => api.get('/admin/stats/user-activity', { params: { top } }),
}

export default api
