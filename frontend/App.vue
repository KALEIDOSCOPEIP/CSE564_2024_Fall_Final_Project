<template>
  <div class="container">
    <!-- <Background /> -->
    <h1 class="title">Air Pollution Dashboard of Chinese Cities</h1>
    <table class="layout">
      <tr>
        <td style="width: 30vw;">
            <LineChart 
                :pollutant="selectedPollutant"
                v-model:selectedCities="selectedCities"
                @update:selectedcities="handleCitiesChange"
            />
        </td>
        <td rowspan="2" style="width: 40vw;">
            <div style="height: 100%; margin-left: -15rem;" ref="map-chart">
                <MapChart 
                    :highlight-cities="selectedCities"
                    :city-colors="cityColors"
                    :pollutant="selectedPollutant"
                />
            </div>
        </td> <!-- 地图占两行 -->
        <td style="width: 30vw;">
            <div style="margin-left: -18rem; margin-top: -2rem; margin-bottom: -5rem; text-align: center;">
            <h2 style="text-align: center;">Top Polluted Provinces & City Pollution Comparison</h2>
            <table class="sunburst-radar-container">
                <tr>
                    <td style="width: 40%;">
                        <SubburstChart />
                    </td>
                    <td style="width: 40%;">
                        <RadarChart 
                        :cities="selectedCities"
                        :city-colors="cityColors"
                        />
                    </td>
                </tr>
            </table>
            </div>
        </td>
      </tr>
      <tr>
        <td style="width: 30vw;">
            <!-- <PlaceholderChart index="4" /> -->
            <ParallelPlot :pollutant="selectedType" :startDate="timeRangeStart" :endDate="timeRangeEnd" />
        </td>
        <td style="width: 30vw;">
            <div>
                <BubbleChart />
            </div>
        </td>
      </tr>
    </table>
  </div>
</template>

<script setup>
import LineChart from './components/LineChart.vue'
import MapChart from './components/MapChart.vue'
import SubburstChart from './components/SunburstChart.vue'
import BubbleChart from './components/BubbleChart.vue'
import ParallelPlot from './components/ParallelCordChart.vue'
// import Background from './components/Background.vue'
import RadarChart from './components/RadarChart.vue'
import { ref, computed } from 'vue'

const PlaceholderChart = {
  props: ['index'],
  template: `<div class="placeholder">Charts {{ index }}</div>`
}

const selectedPollutant = ref('AQI') // 默认选择的污染物
const mapData = ref([
    { name: 'Beijing', value: 100 },
    { name: 'Shanghai', value: 80 },
    { name: 'Guangzhou', value: 60 },
    { name: 'Harbin', value: 40 },
]) // 地图数据

const selectedDateInfo = ref(202001)
function handleDateSelected(info) {
    selectedDateInfo.value = info;
}

const selectedType = ref('PM2.5')
const timeRangeStart = ref(201405)
const timeRangeEnd = ref(202503)





// The following are interactive parts

const selectedCities = ref([
    'Beijing',
    'Shanghai',
    'Guangzhou',
    'Harbin'
])
// ② 给每个城市分配一种颜色（可自定义 Palette）
const palette = ['#5470C6','#91CC75','#FAC858','#EE6666','#73C0DE','#3BA272']
const cityColors = computed(() =>
  selectedCities.value.map((_, i) => palette[i % palette.length])
)
// 把选中城市传给折线图做双向绑定
function handleCitiesChange(cities) {
  selectedCities.value = cities
}
</script>

<style scoped>
.container {
  padding: 0.5rem;
  max-width: 4000px;
  margin: auto;
  height: 1000px;
  display: flex;
  flex-direction: column;
}
.title {
  text-align: center;
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0rem;
  margin-top: 0rem;
}
.layout {
  width: 100%;
  height: 100%;
  border-spacing: 1rem;
  table-layout: fixed;
}
td {
  vertical-align: top;
  height: 50%;
}
td[rowspan="2"] {
  height: 100%;
  /* width: 30vw; 地图那列可以稍微宽一些 */
}
td:not([rowspan]) {
  /* width: 25vw; */
  height: 50%;
}
.placeholder {
  background-color: #374151;
  border-radius: 8px;
  height: 100%;
  padding: 1rem;
  color: white;
}
.sunburst-radar-container {
  display: flex;
  justify-content: space-around;
  align-items: flex-start;
  gap: 24px;
}
</style>
