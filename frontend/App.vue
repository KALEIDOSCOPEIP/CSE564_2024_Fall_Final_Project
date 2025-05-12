<template>
  <div class="container">
    <h1 class="title">Air Pollution Dashboard of Chinese Cities</h1>
    <div class="dashboard-grid">
      <div class="dashboard-card">
        <div class="dashboard-card-header">
          <span class="icon">📈</span> Multi-city Pollutant Trend
        </div>
        <LineChart 
          :pollutant="selectedPollutant"
          @date-selected="handleDateSelected"
          v-model:selectedType="selectedPollutant"
        />
      </div>
      <div class="dashboard-card map-card">
        <div class="dashboard-card-header">
          <span class="icon">🗺️</span> Map Overview
        </div>
        <MapChart 
          :pollutant="selectedPollutant"
          :selectedDateInfo="selectedDateInfo"
          :data="mapData" 
        />
      </div>
      <div class="dashboard-card">
        <div class="dashboard-card-header">
          <span class="icon">🌞</span> Top-5 Pollutant Sunburst
        </div>
        <SubburstChart />
      </div>
      <div class="dashboard-card">
        <div class="dashboard-card-header">
          <span class="icon">🔵</span> Bubble Chart
        </div>
        <BubbleChart />
      </div>
    </div>
    <!-- Loading spinner placeholder -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="spinner"></div>
    </div>
  </div>
</template>

<script setup>
import LineChart from './components/LineChart.vue'
import MapChart from './components/MapChart.vue'
import SubburstChart from './components/SunburstChart.vue'
import BubbleChart from './components/BubbleChart.vue'
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

const isLoading = ref(false) // For future loading spinner usage
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');

.container {
  padding: 0.5rem;
  max-width: 1600px;
  margin: auto;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: 'Inter', Arial, sans-serif;
  background: linear-gradient(135deg, #232526 0%, #414345 100%);
}
.title {
  text-align: center;
  font-size: 2.2rem;
  font-weight: bold;
  margin-bottom: 1.5rem;
  margin-top: 0.5rem;
  color: #fff;
  letter-spacing: 1px;
}
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 2rem;
  width: 100%;
  height: 100%;
}
.dashboard-card {
  background: rgba(40, 40, 50, 0.95);
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.15);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  min-height: 400px;
  transition: box-shadow 0.2s, transform 0.2s;
  position: relative;
}
.dashboard-card:hover {
  box-shadow: 0 8px 32px rgba(0,0,0,0.25);
  transform: translateY(-2px) scale(1.01);
}
.dashboard-card-header {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #e0e0e0;
}
.icon {
  font-size: 1.3rem;
}
.map-card {
  grid-row: 1 / span 2;
  min-height: 820px;
}
.loading-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(30,30,30,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.spinner {
  border: 6px solid #f3f3f3;
  border-top: 6px solid #3498db;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
@media (max-width: 1100px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(4, 1fr);
  }
  .map-card {
    grid-row: auto;
    min-height: 400px;
  }
}
</style>
