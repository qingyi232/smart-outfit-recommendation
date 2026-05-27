<template>
  <div class="page-container">
    <h2 style="font-size:20px;font-weight:700;margin-bottom:20px;color:var(--text-primary)">未来天气与穿衣规划</h2>

    <el-row :gutter="16">
      <el-col :span="24">
        <div style="display:flex;gap:12px;overflow-x:auto;padding-bottom:8px">
          <div v-for="(d, i) in forecast" :key="i"
            class="stat-card" style="min-width:150px;cursor:pointer;text-align:center"
            :style="selected === i ? {border:'2px solid var(--primary)',background:'var(--primary-lighter)'} : {}"
            @click="selected = i">
            <div style="font-size:13px;color:var(--text-secondary)">{{ d.date }}</div>
            <div style="margin:8px 0">
              <el-icon :size="28" :color="getWeatherColor(d.weather_text)"><component :is="getWeatherIcon(d.weather_text)" /></el-icon>
            </div>
            <div style="font-size:22px;font-weight:600;color:var(--text-primary)">{{ d.temp_max }}°</div>
            <div style="font-size:13px;color:var(--text-light)">{{ d.temp_min }}°</div>
            <div style="font-size:12px;color:var(--text-secondary);margin-top:4px">{{ d.weather_text }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-card shadow="never" style="border-radius:var(--radius-md);margin-top:20px" v-if="forecast.length">
      <template #header>
        <div style="display:flex;align-items:center;gap:8px">
          <el-icon color="var(--primary)"><TrendCharts /></el-icon>
          <span style="font-weight:600">7天温度趋势</span>
          <span style="font-size:12px;color:var(--text-light);margin-left:auto">最高温 / 最低温 / 体感温</span>
        </div>
      </template>
      <div ref="trendChartRef" style="height:300px"></div>
    </el-card>

    <div v-if="detail" style="margin-top:24px">
      <el-card shadow="never" style="border-radius:var(--radius-md)">
        <template #header>
          <div style="display:flex;justify-content:space-between;align-items:center">
            <span style="font-weight:600">{{ detail.date }} 天气详情</span>
            <span style="color:var(--text-secondary);font-size:14px">
              <el-icon :size="16" style="vertical-align:middle;margin-right:4px"><component :is="getWeatherIcon(detail.weather_text)" /></el-icon>{{ detail.weather_text }}
            </span>
          </div>
        </template>
        <el-row :gutter="20">
          <el-col :xs="12" :sm="6">
            <div style="text-align:center;padding:12px 0">
              <el-icon :size="20" color="var(--primary)"><Odometer /></el-icon>
              <div style="font-size:13px;color:var(--text-secondary);margin-top:4px">温度范围</div>
              <div style="font-size:20px;font-weight:600;color:var(--primary);margin-top:4px">{{ detail.temp_min }}° ~ {{ detail.temp_max }}°</div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div style="text-align:center;padding:12px 0">
              <el-icon :size="20" color="var(--secondary)"><Filter /></el-icon>
              <div style="font-size:13px;color:var(--text-secondary);margin-top:4px">湿度</div>
              <div style="font-size:20px;font-weight:600;color:var(--secondary);margin-top:4px">{{ detail.humidity }}%</div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div style="text-align:center;padding:12px 0">
              <el-icon :size="20" color="var(--accent)"><WindPower /></el-icon>
              <div style="font-size:13px;color:var(--text-secondary);margin-top:4px">风速</div>
              <div style="font-size:20px;font-weight:600;color:var(--accent);margin-top:4px">{{ detail.wind_speed }} km/h</div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div style="text-align:center;padding:12px 0">
              <el-icon :size="20" :color="detail.aqi > 100 ? '#e74c3c' : 'var(--primary)'"><View /></el-icon>
              <div style="font-size:13px;color:var(--text-secondary);margin-top:4px">空气质量</div>
              <div style="font-size:20px;font-weight:600;margin-top:4px" :style="{color: detail.aqi>100?'#e74c3c':'var(--primary)'}">{{ detail.aqi_level }}</div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <div style="margin-top:20px">
        <h3 style="font-size:16px;font-weight:600;margin-bottom:12px">穿衣建议</h3>
        <el-alert :title="getAdvice(detail)" type="success" show-icon :closable="false" style="border-radius:var(--radius-md)" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { weatherApi } from '../../api'
import { Sunny, Cloudy, Pouring, Lightning, IceDrink, MostlyCloudy, Odometer, Filter, WindPower, View, TrendCharts } from '@element-plus/icons-vue'

const props = defineProps({ city: { type: String, default: '北京' } })
const forecast = ref([])
const selected = ref(0)
const detail = computed(() => forecast.value[selected.value] || null)
const trendChartRef = ref(null)
let trendChart = null

const WEATHER_ICON_MAP = {
  '晴': Sunny, '多云': Cloudy, '阴': MostlyCloudy,
  '小雨': Pouring, '中雨': Pouring, '大雨': Pouring, '雷阵雨': Lightning,
  '小雪': IceDrink, '中雪': IceDrink, '雨夹雪': IceDrink, '雾': View,
}
const WEATHER_COLOR_MAP = {
  '晴': '#e8985a', '多云': '#5a8fa8', '阴': '#99aa9f',
  '小雨': '#5a8fa8', '中雨': '#3d7a9a', '大雨': '#2d5f7a', '雷阵雨': '#7a5a3d',
  '小雪': '#7db3c9', '中雪': '#5a8fa8', '雨夹雪': '#6a9aaa', '雾': '#99aa9f',
}
function getWeatherIcon(t) { return WEATHER_ICON_MAP[t] || Sunny }
function getWeatherColor(t) { return WEATHER_COLOR_MAP[t] || 'var(--primary)' }

function getAdvice(w) {
  const t = w.temperature || (w.temp_min + w.temp_max) / 2
  let a = ''
  if (t < 5) a = '天气寒冷，建议穿厚羽绒服、毛衣、保暖裤，佩戴围巾手套'
  else if (t < 12) a = '天气较冷，建议穿大衣或厚外套搭配毛衣、长裤'
  else if (t < 18) a = '温度偏凉，建议穿薄外套或卫衣搭配长裤'
  else if (t < 25) a = '温度舒适，穿轻薄外套或长袖即可'
  else if (t < 30) a = '天气温暖，穿T恤或衬衫搭配薄裤即可'
  else a = '天气炎热，建议穿短袖短裤，注意防晒补水'
  if (w.precipitation > 5) a += '；有降水，请携带雨伞'
  if (w.wind_speed > 15) a += '；风力较大，注意防风'
  return a
}

function renderTrendChart() {
  if (!trendChartRef.value || !forecast.value.length) return
  if (!trendChart) {
    trendChart = echarts.init(trendChartRef.value)
  }
  const dates = forecast.value.map(d => d.date?.slice(5))
  const maxTemps = forecast.value.map(d => d.temp_max)
  const minTemps = forecast.value.map(d => d.temp_min)
  const feelsLike = forecast.value.map(d => d.feels_like)

  trendChart.setOption({
    color: ['#e8985a', '#5a8fa8', '#3a9d6e'],
    tooltip: {
      trigger: 'axis',
      formatter: params => {
        let html = `<div style="font-weight:600;margin-bottom:4px">${params[0].name}</div>`
        params.forEach(p => {
          html += `<div style="display:flex;align-items:center;gap:6px;font-size:12px">${p.marker}<span>${p.seriesName}</span><b style="margin-left:auto">${p.value}°C</b></div>`
        })
        return html
      }
    },
    legend: { data: ['最高温', '最低温', '体感温'], top: 0, textStyle: { fontSize: 12 } },
    grid: { left: 40, right: 20, top: 40, bottom: 30 },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { fontSize: 11 },
      axisLine: { lineStyle: { color: '#e4e7ed' } }
    },
    yAxis: {
      type: 'value',
      name: '°C',
      nameTextStyle: { fontSize: 11 },
      axisLabel: { fontSize: 11, formatter: '{value}°' },
      splitLine: { lineStyle: { type: 'dashed', color: '#ececec' } }
    },
    series: [
      {
        name: '最高温', type: 'line', data: maxTemps,
        smooth: true, symbol: 'circle', symbolSize: 7,
        lineStyle: { width: 2.5 },
        label: { show: true, position: 'top', fontSize: 11, formatter: '{c}°' },
        areaStyle: { opacity: 0.15 }
      },
      {
        name: '最低温', type: 'line', data: minTemps,
        smooth: true, symbol: 'circle', symbolSize: 7,
        lineStyle: { width: 2.5 },
        label: { show: true, position: 'bottom', fontSize: 11, formatter: '{c}°' }
      },
      {
        name: '体感温', type: 'line', data: feelsLike,
        smooth: true, symbol: 'diamond', symbolSize: 6,
        lineStyle: { width: 2, type: 'dashed' }
      }
    ]
  })
}

async function load() {
  try {
    const r = await weatherApi.getForecast(props.city, 7)
    forecast.value = r.data
    selected.value = 0
    await nextTick()
    renderTrendChart()
  } catch {}
}

function handleResize() { trendChart?.resize() }

watch(() => props.city, load)
onMounted(() => {
  load()
  window.addEventListener('resize', handleResize)
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  trendChart = null
})
</script>
