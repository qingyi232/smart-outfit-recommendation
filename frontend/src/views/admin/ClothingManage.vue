<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
      <h2 style="font-size:20px;font-weight:700;color:var(--text-primary)">服装管理</h2>
      <div style="display:flex;gap:12px">
        <el-select v-model="filterCat" clearable placeholder="全部分类" style="width:140px" @change="load">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-button type="primary" @click="openAdd"><el-icon><Plus /></el-icon>添加服装</el-button>
      </div>
    </div>

    <el-card shadow="never" style="border-radius:var(--radius-md)">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="55" />
        <el-table-column label="图片" width="80">
          <template #default="{row}">
            <el-image :src="row.image_url" style="width:50px;height:50px;border-radius:6px" fit="cover" />
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="140" />
        <el-table-column prop="category_name" label="分类" width="80" />
        <el-table-column prop="warmth_level" label="保暖" width="55" />
        <el-table-column prop="breathability" label="透气" width="55" />
        <el-table-column prop="waterproof" label="防水" width="55" />
        <el-table-column label="温度范围" width="100">
          <template #default="{row}">{{ row.min_temp }}°~{{ row.max_temp }}°</template>
        </el-table-column>
        <el-table-column label="场景" min-width="130">
          <template #default="{row}">
            <el-tag v-for="s in row.suitable_scenes" :key="s" size="small" style="margin:1px 2px">{{ s }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="130" fixed="right">
          <template #default="{row}">
            <el-button type="primary" link size="small" @click="openEdit(row)">编辑</el-button>
            <el-popconfirm title="确定删除？" @confirm="del(row.id)">
              <template #reference><el-button type="danger" link size="small">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <div style="text-align:right;margin-top:16px">
        <el-pagination background layout="total, prev, pager, next" :total="total" :page-size="10" v-model:current-page="page" @current-change="load" />
      </div>
    </el-card>

    <!-- 添加/编辑弹窗 -->
    <el-dialog v-model="dlgVisible" :title="editId ? '编辑服装' : '添加服装'" width="560px" destroy-on-close>
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category_id" style="width:100%">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="图片URL"><el-input v-model="form.image_url" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="2" /></el-form-item>
        <el-row :gutter="12">
          <el-col :span="6"><el-form-item label="保暖"><el-input-number v-model="form.warmth_level" :min="1" :max="5" size="small" style="width:100%" /></el-form-item></el-col>
          <el-col :span="6"><el-form-item label="透气"><el-input-number v-model="form.breathability" :min="1" :max="5" size="small" style="width:100%" /></el-form-item></el-col>
          <el-col :span="6"><el-form-item label="防水"><el-input-number v-model="form.waterproof" :min="1" :max="5" size="small" style="width:100%" /></el-form-item></el-col>
          <el-col :span="6"><el-form-item label="正式"><el-input-number v-model="form.formality" :min="1" :max="5" size="small" style="width:100%" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="最低温"><el-input-number v-model="form.min_temp" :min="-30" :max="40" size="small" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="最高温"><el-input-number v-model="form.max_temp" :min="-10" :max="50" size="small" style="width:100%" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="场景"><el-input v-model="form.suitable_scenes" placeholder="逗号分隔，如: 通勤,运动" /></el-form-item>
        <el-form-item label="适用性别">
          <el-select v-model="form.suitable_gender" style="width:100%">
            <el-option label="通用" value="all" /><el-option label="男" value="male" /><el-option label="女" value="female" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlgVisible=false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminApi, clothingApi } from '../../api'
import { ElMessage } from 'element-plus'

const list = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const filterCat = ref(null)
const categories = ref([])
const dlgVisible = ref(false)
const editId = ref(null)
const saving = ref(false)
const defaultForm = { name:'', category_id:null, image_url:'', description:'', warmth_level:3, breathability:3, waterproof:1, formality:3, min_temp:-10, max_temp:40, suitable_scenes:'通勤', suitable_gender:'all' }
const form = ref({...defaultForm})

async function load() {
  loading.value = true
  try {
    const r = await adminApi.getClothing({ page: page.value, per_page: 10, category_id: filterCat.value || undefined })
    list.value = r.data.items
    total.value = r.data.total
  } catch {} finally { loading.value = false }
}

function openAdd() { editId.value = null; form.value = {...defaultForm}; dlgVisible.value = true }
function openEdit(row) {
  editId.value = row.id
  form.value = { name: row.name, category_id: row.category_id, image_url: row.image_url, description: row.description, warmth_level: row.warmth_level, breathability: row.breathability, waterproof: row.waterproof, formality: row.formality, min_temp: row.min_temp, max_temp: row.max_temp, suitable_scenes: (row.suitable_scenes||[]).join(','), suitable_gender: row.suitable_gender }
  dlgVisible.value = true
}

async function save() {
  saving.value = true
  try {
    if (editId.value) await adminApi.updateClothing(editId.value, form.value)
    else await adminApi.addClothing(form.value)
    ElMessage.success('保存成功')
    dlgVisible.value = false
    load()
  } finally { saving.value = false }
}

async function del(id) {
  try { await adminApi.deleteClothing(id); ElMessage.success('删除成功'); load() } catch {}
}

onMounted(async () => {
  try { const r = await clothingApi.getCategories(); categories.value = r.data } catch {}
  load()
})
</script>
