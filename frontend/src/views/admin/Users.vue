<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
      <h2 style="font-size:20px;font-weight:700;color:var(--text-primary)">用户管理</h2>
      <el-input v-model="keyword" placeholder="搜索用户名/邮箱" clearable style="width:240px" @keyup.enter="load" @clear="load">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
    </div>

    <el-card shadow="never" style="border-radius:var(--radius-md)">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="nickname" label="昵称" width="100" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="gender" label="性别" width="60">
          <template #default="{row}">{{ row.gender === 'male' ? '男' : row.gender === 'female' ? '女' : '未知' }}</template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" width="60" />
        <el-table-column prop="city" label="城市" width="80" />
        <el-table-column prop="body_type" label="体质" width="80">
          <template #default="{row}">{{ {'cold_sensitive':'怕冷','normal':'普通','heat_sensitive':'怕热'}[row.body_type] }}</template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="70">
          <template #default="{row}"><el-tag :type="row.role==='admin'?'danger':''" size="small">{{ row.role==='admin'?'管理员':'用户' }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="70">
          <template #default="{row}"><el-tag :type="row.is_active?'success':'info'" size="small">{{ row.is_active?'正常':'禁用' }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="170" />
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{row}">
            <el-button v-if="row.role!=='admin'" type="warning" link size="small" @click="toggle(row)">{{ row.is_active?'禁用':'启用' }}</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="text-align:right;margin-top:16px">
        <el-pagination background layout="total, prev, pager, next" :total="total" :page-size="10" v-model:current-page="page" @current-change="load" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminApi } from '../../api'
import { ElMessage } from 'element-plus'

const list = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const keyword = ref('')

async function load() {
  loading.value = true
  try {
    const r = await adminApi.getUsers({ page: page.value, per_page: 10, keyword: keyword.value })
    list.value = r.data.items
    total.value = r.data.total
  } catch {} finally { loading.value = false }
}

async function toggle(row) {
  try {
    await adminApi.toggleUser(row.id)
    ElMessage.success('操作成功')
    load()
  } catch {}
}

onMounted(load)
</script>
