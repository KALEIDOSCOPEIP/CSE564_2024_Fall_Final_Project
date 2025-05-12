<template>
    <div style="position:relative;">
        <h2 style="text-align: center; margin-top: 1rem; color: azure;">Multi-city Pollutant Trend thr. Years</h2>
        <v-chart :option="mapOptions" autoresize class="map-chart" />
        <div v-if="isLoading" class="loading-overlay">
            <div class="spinner"></div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import { use } from 'echarts/core'
import VChart from 'vue-echarts'
import * as echarts from 'echarts'
import { CanvasRenderer } from 'echarts/renderers'
import { MapChart as EChartsMapChart } from 'echarts/charts'
import { TooltipComponent, VisualMapComponent } from 'echarts/components'
import chinaGeoJson from '../src/assets/china.json'

use([CanvasRenderer, EChartsMapChart, TooltipComponent, VisualMapComponent])
echarts.registerMap('china', chinaGeoJson)

const props = defineProps({
    pollutant: String,
    selectedDateInfo: Object,
})

const mapOptions = ref({})
const provinceDetails = ref({})

const chart = ref(null);
const isLoading = ref(false)

const updateMap = async (date, pollutant) => {
  if (!date || !pollutant) return;
  isLoading.value = true
  try {
    const res = await axios.get("http://localhost:5000/api/monthly_city_values", {
      params: { date, type: pollutant }
    });

    const newData = res.data;
    const seriesData = newData.map(d => {
              provinceDetails.value[d.province] = d
              return {
                  name: d.province,
                  value: d.gdp // 可替换为 d.population 显示人口
              }
          })
    const currentOptions = chart.value.getOption();

    chart.value.setOption({
      title: {
        text: `\n      Date: ${String(date).slice(0, 4)}-${String(date).slice(4, 6)}\n      \n      Pollutant: ${pollutant}\n      `,
        left: 'center',
        top: '10%',
        textStyle: {
          color: 'azure',
          fontSize: 18,
          fontWeight: 'bold'
        }
      },
      tooltip: {
        trigger: 'item',
        formatter: params => {
          const info = provinceDetails.value[params.name]
          if (!info) return `${params.name}`
          return `
            <strong>${params.name}</strong><br/>
            ${pollutant}: ${params.value} µg/m³
            Population: ${info.population.toLocaleString()} Mil.<br/>
            GDP: ${info.gdp} Tri. ￥
          `
        }
      },
      visualMap: {
        min: 0,
        max: Math.max(...res.data.map(d => d.value), 200),
        left: 'right',
        bottom: '45%',
        inRange: {
          color: ['#fff5eb', '#fcae91', '#fb6a4a', '#de2d26', '#a50f15']
        },
        text: ['High', 'Low'],
        textStyle: {
          color: '#fff',
          fontSize: 10,
        },
        calculable: false
      },
      series: [{
          name: 'Pollution',
          type: 'map',
          map: 'china',
          roam: true,
          zoom: 1.2,
          center: [104.114129, 30.550339],
          data: res.data,
          itemStyle: {
              borderColor: 'rgb(120, 120, 120)',
              borderWidth: 1,
          },
          emphasis: {
              itemStyle: {
                  areaColor: '#ffff00',
                  borderColor: '#fff',
                  borderWidth: 2,
              }
          }
      }]
    }, false);
  } finally {
    isLoading.value = false
  }
};

onMounted(async () => {
  chart.value = echarts.init(document.querySelector('.map-chart'));
  updateMap(202001, "AQI");
})

watch(() => props.selectedDateInfo, async (info) => {
  if (info?.date && info?.pollutant) {
    updateMap(info.date, info.pollutant);
  }
}, { deep: true });
</script>

<style scoped>
.map-chart {
    width: 100%;
    height: 100%;
    margin-top: -5rem;
}
.loading-overlay {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(30,30,30,0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
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
</style>