import { createRouter, createWebHistory } from 'vue-router'

import UserLayout from '../views/user/Layout.vue'
import Home from '../views/user/Home.vue'
import Forecast from '../views/user/Forecast.vue'
import History from '../views/user/History.vue'
import Profile from '../views/user/Profile.vue'
import AdminLayout from '../views/admin/Layout.vue'
import Dashboard from '../views/admin/Dashboard.vue'
import Users from '../views/admin/Users.vue'
import ClothingManage from '../views/admin/ClothingManage.vue'
import WeatherMonitor from '../views/admin/WeatherMonitor.vue'
import Recommendations from '../views/admin/Recommendations.vue'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/user/Login.vue'), meta: { guest: true } },
  { path: '/register', name: 'Register', component: () => import('../views/user/Register.vue'), meta: { guest: true } },
  {
    path: '/',
    component: UserLayout,
    meta: { auth: true },
    children: [
      { path: '', name: 'Home', component: Home },
      { path: 'forecast', name: 'Forecast', component: Forecast },
      { path: 'history', name: 'History', component: History },
      { path: 'profile', name: 'Profile', component: Profile },
    ],
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { auth: true, admin: true },
    children: [
      { path: '', name: 'AdminDashboard', component: Dashboard },
      { path: 'users', name: 'AdminUsers', component: Users },
      { path: 'clothing', name: 'AdminClothing', component: ClothingManage },
      { path: 'weather', name: 'AdminWeather', component: WeatherMonitor },
      { path: 'recommendations', name: 'AdminRecommendations', component: Recommendations },
    ],
  },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || 'null')

  if (to.meta.auth && !token) return next('/login')
  if (to.meta.admin && user?.role !== 'admin') return next('/')
  if (to.meta.guest && token) return next('/')
  next()
})

export default router
