<template>
  <div>
    <h2 style="font-size:20px;font-weight:700;margin-bottom:20px;color:var(--text-primary)">数据概览</h2>

    <!-- 统计卡片 -->
    <el-row :gutter="16" style="margin-bottom:24px">
      <el-col :xs="12" :sm="6" v-for="s in statCards" :key="s.label">
        <div class="stat-card">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div><div class="stat-value">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
            <el-icon :size="32" color="var(--primary-light)" style="opacity:0.7"><component :is="s.icon" /></el-icon>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-bottom:24px">
      <el-col :xs="12" :sm="6" v-for="s in statCards2" :key="s.label">
        <div class="stat-card">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div><div class="stat-value" style="color:var(--accent)">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
            <el-icon :size="32" color="var(--accent-light)" style="opacity:0.7"><component :is="s.icon" /></el-icon>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-card shadow="never" style="border-radius:var(--radius-md);margin-bottom:16px">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-weight:600">推荐趋势</span>
          <el-radio-group v-model="trendDays" size="small" @change="loadTrend">
            <el-radio-button :value="7">最近7天</el-radio-button>
            <el-radio-button :value="30">最近30天</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div ref="trendChartRef" style="height:300px"></div>
    </el-card>

    <el-row :gutter="16">
      <el-col :xs="24" :sm="12">
        <el-card shadow="never" style="border-radius:var(--radius-md);margin-bottom:16px">
          <template #header><span style="font-weight:600">场景使用分布</span></template>
          <div ref="sceneChartRef" style="height:280px"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12">
        <el-card shadow="never" style="border-radius:var(--radius-md);margin-bottom:16px">
          <template #header><span style="font-weight:600">城市热度排行</span></template>
          <div ref="cityChartRef" style="height:280px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" style="border-radius:var(--radius-md);margin-bottom:16px">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-weight:600">用户活跃度 TOP {{ activity.top_users.length }}</span>
          <span style="font-size:13px;color:var(--text-secondary)">
            今日活跃 <b style="color:var(--primary)">{{ activity.active_users_today }}</b> /
            总活跃 <b style="color:var(--primary)">{{ activity.total_active_users }}</b>
          </span>
        </div>
      </template>
      <el-table :data="activity.top_users" stripe size="small" style="width:100%">
        <el-table-column type="index" label="排名" width="60" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="nickname" label="昵称" width="120" />
        <el-table-column prop="city" label="城市" width="80" />
        <el-table-column prop="recommendation_count" label="推荐次数" width="100" sortable />
        <el-table-column prop="feedback_count" label="反馈次数" width="100" sortable />
        <el-table-column label="平均舒适度" min-width="200">
          <template #default="{row}">
            <div style="display:flex;align-items:center;gap:8px">
              <el-progress :percentage="row.avg_comfort_score" :stroke-width="10" :text-inside="true" color="var(--primary)" style="flex:1" />
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card shadow="never" style="border-radius:var(--radius-md);margin-bottom:16px">
      <template #header><span style="font-weight:600">最新注册用户</span></template>
      <el-table :data="data.recent_users" stripe size="small" style="width:100%">
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="nickname" label="昵称" />
        <el-table-column prop="city" label="城市" />
        <el-table-column prop="gender" label="性别"><template #default="{row}">{{ row.gender==='male'?'男':'女' }}</template></el-table-column>
        <el-table-column prop="created_at" label="注册时间" />
      </el-table>
    </el-card>

    <el-card shadow="never" style="border-radius:var(--radius-md)">
      <template #header><span style="font-weight:600">最新用户反馈</span></template>
      <el-table :data="data.recent_feedbacks" stripe size="small" style="width:100%">
        <el-table-column prop="user_id" label="用户ID" width="80" />
        <el-table-column prop="rating" label="评分" width="100">
          <template #default="{row}"><el-rate v-model="row.rating" disabled size="small" /></template>
        </el-table-column>
        <el-table-column prop="comment" label="评论" />
        <el-table-column prop="created_at" label="时间" width="170" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { adminApi } from '../../api'
import { User, Goods, DataLine, ChatDotSquare, Star, Odometer, UserFilled, TrendCharts } from '@element-plus/icons-vue'

const data = ref({ overview: {}, recent_users: [], recent_feedbacks: [], scene_stats: [], city_stats: [] })
const activity = ref({ top_users: [], active_users_today: 0, total_active_users: 0 })
const trendDays = ref(7)
const sceneChartRef = ref(null)
const cityChartRef = ref(null)
const trendChartRef = ref(null)
let sceneChart = null
let cityChart = null
let trendChart = null

const statCards = computed(() => {
  const o = data.value.overview
  return [
    { label: '注册用户', value: o.total_users || 0, icon: User },
    { label: '服装数量', value: o.total_clothes || 0, icon: Goods },
    { label: '推荐次数', value: o.total_recommendations || 0, icon: DataLine },
    { label: '反馈数量', value: o.total_feedbacks || 0, icon: ChatDotSquare },
  ]
})
const statCards2 = computed(() => {
  const o = data.value.overview
  return [
    { label: '平均评分', value: o.avg_rating || 0, icon: Star },
    { label: '平均舒适度', value: o.avg_comfort || 0, icon: Odometer },
    { label: '本周新用户', value: o.new_users_week || 0, icon: UserFilled },
    { label: '本周推荐', value: o.week_recommendations || 0, icon: TrendCharts },
  ]
})

function renderCharts() {
  if (sceneChartRef.value && data.value.scene_stats.length) {
    if (!sceneChart) sceneChart = echarts.init(sceneChartRef.value)
    sceneChart.setOption({
      color: ['#3a9d6e','#5bb88a','#e8985a','#5a8fa8','#7db3c9','#f0b88a','#99aa9f'],
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie', radius: ['40%','70%'], padAngle: 3, itemStyle: { borderRadius: 6 },
        data: data.value.scene_stats.map(s => ({ name: s.scene, value: s.count })),
        label: { fontSize: 12 }
      }]
    })
  }
  if (cityChartRef.value && data.value.city_stats.length) {
    if (!cityChart) cityChart = echarts.init(cityChartRef.value)
    const cs = data.value.city_stats
    cityChart.setOption({
      color: ['#3a9d6e'],
      tooltip: { trigger: 'axis' },
      grid: { left: 60, right: 20, top: 10, bottom: 30 },
      xAxis: { type: 'category', data: cs.map(c => c.city), axisLabel: { fontSize: 11 } },
      yAxis: { type: 'value', axisLabel: { fontSize: 11 } },
      series: [{ type: 'bar', data: cs.map(c => c.count), barWidth: 28, itemStyle: { borderRadius: [4,4,0,0] } }]
    })
  }
}

function renderTrendChart(trend) {
  if (!trendChartRef.value) return
  if (!trendChart) trendChart = echarts.init(trendChartRef.value)
  const dates = trend.map(d => d.date?.slice(5))
  const recs = trend.map(d => d.recommendations)
  const fbs = trend.map(d => d.feedbacks)
  const comfort = trend.map(d => d.avg_comfort)

  trendChart.setOption({
    color: ['#3a9d6e', '#e8985a', '#5a8fa8'],
    tooltip: { trigger: 'axis' },
    legend: { data: ['推荐次数', '反馈次数', '平均舒适度'], top: 0, textStyle: { fontSize: 12 } },
    grid: { left: 50, right: 50, top: 40, bottom: 40 },
    xAxis: {
      type: 'category', data: dates, axisLabel: { fontSize: 11 },
      axisLine: { lineStyle: { color: '#e4e7ed' } }
    },
    yAxis: [
      { type: 'value', name: '次数', position: 'left', nameTextStyle: { fontSize: 11 }, axisLabel: { fontSize: 11 } },
      { type: 'value', name: '舒适度', position: 'right', min: 0, max: 100, nameTextStyle: { fontSize: 11 }, axisLabel: { fontSize: 11, formatter: '{value}' } }
    ],
    series: [
      { name: '推荐次数', type: 'bar', data: recs, barWidth: 20, itemStyle: { borderRadius: [4, 4, 0, 0] } },
      { name: '反馈次数', type: 'bar', data: fbs, barWidth: 20, itemStyle: { borderRadius: [4, 4, 0, 0] } },
      { name: '平均舒适度', type: 'line', yAxisIndex: 1, data: comfort, smooth: true, symbol: 'circle', symbolSize: 7, lineStyle: { width: 2.5 } }
    ]
  })
}

async function loadTrend() {
  try {
    const r = await adminApi.getStatsTrend(trendDays.value)
    await nextTick()
    renderTrendChart(r.data)
  } catch {}
}

async function loadActivity() {
  try {
    const r = await adminApi.getUserActivity(10)
    activity.value = r.data
  } catch {}
}

function handleResize() {
  sceneChart?.resize()
  cityChart?.resize()
  trendChart?.resize()
}

onMounted(async () => {
  try {
    const r = await adminApi.getDashboard()
    data.value = r.data
    await nextTick()
    renderCharts()
  } catch {}
  loadTrend()
  loadActivity()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  sceneChart?.dispose(); sceneChart = null
  cityChart?.dispose(); cityChart = null
  trendChart?.dispose(); trendChart = null
})
</script>
