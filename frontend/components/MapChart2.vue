<template>
  <div class="map-container">
    <!-- 控制面板：年份、月份、污染物类型 -->
    <div class="controls">
      <!-- 年份单选 -->
      <label>Year:</n      <select v-model="selectedYear" @change="onFilterChange">
        <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}</option>
      </select>

      <!-- 月份多选（带全选） -->
      <label>Month:</n      <vue-multiselect
        v-model="selectedMonths"
        :options="monthOptions"
        :multiple="true"
        :close-on-select="false"
        placeholder="Choose month(s)"
        label="label"
        track-by="value"
      >
        <template #header>
          <button class="select-all" @click.prevent="toggleSelectAll">
            {{ allSelected ? 'Deselect All' : 'Select All' }}
          </button>
        </template>
      </vue-multiselect>

      <!-- 污染物类型单选 -->
      <label>污染物：</n      <select v-model="selectedPollutant" @change="onFilterChange">
        <option v-for="p in pollutantOptions" :key="p" :value="p">{{ p }}</option>
      </select>
    </div>

    <!-- ECharts 容器 -->
    <div ref="chartRef" class="chart"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import 'echarts/map/js/china'
import axios from 'axios'
import Multiselect from 'vue-multiselect'

export default {
  name: 'MapChart',
  components: { VueMultiselect: Multiselect },
  setup() {
    const chartRef = ref(null)
    let chart = null

    const yearOptions = ref([])
    const monthOptions = ref([
      { value: 1, label: '1月' },
      { value: 2, label: '2月' },
      { value: 3, label: '3月' },
      { value: 4, label: '4月' },
      { value: 5, label: '5月' },
      { value: 6, label: '6月' },
      { value: 7, label: '7月' },
      { value: 8, label: '8月' },
      { value: 9, label: '9月' },
      { value: 10, label: '10月' },
      { value: 11, label: '11月' },
      { value: 12, label: '12月' }
    ])
    const pollutantOptions = ref([])

    const selectedYear = ref(null)
    const selectedMonths = ref([])
    const selectedPollutant = ref(null)

    const allSelected = computed(() => selectedMonths.value.length === monthOptions.value.length)

    // 切换全选/取消全选
    function toggleSelectAll() {
      if (allSelected.value) {
        selectedMonths.value = []
      } else {
        selectedMonths.value = monthOptions.value.slice()
      }
      onFilterChange()
    }

    // 当筛选条件变化时，重新加载地图数据
    async function onFilterChange() {
      if (!selectedYear.value || selectedMonths.value.length === 0 || !selectedPollutant.value) return

      // 构造年-月列表，如202001, 202002
      const months = selectedMonths.value.map(m => selectedYear.value * 100 + m.value)
      const params = new URLSearchParams()
      params.append('type', selectedPollutant.value)
      months.forEach(m => params.append('months', m))

      const { data } = await axios.get('/api/province_pollutant_by_months', { params })

      chart.setOption({
        series: [{
          data: data.map(item => ({ name: item.province, value: item.avg_value }))
        }]
      })
    }

    // 初始化：获取年份、污染物选项，并绘制空地图
    onMounted(async () => {
      chart = echarts.init(chartRef.value)
      chart.setOption({
        title: { text: '', subtext: '' },
        tooltip: { trigger: 'item' },
        visualMap: { min: 0, max: 100, left: 'right', top: 'center', text: ['高','低'] },
        series: [{
          name: '污染物平均值',
          type: 'map',
          map: 'china',
          roam: true,
          data: []
        }]
      })

      // 获取可选年份
      const { data: dates } = await axios.get('/api/available_dates')
      const years = Array.from(new Set(dates.map(d => Math.floor(d / 100))))
      yearOptions.value = years.sort((a, b) => a - b)
      selectedYear.value = yearOptions.value[0]

      // 获取污染物类型
      const { data: types } = await axios.get('/api/pollutants')
      pollutantOptions.value = types
      selectedPollutant.value = types[0]

      // 默认全选月份
      selectedMonths.value = monthOptions.value.slice()

      // 首次渲染
      onFilterChange()
    })

    return {
      chartRef,
      yearOptions,
      monthOptions,
      pollutantOptions,
      selectedYear,
      selectedMonths,
      selectedPollutant,
      allSelected,
      toggleSelectAll,
      onFilterChange
    }
  }
}
</script>

<style scoped>
.map-container {
  position: relative;
}
.controls {
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.8);
  padding: 5px 10px;
  border-radius: 4px;
}
.chart {
  width: 100%;
  height: 100%;
}
.select-all {
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 2px 5px;
  font-size: 12px;
}
</style>
