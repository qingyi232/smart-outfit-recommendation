<template>
  <div>
    <h2 style="font-size:20px;font-weight:700;margin-bottom:20px;color:var(--text-primary)">推荐记录</h2>

    <el-card shadow="never" style="border-radius:var(--radius-md)">
      <el-table :data="list" v-loading="loading" stripe size="small">
        <el-table-column prop="id" label="ID" width="55" />
        <el-table-column prop="username" label="用户" width="90" />
        <el-table-column prop="city" label="城市" width="70" />
        <el-table-column prop="scene" label="场景" width="70" />
        <el-table-column prop="date" label="日期" width="100" />
        <el-table-column prop="weather_text" label="天气" width="60" />
        <el-table-column prop="temperature" label="温度" width="60" />
        <el-table-column label="推荐搭配" min-width="250">
          <template #default="{row}">
            <template v-for="(item, key) in getOutfit(row.outfit)" :key="key">
              <el-tag size="small" style="margin:1px 2px">{{ labels[key] }}: {{ item.name }}</el-tag>
            </template>
          </template>
        </el-table-column>
        <el-table-column prop="comfort_score" label="舒适度" width="70" />
        <el-table-column prop="match_score" label="搭配分" width="70" />
        <el-table-column prop="algorithm_type" label="算法" width="100">
          <template #default="{row}"><el-tag type="info" size="small">{{ row.algorithm_type }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="160" />
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

const list = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const labels = { top:'上衣', bottom:'下装', outer:'外套', shoes:'鞋子', accessory:'配饰' }

function getOutfit(o) {
  if (!o) return {}
  const r = {}
  for (const k of ['top','bottom','outer','shoes','accessory']) { if (o[k]) r[k] = o[k] }
  return r
}

async function load() {
  loading.value = true
  try {
    const r = await adminApi.getRecommendations({ page: page.value, per_page: 10 })
    list.value = r.data.items
    total.value = r.data.total
  } catch {} finally { loading.value = false }
}

onMounted(load)
</script>
