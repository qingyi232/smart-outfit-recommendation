<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
      <h2 style="font-size:20px;font-weight:700;color:var(--text-primary)">天气数据监控</h2>
      <el-select v-model="filterCity" clearable placeholder="全部城市" style="width:140px" @change="load">
        <el-option v-for="c in cities" :key="c" :label="c" :value="c" />
      </el-select>
    </div>

    <el-card shadow="never" style="border-radius:var(--radius-md)">
      <el-table :data="list" v-loading="loading" stripe size="small">
        <el-table-column prop="city" label="城市" width="80" />
        <el-table-column prop="date" label="日期" width="110" />
        <el-table-column prop="weather_text" label="天气" width="70" />
        <el-table-column prop="temperature" label="温度℃" width="75" />
        <el-table-column prop="feels_like" label="体感℃" width="75" />
        <el-table-column label="温度范围" width="100"><template #default="{row}">{{ row.temp_min }}° ~ {{ row.temp_max }}°</template></el-table-column>
        <el-table-column prop="humidity" label="湿度%" width="70" />
        <el-table-column prop="wind_speed" label="风速" width="70" />
        <el-table-column prop="wind_direction" label="风向" width="70" />
        <el-table-column prop="precipitation" label="降水mm" width="80" />
        <el-table-column prop="aqi" label="AQI" width="55" />
        <el-table-column prop="aqi_level" label="空气质量" width="85">
          <template #default="{row}">
            <el-tag :type="row.aqi<=50?'success':row.aqi<=100?'':'warning'" size="small">{{ row.aqi_level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="uv_index" label="UV" width="50" />
        <el-table-column prop="sunrise" label="日出" width="60" />
        <el-table-column prop="sunset" label="日落" width="60" />
      </el-table>
      <div style="text-align:right;margin-top:16px">
        <el-pagination background layout="total, prev, pager, next" :total="total" :page-size="10" v-model:current-page="page" @current-change="load" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminApi, weatherApi } from '../../api'

const list = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const filterCity = ref('')
const cities = ref([])

async function load() {
  loading.value = true
  try {
    const r = await adminApi.getWeatherRecords({ page: page.value, per_page: 10, city: filterCity.value || undefined })
    list.value = r.data.items
    total.value = r.data.total
  } catch {} finally { loading.value = false }
}

onMounted(async () => {
  try { const r = await weatherApi.getCities(); cities.value = r.data } catch {}
  load()
})
</script>
