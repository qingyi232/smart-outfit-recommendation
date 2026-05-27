<template>
  <div class="page-container">
    <!-- 天气概览 -->
    <div class="weather-hero" v-if="weather">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;position:relative;z-index:1">
        <div>
          <div style="font-size:14px;opacity:0.85;margin-bottom:4px">{{ weather.city }} · {{ weather.date }}</div>
          <div class="temp-display">{{ weather.temperature }}°</div>
          <div class="weather-info">
            {{ weather.weather_text }} | 体感 {{ weather.feels_like }}° | 湿度 {{ weather.humidity }}% | 风速 {{ weather.wind_speed }}km/h
          </div>
          <div class="weather-info" style="margin-top:4px">
            AQI {{ weather.aqi }} {{ weather.aqi_level }} | UV {{ weather.uv_index }}
          </div>
        </div>
        <div style="text-align:right" v-if="comfort">
          <div style="font-size:14px;opacity:0.85">舒适度指数</div>
          <div style="font-size:36px;font-weight:200">{{ comfort.thi }}</div>
          <div style="font-size:13px;opacity:0.9">{{ comfort.description }}</div>
        </div>
      </div>
    </div>
    <div v-else style="text-align:center;padding:40px"><el-skeleton :rows="3" animated /></div>

    <!-- 场景选择 -->
    <div style="margin-top:28px">
      <h3 style="font-size:17px;font-weight:600;margin-bottom:16px;color:var(--text-primary)">选择出行场景</h3>
      <div class="scene-grid">
        <div v-for="s in sceneOptions" :key="s.name" class="scene-item" :class="{ active: scene === s.name }" @click="changeScene(s.name)">
          <div class="scene-icon"><el-icon :size="28" :color="scene === s.name ? 'var(--primary)' : 'var(--text-secondary)'"><component :is="s.icon" /></el-icon></div>
          <div class="scene-name">{{ s.name }}</div>
        </div>
      </div>
    </div>

    <!-- AI 推荐模式选择 -->
    <div style="margin-top:28px">
      <h3 style="font-size:17px;font-weight:600;margin-bottom:12px;color:var(--text-primary)">AI 推荐模式</h3>
      <div style="display:flex;gap:10px">
        <div v-for="m in modelOptions" :key="m.key"
          class="model-card" :class="{ active: modelType === m.key }"
          @click="changeModel(m.key)">
          <div class="model-icon">{{ m.icon }}</div>
          <div class="model-name">{{ m.label }}</div>
          <div class="model-desc">{{ m.desc }}</div>
        </div>
      </div>
    </div>

    <!-- 今日推荐 -->
    <div style="margin-top:32px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
        <h3 style="font-size:17px;font-weight:600;color:var(--text-primary)">今日穿搭推荐</h3>
        <el-button type="primary" plain size="small" :loading="recLoading" @click="refreshRec">
          <el-icon><Refresh /></el-icon>换一套
        </el-button>
      </div>

      <div v-if="recLoading" style="text-align:center;padding:40px"><el-skeleton :rows="4" animated /></div>
      <div v-else-if="recommendation">
        <!-- 建议文字 -->
        <el-alert :title="recommendation.advice_text" type="success" show-icon :closable="false" style="margin-bottom:20px;border-radius:var(--radius-md)" />

        <!-- 评分 -->
        <el-row :gutter="16" style="margin-bottom:20px">
          <el-col :span="12">
            <div class="stat-card">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <div><div class="stat-value">{{ recommendation.comfort_score }}</div><div class="stat-label">舒适度评分</div></div>
                <el-icon :size="32" color="var(--primary-light)" style="opacity:0.7"><Odometer /></el-icon>
              </div>
              <div class="score-bar" style="margin-top:12px"><div class="score-fill green" :style="{width: recommendation.comfort_score+'%'}"></div></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="stat-card">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <div><div class="stat-value">{{ recommendation.match_score }}</div><div class="stat-label">搭配评分</div></div>
                <el-icon :size="32" color="var(--secondary)" style="opacity:0.7"><TrophyBase /></el-icon>
              </div>
              <div class="score-bar" style="margin-top:12px"><div class="score-fill blue" :style="{width: recommendation.match_score+'%'}"></div></div>
            </div>
          </el-col>
        </el-row>

        <!-- 推荐服装 -->
        <el-row :gutter="16">
          <el-col :xs="12" :sm="8" :md="6" v-for="(item, key) in outfitItems" :key="key">
            <div class="outfit-card" v-if="item">
              <img :src="item.image_url" :alt="item.name" class="outfit-img" loading="lazy" @error="e => e.target.src='https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=400'" />
              <div class="outfit-info">
                <div class="outfit-name">{{ item.name }}</div>
                <div>
                  <span class="outfit-tag">{{ slotLabel(key) }}</span>
                  <span class="outfit-tag accent" v-if="item.category_name">{{ item.category_name }}</span>
                </div>
                <div style="font-size:12px;color:var(--text-light);margin-top:6px">{{ item.description }}</div>
              </div>
            </div>
          </el-col>
        </el-row>

        <!-- 反馈 -->
        <div style="margin-top:24px;text-align:center">
          <span style="font-size:14px;color:var(--text-secondary);margin-right:12px">这套搭配如何？</span>
          <el-rate v-model="feedbackRating" :colors="['var(--accent-light)','var(--accent)','var(--primary)']" @change="submitFeedback" />
        </div>
      </div>
      <el-empty v-else description="暂无推荐数据" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { weatherApi, recommendApi } from '../../api'
import { useUserStore } from '../../stores'
import { ElMessage } from 'element-plus'
import { OfficeBuilding, Basketball, Lollipop, GobletSquareFull, Location, House, Briefcase, Refresh, Odometer, TrophyBase } from '@element-plus/icons-vue'

const props = defineProps({ city: { type: String, default: '北京' } })
const store = useUserStore()

const weather = ref(null)
const comfort = ref(null)
const recommendation = ref(null)
const recLoading = ref(false)
const feedbackRating = ref(0)
const scene = ref('通勤')
const modelType = ref('standard')

const modelOptions = [
  { key: 'cool', label: '偏冷模式', icon: '❄️', desc: '清凉透气' },
  { key: 'standard', label: '标准模式', icon: '⚖️', desc: '均衡推荐' },
  { key: 'warm', label: '偏暖模式', icon: '🔥', desc: '保暖舒适' },
]

const sceneOptions = [
  { name: '通勤', icon: OfficeBuilding },
  { name: '运动', icon: Basketball },
  { name: '约会', icon: Lollipop },
  { name: '聚会', icon: GobletSquareFull },
  { name: '旅行', icon: Location },
  { name: '居家', icon: House },
  { name: '商务', icon: Briefcase },
]

const SLOT_LABELS = { top: '上衣', bottom: '下装', outer: '外套', shoes: '鞋子', accessory: '配饰' }
function slotLabel(k) { return SLOT_LABELS[k] || k }

const outfitItems = computed(() => {
  if (!recommendation.value?.outfit) return {}
  const o = recommendation.value.outfit
  const result = {}
  for (const k of ['top','bottom','outer','shoes','accessory']) {
    if (o[k]) result[k] = o[k]
  }
  return result
})

async function loadWeather() {
  try {
    const r = await weatherApi.getCurrent(props.city)
    weather.value = r.data
    comfort.value = r.data.comfort
  } catch {}
}

async function loadRecommendation() {
  recLoading.value = true
  feedbackRating.value = 0
  try {
    const r = await recommendApi.getToday(props.city, scene.value, modelType.value)
    recommendation.value = r.data
  } catch {} finally { recLoading.value = false }
}

async function refreshRec() {
  recLoading.value = true
  feedbackRating.value = 0
  try {
    const r = await recommendApi.generate({ city: props.city, scene: scene.value, model_type: modelType.value })
    recommendation.value = r.data
  } catch {} finally { recLoading.value = false }
}

function changeScene(s) {
  scene.value = s
  loadRecommendation()
}

function changeModel(m) {
  modelType.value = m
  refreshRec()
}

async function submitFeedback(val) {
  if (!recommendation.value) return
  try {
    await recommendApi.feedback({ recommendation_id: recommendation.value.id, rating: val })
    ElMessage.success('感谢您的反馈')
  } catch {}
}

watch(() => props.city, () => { loadWeather(); loadRecommendation() })
onMounted(() => { loadWeather(); loadRecommendation() })
</script>
