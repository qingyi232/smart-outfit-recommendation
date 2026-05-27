<template>
  <div class="auth-page">
    <div class="auth-card">
      <div style="text-align:center;margin-bottom:16px">
        <el-icon :size="42" color="var(--primary)"><Sunny /></el-icon>
      </div>
      <h1 class="auth-title">智能出行穿衣服务</h1>
      <p class="auth-subtitle">基于环境信息感知的个性化穿衣推荐</p>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" size="large">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名 / 邮箱" :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" show-password :prefix-icon="Lock" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" style="width:100%" :loading="loading" @click="handleLogin">登 录</el-button>
        </el-form-item>
      </el-form>

      <div style="text-align:center;margin-top:12px">
        <span style="color:var(--text-secondary);font-size:14px">还没有账号？</span>
        <router-link to="/register" style="font-size:14px;font-weight:500">立即注册</router-link>
      </div>

      <el-divider>演示账号</el-divider>
      <div style="display:flex;gap:12px">
        <el-button style="flex:1" @click="fillDemo('zhangsan','123456')">普通用户</el-button>
        <el-button style="flex:1" @click="fillDemo('admin','admin123')">管理员</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, shallowRef } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, Sunny } from '@element-plus/icons-vue'
import { authApi } from '../../api'
import { useUserStore } from '../../stores'
import { ElMessage } from 'element-plus'

const router = useRouter()
const store = useUserStore()
const formRef = ref(null)
const loading = ref(false)
const form = ref({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

function fillDemo(u, p) {
  form.value.username = u
  form.value.password = p
}

async function handleLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await authApi.login(form.value)
    store.setAuth(res.data.token, res.data.user)
    ElMessage.success('登录成功')
    router.push(res.data.user.role === 'admin' ? '/admin' : '/')
  } finally {
    loading.value = false
  }
}
</script>
