<template>
  <div class="page-container" style="max-width:700px">
    <h2 style="font-size:20px;font-weight:700;margin-bottom:24px;color:var(--text-primary)">个人中心</h2>

    <!-- 统计卡片 -->
    <el-row :gutter="16" style="margin-bottom:24px">
      <el-col :span="8">
        <div class="stat-card" style="text-align:center">
          <div class="stat-value">{{ stats.total_recommendations }}</div>
          <div class="stat-label">累计推荐</div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="stat-card" style="text-align:center">
          <div class="stat-value">{{ stats.total_feedbacks }}</div>
          <div class="stat-label">反馈次数</div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="stat-card" style="text-align:center">
          <div class="stat-value">{{ stats.avg_comfort_score }}</div>
          <div class="stat-label">平均舒适度</div>
        </div>
      </el-col>
    </el-row>

    <!-- 个人信息表单 -->
    <el-card shadow="never" style="border-radius:var(--radius-md)">
      <template #header><span style="font-weight:600">个人信息</span></template>
      <el-form :model="form" label-width="90px" label-position="right">
        <el-form-item label="用户名"><el-input :value="form.username" disabled /></el-form-item>
        <el-form-item label="邮箱"><el-input :value="form.email" disabled /></el-form-item>
        <el-form-item label="昵称"><el-input v-model="form.nickname" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="性别">
              <el-select v-model="form.gender" style="width:100%">
                <el-option label="男" value="male" /><el-option label="女" value="female" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="年龄"><el-input-number v-model="form.age" :min="10" :max="100" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="所在城市">
              <el-select v-model="form.city" filterable style="width:100%">
                <el-option v-for="c in cities" :key="c" :label="c" :value="c" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="体质类型">
              <el-select v-model="form.body_type" style="width:100%">
                <el-option label="怕冷体质" value="cold_sensitive" />
                <el-option label="普通体质" value="normal" />
                <el-option label="怕热体质" value="heat_sensitive" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="save">保存修改</el-button>
          <el-button @click="pwdVisible = true"><el-icon><Lock /></el-icon>修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-dialog v-model="pwdVisible" title="修改密码" width="420px" destroy-on-close>
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="90px">
        <el-form-item label="旧密码" prop="old_password">
          <el-input v-model="pwdForm.old_password" type="password" show-password placeholder="请输入当前密码" />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password placeholder="至少6位" />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input v-model="pwdForm.confirm_password" type="password" show-password placeholder="再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdVisible = false">取消</el-button>
        <el-button type="primary" :loading="pwdSaving" @click="savePassword">确 定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { authApi, userApi, weatherApi } from '../../api'
import { useUserStore } from '../../stores'
import { ElMessage } from 'element-plus'
import { Lock } from '@element-plus/icons-vue'

const store = useUserStore()
const saving = ref(false)
const cities = ref(['北京','上海','广州','深圳','成都','杭州','武汉','南京','重庆'])
const stats = ref({ total_recommendations: 0, total_feedbacks: 0, avg_comfort_score: 0 })
const form = ref({ username:'', email:'', nickname:'', gender:'male', age:25, city:'北京', body_type:'normal' })

const pwdVisible = ref(false)
const pwdSaving = ref(false)
const pwdFormRef = ref(null)
const pwdForm = ref({ old_password: '', new_password: '', confirm_password: '' })
const pwdRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '新密码至少6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: (_, v, cb) => v === pwdForm.value.new_password ? cb() : cb(new Error('两次密码不一致')), trigger: 'blur' }
  ]
}

onMounted(async () => {
  try { const r = await weatherApi.getCities(); if (r.data) cities.value = r.data } catch {}
  try {
    const r = await userApi.getDashboard()
    stats.value = r.data.stats
    const u = r.data.user
    form.value = { username: u.username, email: u.email, nickname: u.nickname, gender: u.gender, age: u.age, city: u.city, body_type: u.body_type }
  } catch {}
})

async function save() {
  saving.value = true
  try {
    const r = await authApi.updateProfile({ nickname: form.value.nickname, gender: form.value.gender, age: form.value.age, city: form.value.city, body_type: form.value.body_type })
    store.updateUser(r.data)
    ElMessage.success('保存成功')
  } finally { saving.value = false }
}

async function savePassword() {
  await pwdFormRef.value.validate()
  pwdSaving.value = true
  try {
    await authApi.changePassword({
      old_password: pwdForm.value.old_password,
      new_password: pwdForm.value.new_password,
    })
    ElMessage.success('密码修改成功，请重新登录')
    pwdVisible.value = false
    pwdForm.value = { old_password: '', new_password: '', confirm_password: '' }
    setTimeout(() => { store.logout(); location.href = '/login' }, 1000)
  } finally { pwdSaving.value = false }
}
</script>
