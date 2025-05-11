<template>
  <div class="container">
    <h1 class="title">Air Pollution Dashboard of Chinese Cities</h1>
    <table class="layout">
      <tr>
        <td>
            <LineChart 
                :pollutant="selectedPollutant"
                @date-selected="handleDataSelected"
                v-model:selectedType="selectedPollutant"
            />
        </td>
        <td rowspan="2">
            <div style="height: 100%;" ref="map-chart">
                <MapChart 
                    :pollutant="selectedPollutant"
                    :selectedDateInfo="selectedDateInfo"
                    :data="mapData" 
                />
            </div>
        </td> <!-- 地图占两行 -->
        <td>
            <SubburstChart />
        </td>
      </tr>
      <tr>
        <td><PlaceholderChart index="4" /></td>
        <td><PlaceholderChart index="5" /></td>
      </tr>
    </table>
  </div>
</template>

<script setup>
import LineChart from './components/LineChart.vue'
import MapChart from './components/MapChart.vue'
import SubburstChart from './components/SunburstChart.vue'
import { ref } from 'vue'

const PlaceholderChart = {
  props: ['index'],
  template: `<div class="placeholder">图表 {{ index }}</div>`
}

const selectedPollutant = ref('AQI') // 默认选择的污染物
const mapData = ref([
    { name: '北京', value: 100 },
    { name: '上海', value: 80 },
    { name: '广州', value: 60 },
    { name: '哈尔滨', value: 40 },
]) // 地图数据

const selectedDateInfo = ref(202001)
function handleDateSelected(info) {
    selectedDateInfo.value = info;
}
</script>

<style scoped>
.container {
  padding: 0.5rem;
  max-width: 4000px;
  margin: auto;
  height: 100vh;
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
  height: 30%;
}
td[rowspan="2"] {
  height: 100%;
  width: 40%; /* 地图那列可以稍微宽一些 */
}
td:not([rowspan]) {
  width: 30%;
}
.placeholder {
  background-color: #374151;
  border-radius: 8px;
  height: 100%;
  padding: 1rem;
  color: white;
}
</style>

<style>
/* 隐藏 vue-multiselect 的 aria-label 辅助提示 */
.multiselect__option [aria-label]::after,
.multiselect__option [aria-label]::before,
.multiselect__option [aria-label],
.multiselect__tag span[aria-label],
.multiselect__option span[aria-label] {
  display: none !important;
}
</style>
