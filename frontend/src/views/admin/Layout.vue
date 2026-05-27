<template>
  <div class="admin-layout">
    <aside class="admin-sidebar">
      <div class="logo-area">
        <el-icon :size="20" style="margin-right:6px"><Sunny /></el-icon>管理后台
      </div>
      <el-menu :default-active="route.path" router style="border:none">
        <el-menu-item index="/admin"><el-icon><DataAnalysis /></el-icon><span>数据概览</span></el-menu-item>
        <el-menu-item index="/admin/users"><el-icon><User /></el-icon><span>用户管理</span></el-menu-item>
        <el-menu-item index="/admin/clothing"><el-icon><Goods /></el-icon><span>服装管理</span></el-menu-item>
        <el-menu-item index="/admin/weather"><el-icon><Cloudy /></el-icon><span>天气监控</span></el-menu-item>
        <el-menu-item index="/admin/recommendations"><el-icon><List /></el-icon><span>推荐记录</span></el-menu-item>
      </el-menu>
    </aside>
    <div class="admin-main">
      <header class="admin-header">
        <span style="font-size:15px;color:var(--text-secondary)">智能出行穿衣服务系统 · 管理控制台</span>
        <div style="display:flex;align-items:center;gap:12px">
          <el-button text @click="$router.push('/')"><el-icon><HomeFilled /></el-icon>返回前台</el-button>
          <el-dropdown @command="cmd => { if(cmd==='logout'){store.logout();$router.push('/login')} }">
            <span style="cursor:pointer;display:flex;align-items:center;gap:6px">
              <el-avatar :size="30" style="background:var(--primary)">{{ store.userInfo?.nickname?.[0] || 'A' }}</el-avatar>
              <span style="font-size:14px">{{ store.userInfo?.nickname }}</span>
            </span>
            <template #dropdown><el-dropdown-menu><el-dropdown-item command="logout">退出登录</el-dropdown-item></el-dropdown-menu></template>
          </el-dropdown>
        </div>
      </header>
      <div class="admin-content"><router-view /></div>
    </div>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../../stores'
const route = useRoute()
const store = useUserStore()
</script>
