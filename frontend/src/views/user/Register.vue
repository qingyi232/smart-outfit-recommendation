<template>
  <div class="auth-page">
    <div class="auth-card">
      <div style="text-align:center;margin-bottom:16px">
        <el-icon :size="42" color="var(--primary)"><Sunny /></el-icon>
      </div>
      <h1 class="auth-title">创建账号</h1>
      <p class="auth-subtitle">加入智能出行穿衣服务平台</p>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" size="large">
        <el-form-item prop="username" label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item prop="email" label="邮箱">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item prop="password" label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item prop="gender" label="性别">
              <el-select v-model="form.gender" style="width:100%">
                <el-option label="男" value="male" />
                <el-option label="女" value="female" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="age" label="年龄">
              <el-input-number v-model="form.age" :min="10" :max="100" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item prop="city" label="所在城市">
              <el-select v-model="form.city" filterable style="width:100%">
                <el-option v-for="c in cities" :key="c" :label="c" :value="c" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="body_type" label="体质类型">
              <el-select v-model="form.body_type" style="width:100%">
                <el-option label="怕冷体质" value="cold_sensitive" />
                <el-option label="普通体质" value="normal" />
                <el-option label="怕热体质" value="heat_sensitive" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" style="width:100%" :loading="loading" @click="handleRegister">注 册</el-button>
        </el-form-item>
      </el-form>

      <div style="text-align:center;margin-top:8px">
        <span style="color:var(--text-secondary);font-size:14px">已有账号？</span>
        <router-link to="/login" style="font-size:14px;font-weight:500">返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Sunny } from '@element-plus/icons-vue'
import { authApi, weatherApi } from '../../api'
import { useUserStore } from '../../stores'
import { ElMessage } from 'element-plus'

const router = useRouter()
const store = useUserStore()
const formRef = ref(null)
const loading = ref(false)
const cities = ref(['北京','上海','广州','深圳','成都','杭州','武汉','南京','重庆','西安','长沙','天津'])

const form = ref({
  username: '', email: '', password: '',
  gender: 'male', age: 25, city: '北京', body_type: 'normal',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }, { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码至少6位', trigger: 'blur' }],
}

onMounted(async () => {
  try {
    const res = await weatherApi.getCities()
    if (res.data) cities.value = res.data
  } catch {}
})

async function handleRegister() {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await authApi.register(form.value)
    store.setAuth(res.data.token, res.data.user)
    ElMessage.success('注册成功')
    router.push('/')
  } finally {
    loading.value = false
  }
}
</script>
