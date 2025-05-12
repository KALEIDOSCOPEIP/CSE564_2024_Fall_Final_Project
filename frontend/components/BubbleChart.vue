<template>
  <div class="bubble-chart-wrapper p-4">
    <h2 class="text-xl font-bold mb-4 text-white">Bubble Chart</h2>

    <!-- 四个下拉菜单并排一行 -->
<div class="flex flex-wrap gap-4 mb-6 w-full">
  <div class="flex items-center space-x-2" style="flex: 1 1 23%; min-width: 180px;">
    <label class="text-white whitespace-nowrap">X轴：</label>
    <div style="flex: 1;">
      <Multiselect v-model="xField" :options="numericOptions" />
    </div>
  </div>
  <div class="flex items-center space-x-2" style="flex: 1 1 23%; min-width: 180px;">
    <label class="text-white whitespace-nowrap">Y轴：</label>
    <div style="flex: 1;">
      <Multiselect v-model="yField" :options="numericOptions" />
    </div>
  </div>
  <div class="flex items-center space-x-2" style="flex: 1 1 23%; min-width: 180px;">
    <label class="text-white whitespace-nowrap">大小：</label>
    <div style="flex: 1;">
      <Multiselect v-model="sizeField" :options="numericOptions" />
    </div>
  </div>
  <div class="flex items-center space-x-2" style="flex: 1 1 23%; min-width: 180px;">
    <label class="text-white whitespace-nowrap">颜色：</label>
    <div style="flex: 1;">
      <Multiselect v-model="colorField" :options="categoricalOptions" />
    </div>
  </div>
</div>

    <!-- 时间滑块 -->
    <div class="flex items-center mb-4">
      <label class="text-white mr-4">月份：</label>
      <input type="range" :min="0" :max="yearList.length - 1" v-model="currentYearIndex" class="w-full" />
      <span class="text-white ml-4">{{ currentYear }}</span>
    </div>

    <!-- 气泡图 -->
    <svg ref="svgRef" :width="svgWidth" :height="svgHeight"></svg>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import Multiselect from 'vue-multiselect'
import * as d3 from 'd3'

const xField = ref("PM2.5")
const yField = ref("PM10")
const sizeField = ref("population")
const colorField = ref("region")

const numericOptions = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3", "population", "gdp"]
const categoricalOptions = ["region", "climate_type", "is_coastal"]

const rawData = ref([])
const svgRef = ref(null)
const yearList = ref([])
const currentYearIndex = ref(0)
const currentYear = computed(() => yearList.value[currentYearIndex.value] || '')

const svgWidth = 700
const svgHeight = 450

async function fetchData() {
  const res = await fetch("http://localhost:5000/api/bubble_data")
  const data = await res.json()
  rawData.value = data
  yearList.value = [...new Set(data.map(d => d.year_month))].sort()
  drawChart()
}

function drawChart() {
  const svg = d3.select(svgRef.value)
  svg.selectAll("*").remove()

  const margin = { top: 20, right: 40, bottom: 40, left: 60 }
  const width = svgWidth - margin.left - margin.right
  const height = svgHeight - margin.top - margin.bottom

  const g = svg.append("g").attr("transform", `translate(${margin.left}, ${margin.top})`)

  const year = yearList.value[currentYearIndex.value]
  const data = rawData.value.filter(d => d.year_month === year)

  const xScale = d3.scaleLinear()
    .domain(d3.extent(data, d => +d[xField.value])).nice()
    .range([0, width])

  const yScale = d3.scaleLinear()
    .domain(d3.extent(data, d => +d[yField.value])).nice()
    .range([height, 0])

  const sizeScale = d3.scaleSqrt()
    .domain(d3.extent(data, d => +d[sizeField.value]))
    .range([5, 30])

  const colorScale = d3.scaleOrdinal(d3.schemeTableau10)

  // 坐标轴
  g.append("g").attr("transform", `translate(0, ${height})`).call(d3.axisBottom(xScale))
  g.append("g").call(d3.axisLeft(yScale))

  // 圆形气泡
  g.selectAll("circle")
    .data(data)
    .join("circle")
    .attr("cx", d => xScale(+d[xField.value]))
    .attr("cy", d => yScale(+d[yField.value]))
    .attr("r", d => sizeScale(+d[sizeField.value]))
    .attr("fill", d => colorScale(d[colorField.value]))
    .attr("opacity", 0.75)
    .attr("stroke", "white")
    .append("title")
    .text(d => `${d.province}\n${xField.value}: ${d[xField.value]}\n${yField.value}: ${d[yField.value]}`)

  // 年份标签
  g.append("text")
    .attr("x", width / 2)
    .attr("y", -5)
    .attr("text-anchor", "middle")
    .attr("fill", "white")
    .text(`时间: ${year}`)
}

onMounted(fetchData)
watch([xField, yField, sizeField, colorField, currentYearIndex], drawChart)
</script>

<style scoped>
.multiselect {
  background-color: white;
  color: black;
}
</style>
