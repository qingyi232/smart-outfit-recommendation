<template>
  <div class="app-container">
    <el-header style="background:var(--bg-card);border-bottom:1px solid var(--border-light);display:flex;align-items:center;justify-content:space-between;padding:0 24px;height:60px;box-shadow:var(--shadow-sm)">
      <div style="display:flex;align-items:center;gap:8px;cursor:pointer" @click="$router.push('/')">
        <el-icon :size="26" color="var(--primary)"><Sunny /></el-icon>
        <span style="font-size:17px;font-weight:700;color:var(--text-primary)">智能穿衣助手</span>
      </div>
      <el-menu mode="horizontal" :default-active="route.path" :ellipsis="false" router style="border:none;height:60px">
        <el-menu-item index="/"><el-icon><HomeFilled /></el-icon>首页推荐</el-menu-item>
        <el-menu-item index="/forecast"><el-icon><Cloudy /></el-icon>天气预报</el-menu-item>
        <el-menu-item index="/history"><el-icon><Clock /></el-icon>推荐历史</el-menu-item>
        <el-menu-item index="/profile"><el-icon><UserFilled /></el-icon>个人中心</el-menu-item>
      </el-menu>
      <div style="display:flex;align-items:center;gap:12px">
        <el-select v-model="city" filterable size="default" style="width:110px" @change="onCityChange">
          <el-option v-for="c in cities" :key="c" :label="c" :value="c" />
        </el-select>
        <el-dropdown @command="handleCmd">
          <span style="cursor:pointer;display:flex;align-items:center;gap:6px;color:var(--text-primary)">
            <el-avatar :size="32" style="background:var(--primary)">{{ store.userInfo?.nickname?.[0] || 'U' }}</el-avatar>
            <span style="font-size:14px">{{ store.userInfo?.nickname || '用户' }}</span>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-if="store.isAdmin" command="admin">管理后台</el-dropdown-item>
              <el-dropdown-item command="profile">个人设置</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    <main style="flex:1;overflow-y:auto">
      <router-view :city="city" />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../../stores'
import { weatherApi } from '../../api'

const route = useRoute()
const router = useRouter()
const store = useUserStore()
const city = ref(store.currentCity)
const cities = ref(['北京','上海','广州','深圳','成都','杭州','武汉','南京','重庆','西安'])

onMounted(async () => {
  try { const r = await weatherApi.getCities(); if (r.data) cities.value = r.data } catch {}
})
function onCityChange(v) { city.value = v }
function handleCmd(cmd) {
  if (cmd === 'logout') { store.logout(); router.push('/login') }
  else if (cmd === 'admin') router.push('/admin')
  else if (cmd === 'profile') router.push('/profile')
}
</script>
