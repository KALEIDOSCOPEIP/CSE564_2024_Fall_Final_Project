<template>
  <div class="bubble-chart-container">
    <h2 class="text-xl font-bold mb-4 text-white"
    style="text-align: center; margin-top: -4rem; color: azure;">
    Bubble Chart of Pollution Interrelation & Provincial Statistics</h2>

    <!-- 四个下拉菜单并排一行 -->
<!-- <div class="flex flex-wrap gap-4 mb-6 w-full">
  <div class="bubble-selectors-parent">
    <label class="text-white">X轴：</label>
    <div class="bubble-selectors">
      <Multiselect v-model="xField" :options="numericOptions" />
    </div>
  </div>
  <div class="bubble-selectors-parent">
    <label class="text-white whitespace-nowrap">Y轴：</label>
    <div class="bubble-selectors">
      <Multiselect v-model="yField" :options="numericOptions" />
    </div>
  </div>
  <div class="bubble-selectors-parent">
    <label class="text-white whitespace-nowrap">大小：</label>
    <div class="bubble-selectors">
      <Multiselect v-model="sizeField" :options="numericOptions" />
    </div>
  </div>
  <div class="bubble-selectors-parent">
    <label class="text-white whitespace-nowrap">颜色：</label>
    <div class="bubble-selectors">
      <Multiselect v-model="colorField" :options="categoricalOptions" />
    </div>
  </div>
</div> -->

    <div class="selectors-div" style="text-align: center; margin-top: -1rem;">
        <table class="selectors-table" style="text-align: center;">
            <tr>
                <td style="width: 25vw; align-items: center;">
                    <label class="text-white">X axis:</label>
                    <div class="bubble-selectors">
                        <Multiselect v-model="xField" :options="numericOptions" />
                    </div>
                </td>
                <td style="width: 25%; align-items: center;">
                    <label class="text-white">Y axis:</label>
                    <div class="bubble-selectors">
                        <Multiselect v-model="yField" :options="numericOptions" />
                    </div>
                </td>
                <td style="width: 25%; align-items: center;">
                    <label class="text-white">Bubble size:</label>
                    <div class="bubble-selectors">
                        <Multiselect v-model="sizeField" :options="numericOptions" />
                    </div>
                </td>
                <td style="width: 25%; align-items: center;">
                    <label class="text-white">Bubble color:</label>
                    <div class="bubble-selectors">
                        <Multiselect v-model="colorField" :options="categoricalOptions" />
                    </div>
                </td>
            </tr>
        </table>
    </div>

    <!-- 时间滑块 -->
    <div class="flex items-center mb-4" style="width: 100%; text-align: center;">
      <label class="text-white mr-4">Date: {{ currentYear }}</label>
      <input 
      type="range" 
      :min="0" 
      :max="yearList.length - 1" 
      v-model="currentYearIndex" 
      class="w-full" 
      style="width: 80%;"
      @mousedown="onSliderInteraction" @touchstart="onSliderInteraction"/>
      <!-- <span class="text-white ml-4">{{ currentYear }}</span> -->
        <button @click="toggleAutoPlay" class="ml-4 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded">
        {{ isPlaying ? '⏸' : '▶' }}
        </button>
    </div>

    <!-- 气泡图 -->
     <div class="relative w-full h-full" style="text-align: center;">
        <svg 
        ref="svgRef" 
        :width="svgWidth"
        :height="svgHeight"
        preserveAspectRatio="xMinYMin meet"
        class="w-full h-full"
        ></svg>
    </div>
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

const svgWidth = 750
const svgHeight = 400



const isPlaying = ref(false)
let timer = null

function toggleAutoPlay() {
  if (isPlaying.value) {
    stopAutoPlay()
  } else {
    isPlaying.value = true
    timer = setInterval(() => {
      currentYearIndex.value = (currentYearIndex.value + 1) % yearList.value.length
    }, 1000)
  }
}

function stopAutoPlay() {
  isPlaying.value = false
  if (timer) clearInterval(timer)
  timer = null
}

function onSliderInteraction() {
  stopAutoPlay()
}


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

  // 轴动画更新
  g.select(".x-axis").remove()
  g.select(".y-axis").remove()

  g.append("g")
    .attr("class", "x-axis")
    .attr("transform", `translate(0, ${height})`)
    .transition().duration(500)
    .call(d3.axisBottom(xScale))

  g.append("g")
    .attr("class", "y-axis")
    .transition().duration(500)
    .call(d3.axisLeft(yScale))
  
//   let xAxis = g.select(".x-axis")
//   if (xAxis.empty()) {
//     xAxis = g.append("g")
//       .attr("class", "x-axis")
//       .attr("transform", `translate(0, ${height})`)
//   }
//   xAxis.transition().duration(500).call(d3.axisBottom(xScale))

//   let yAxis = g.select(".y-axis")
//   if (yAxis.empty()) {
//     yAxis = g.append("g")
//       .attr("class", "y-axis")
//   }
//   yAxis.transition().duration(500).call(d3.axisLeft(yScale))

//   // 圆形气泡更新动画
//   const circles = g.selectAll("circle").data(data, d => d.province)

//   circles
//     .join(
//       enter => enter.append("circle")
//         .attr("cx", d => xScale(+d[xField.value]))
//         .attr("cy", d => yScale(+d[yField.value]))
//         .attr("r", 0)
//         .attr("fill", d => colorScale(d[colorField.value]))
//         .attr("opacity", 0.75)
//         .attr("stroke", "white")
//         .call(enter => enter.transition().duration(500).attr("r", d => sizeScale(+d[sizeField.value])))
//         .append("title")
//         .text(d => `${d.province}\n${xField.value}: ${d[xField.value]}\n${yField.value}: ${d[yField.value]}`),

//       update => update
//         .transition().duration(500)
//         .attr("cx", d => xScale(+d[xField.value]))
//         .attr("cy", d => yScale(+d[yField.value]))
//         .attr("r", d => sizeScale(+d[sizeField.value]))
//         .attr("fill", d => colorScale(d[colorField.value])),

//       exit => exit.transition().duration(300).attr("r", 0).remove()
//     )

//   g.select(".year-label").remove()
//   g.append("text")
//     .attr("class", "year-label")
//     .attr("x", width / 2)
//     .attr("y", -5)
//     .attr("text-anchor", "middle")
//     .attr("fill", "white")
//     .text(`时间: ${year}`)

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
//   g.append("text")
//     .attr("x", width / 2)
//     .attr("y", -5)
//     .attr("text-anchor", "middle")
//     .attr("fill", "white")
//     .text(`${year}`)
  
  // 添加图例
//   const legendData = Array.from(new Set(data.map(d => d[colorField.value])))

//   const legend = g.append("g")
//     .attr("transform", `translate(${width - 150}, ${height - legendData.length * 20 - 10})`)

//   legend.append("rect")
//     .attr("width", 140)
//     .attr("height", legendData.length * 20 + 10)
//     .attr("fill", "#000")
//     .attr("opacity", 0.5)
//     .attr("rx", 5)
//     .attr("radius", 100)

//   legend.selectAll("legend-dots")
//     .data(legendData)
//     .join("circle")
//     .attr("cx", 20)
//     .attr("cy", (d, i) => 15 + i * 20)
//     .attr("r", 6)
//     .style("fill", d => colorScale(d))

//   legend.selectAll("legend-labels")
//     .data(legendData)
//     .join("text")
//     .attr("x", 35)
//     .attr("y", (d, i) => 18 + i * 20)
//     .text(d => d)
//     .attr("fill", "white")
//     .style("font-size", "12px")
  
  // legend 数据与文字宽度预估
const legendData = Array.from(new Set(data.map(d => d[colorField.value])))
const maxLabelLength = d3.max(legendData, d => d.length)
const charWidth = 7 // 每个字符大约 7px 宽
const legendWidth = 30 + maxLabelLength * charWidth // 30: 圆点+间距+padding

const legendHeight = legendData.length * 20 + 10

const legend = g.append("g")
  .attr("transform", `translate(${width - legendWidth - 10}, ${height - legendHeight - 10})`)

// legend.append("rect")
//   .attr("width", legendWidth)
//   .attr("height", legendHeight)
//   .attr("fill", "#000")
//   .attr("opacity", 0.5)
//   .attr("rx", 5)

legend.selectAll("legend-dots")
  .data(legendData)
  .join("circle")
  .attr("cx", 10)
  .attr("cy", (d, i) => 10 + i * 20)
  .attr("r", 6)
  .style("fill", d => colorScale(d))

legend.selectAll("legend-labels")
  .data(legendData)
  .join("text")
  .attr("x", 22)
  .attr("y", (d, i) => 14 + i * 20)
  .text(d => d)
  .attr("fill", "white")
  .style("font-size", "12px")
}

onMounted(fetchData)
watch([xField, yField, sizeField, colorField, currentYearIndex], drawChart)
</script>

<style scoped>
.bubble-chart-container {
  padding: 1rem;
  max-width: 100%;
  height: 80%;
  display: flex;
  flex-direction: column;
  margin-top: -10rem;
  margin-left: -10rem;;
}

::v-deep .multiselect {
  width: 100% !important;
  min-width: 0 !important;
  max-width: 100% !important;
  box-sizing: border-box;
}

.bubble-selectors-parent {
  display: flex;
  flex-direction: row;
  align-items: center;
}
</style>
