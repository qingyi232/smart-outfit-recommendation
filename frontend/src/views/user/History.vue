<template>
  <div class="page-container">
    <h2 style="font-size:20px;font-weight:700;margin-bottom:20px;color:var(--text-primary)">推荐历史</h2>

    <div v-if="loading" style="text-align:center;padding:40px"><el-skeleton :rows="6" animated /></div>
    <div v-else-if="list.length">
      <el-timeline>
        <el-timeline-item v-for="r in list" :key="r.id" :timestamp="r.created_at" placement="top"
          :color="r.comfort_score >= 80 ? 'var(--primary)' : 'var(--accent)'">
          <el-card shadow="never" style="border-radius:var(--radius-md)">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px">
              <div style="flex:1;min-width:0">
                <div style="font-weight:600;font-size:15px;margin-bottom:6px">
                  {{ r.city }} · {{ r.scene }} · {{ r.weather_text }} {{ r.temperature }}°C
                </div>
                <div style="font-size:13px;color:var(--text-secondary);margin-bottom:8px">{{ r.advice_text }}</div>
                <div style="display:flex;gap:8px;flex-wrap:wrap">
                  <template v-for="(item, key) in getOutfitList(r.outfit)" :key="key">
                    <el-tag size="small" :type="key === 'outer' ? 'warning' : ''">{{ slotLabel(key) }}: {{ item.name }}</el-tag>
                  </template>
                </div>
              </div>
              <div style="text-align:right;min-width:100px;display:flex;flex-direction:column;align-items:flex-end;gap:8px">
                <div>
                  <div style="font-size:13px;color:var(--text-secondary)">舒适度</div>
                  <div style="font-size:22px;font-weight:600;color:var(--primary)">{{ r.comfort_score }}</div>
                </div>
                <el-popconfirm title="确定删除这条推荐记录？" @confirm="handleDelete(r.id)" width="200">
                  <template #reference>
                    <el-button type="danger" link size="small"><el-icon><Delete /></el-icon>删除</el-button>
                  </template>
                </el-popconfirm>
              </div>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>

      <div style="text-align:center;margin-top:20px">
        <el-pagination background layout="prev, pager, next" :total="total" :page-size="pageSize" v-model:current-page="page" @current-change="load" />
      </div>
    </div>
    <el-empty v-else description="暂无推荐记录" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { recommendApi } from '../../api'
import { ElMessage } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'

const list = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = 10
const total = ref(0)

const LABELS = { top:'上衣', bottom:'下装', outer:'外套', shoes:'鞋子', accessory:'配饰' }
function slotLabel(k) { return LABELS[k] || k }
function getOutfitList(outfit) {
  if (!outfit) return {}
  const r = {}
  for (const k of ['top','bottom','outer','shoes','accessory']) { if (outfit[k]) r[k] = outfit[k] }
  return r
}

async function load() {
  loading.value = true
  try {
    const r = await recommendApi.getHistory(page.value, pageSize)
    list.value = r.data.items
    total.value = r.data.total
  } catch {} finally { loading.value = false }
}

async function handleDelete(id) {
  try {
    await recommendApi.deleteHistory(id)
    ElMessage.success('已删除')
    if (list.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch {}
}

onMounted(load)
</script>
