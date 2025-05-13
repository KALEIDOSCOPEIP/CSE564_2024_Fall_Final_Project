<template>
    <h2 style="margin-top: -12rem; margin-bottom: 6rem; text-align: center; color: azure;">Parallel Coordinate Plot of City Main Attributes</h2>
    <div style="text-align: center; width: 100%; z-index: 1; margin-top: -5rem; margin-bottom: 5rem;">
        <table style="text-align: center; width: 100%; margin-left: 12rem;">
            <tr style="text-align: center; display: flex;">
                <!-- <td>
                    <div style="width: 4vw; text-align: center;">
                    <Multiselect
                        v-model="selectedPollutantPC"
                        :options="pollutantsPC"
                        :multiple="false"
                        :close-on-select="true"
                        placeholder="Select Pollutant"
                        class="select" />
                    </div>
                </td> -->
                
                <td style="text-align: center;">
                    <div style="width: 6vw; text-align: center;">
                    <Multiselect
                        v-model="startDate"
                        :options="year_months"
                        :multiple="false"
                        :close-on-select="true"
                        placeholder="Select Start Date"
                        class="select" />
                    </div>
                </td>
                
                <td style="text-align: center;">
                    <div style="width: 6vw; text-align: center;">
                    <Multiselect
                        v-model="endDate"
                        :options="year_months"
                        :multiple="false"
                        :close-on-select="true"
                        placeholder="Select End Date"
                        class="select" />
                    </div>
                </td>
            </tr>
        </table>
    </div>
    <div class="pc-overall-container">
        <svg
            ref="svgRef"
            :viewBox="`0 0 ${svgwidth} ${svgheight}`"
            preserveAspectRatio="xMinYMin meet"
            class="w-full h-full"
            style="margin-top:-8rem;"
            >
        </svg> 
    </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'
import Multiselect from 'vue-multiselect'

const props = defineProps({
  pollutant: String,
  startDate: String,
  endDate: String,
})

const svgRef = ref(null)
const svgwidth = 1000
const svgheight = 500
const margin = { top: 50, right: 30, bottom: 10, left: 10 }

const barRef = ref(null)
const barChartXStart = svgwidth - 300

let dimensions = ['AQI', 'CO', 'NO2', 'SO2', 'PM10', 'PM2.5', 'population', 'gdp', 'is_coastal', 'climate_code']
let y = {} // 每个维度一个 y 轴比例尺
let x = null


const pollutantsPC = ['AQI', 'PM2.5', 'PM10', 'SO2', 'NO2', 'O3', 'CO']
const years = ['2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']
const months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
const year_months = []
for (const year of years) {
    for (const month of months) {
        year_months.push(`${year}-${month}`)
    }
}
// const cityPC = ref([])
// const fetchCities = async () => {
//     const res = await fetch('http://localhost:5000/api/cities')
//     cityPC.value = await res.json()
// }
// const selectedCityPC = ref('Beijing')
const selectedPollutantPC = ref('AQI')
const startDate = ref('2014-05')
const endDate = ref('2023-05')


async function draw() {
//   const fetch_startDate = startDate.value.replace('-', '')
//   const fetch_endDate = endDate.value.replace('-', '')

  const res = await fetch(`http://localhost:5000/api/parallel-data?type=${selectedPollutantPC.value}&start=${startDate.value}&end=${endDate.value}`)
  const data = await res.json()

  const svg = d3.select(svgRef.value)
  svg.selectAll("*").remove()

  x = d3.scalePoint()
    .range([margin.left, svgwidth - margin.right])
    .padding(1)
    .domain(dimensions)

//   for (const dim of dimensions) {
//     y[dim] = d3.scaleLinear()
//       .domain(d3.extent(data, d => +d[dim]))
//       .range([svgheight - margin.bottom, margin.top])
//   }

  for (const dim of dimensions) {
    if (dim === 'is_coastal') {
        y[dim] = d3.scalePoint()
        .domain(['No', 'Yes'])
        .range([svgheight - margin.bottom, margin.top])
    } else if (dim === 'climate_code') {
        const labels = {
        0: 'Subtropical Monsoon',
        1: 'Temperate Monsoon',
        2: 'Temperate Continental',
        3: 'Plateau Mountain',
        4: 'tropical Monsoon',
        }
        y[dim] = d3.scalePoint()
        .domain(Object.values(labels))
        .range([svgheight - margin.bottom, margin.top])
    } else {
        y[dim] = d3.scaleLinear()
        .domain(d3.extent(data, d => +d[dim]))
        .range([svgheight - margin.bottom, margin.top])
    }
  }

//   function path(d) {
//     return d3.line()(dimensions.map(p => [x(p), y[p](d[p])]))
//   }

  function path(d) {
  return d3.line()(dimensions.map(p => {
    if (p === 'is_coastal') return [x(p), y[p](d[p] === 1 ? 'Yes' : 'No')]
    if (p === 'climate_code') {
      const climateMap = {
        0: 'Subtropical Monsoon',
        1: 'Temperate Monsoon',
        2: 'Temperate Continental',
        3: 'Plateau Mountain',
        4: 'tropical Monsoon',
      }
      return [x(p), y[p](climateMap[d[p]])]
    }
    return [x(p), y[p](d[p])]
  }))
}

//   // 背景线
//   svg.append("g")
//     .attr("fill", "none")
//     .attr("stroke", "#ccc")
//     .attr("stroke-width", 1)
//     .selectAll("path")
//     .data(data)
//     .join("path")
//     .attr("d", path)

  // 背景线（淡灰）
    svg.append("g")
    .attr("fill", "none")
    .attr("stroke", "#888")
    .attr("stroke-opacity", 1)
    .attr("stroke-width", 1)
    .selectAll("path")
    .data(data)
    .join("path")
    .attr("d", path)

  // 前景线
//   svg.append("g")
//     .attr("fill", "none")
//     .attr("stroke", "#0077cc")
//     .attr("stroke-width", 1.5)
//     .attr("stroke-opacity", 0.6)
//     .selectAll("path")
//     .data(data)
//     .join("path")
//     .attr("d", path)
//     .append("title")
//     .text(d => d.province)

  svg.append("g")
  .attr("fill", "none")
  .attr("stroke", "#00baff")
  .attr("stroke-opacity", 0.15)
  .attr("stroke-width", 8)
  .attr("stroke-linecap", "round")
  .attr("stroke-linejoin", "round")
  .attr("stroke-dasharray", "5,5")
  .attr("stroke-linejoin", "round")
  .selectAll("path")
  .data(data)
  .join("path")
  .attr("d", path)
  .on("mouseover", function (event, d) {
    d3.select(this).attr("stroke", "#ffcc00").attr("stroke-width", 12).attr("stroke-opacity", 0.8)
  })
  .on("mouseout", function (event, d) {
    d3.select(this).attr("stroke", "#00baff").attr("stroke-width", 8).attr("stroke-opacity", 0.15)
  })
  .append("title")
  .text(d => d.province)

  // 坐标轴
//   svg.selectAll("g.axis")
//     .data(dimensions)
//     .join("g")
//     .attr("class", "axis")
//     .attr("transform", d => `translate(${x(d)},0)`)
//     .each(function (d) {
//       d3.select(this).call(d3.axisLeft(y[d]))
//     })
//     .append("text")
//     .attr("y", margin.top - 10)
//     .attr("text-anchor", "middle")
//     .attr("font-size", "12px")
//     .attr("fill", "#fff")
//     .text(d => {
//       switch (d) {
//         case 'value': return '污染值'
//         case 'population': return '人口'
//         case 'gdp': return 'GDP'
//         case 'is_coastal': return '沿海'
//         case 'climate_code': return '气候类型'
//         default: return d
//       }
//     })

  svg.selectAll("g.axis")
  .data(dimensions)
  .join("g")
  .attr("class", "axis")
  .attr("transform", d => `translate(${x(d)},0)`)
  .each(function (d) {
    d3.select(this).call(d3.axisLeft(y[d]).ticks(6))
    .selectAll("text")
    .attr("font-size", "1.5em")
  })
  .append("text")
  .attr("y", margin.top - 20)
  .attr("text-anchor", "middle")
  .attr("fill", "#ffffff")
  .attr("font-size", "1.5em")
  .text(d => {
    switch (d) {
      case 'value': return 'Pollution'
      case 'population': return 'Population'
      case 'gdp': return 'GDP'
      case 'is_coastal': return 'Coastal'
      case 'climate_code': return 'Climate'
      default: return d
    }
  })








    // 柱状图逻辑
  const barSvg = d3.select(barRef.value)
  barSvg.selectAll("*").remove()

  // 取污染值前五的省份
const topData = [...data]
  .sort((a, b) => b.value - a.value)

// y 轴为省份名，x 轴为污染值
const barY = d3.scaleBand()
  .domain(topData.map(d => d.province))
  .range([margin.top, svgheight - margin.bottom])
  .padding(0.1)

const barX = d3.scaleLinear()
  .domain([0, d3.max(topData, d => d.value)])
  .range([0, 100])  // 控制柱子长度

// 绘制柱子
barSvg.append("g")
  .selectAll("rect")
  .data(topData)
  .join("rect")
  .attr("x", 20)
  .attr("y", d => barY(d.province))
  .attr("width", d => barX(d.value))
  .attr("height", barY.bandwidth())
  .attr("fill", "#00baff")

// 绘制标签（省份名）
barSvg.append("g")
  .selectAll("text")
  .data(topData)
  .join("text")
  .attr("x", 20)
  .attr("y", d => barY(d.province) + barY.bandwidth() / 2 + 4)
  .text(d => d.province)
  .attr("fill", "#fff")
  .attr("font-size", "12px")
}
// onMounted(draw)

onMounted(() => {
//   fetchCities()
  draw()
})

// watch(() => [props.pollutant, props.startDate, props.endDate], draw)
// watch(
//   () => selectedCityPC.value,
//   () => {
//     draw()
//   }, { deep: true }
// )

watch(
  () => selectedPollutantPC.value,
  () => {
    draw()
  }, { deep: true }
)

watch(
  () => startDate.value,
  () => {
    draw()
  }, { deep: true }
)

watch(
  () => endDate.value,
  () => {
    draw()
  }, { deep: true }
)
</script>


<style scoped>
.pc-overall-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 35vh;
}

.bar-container {
  width: 40%;
  height: 100%;
  background-color: rgba(47, 47, 47, 0);
  padding: 2rem;
  border-radius: 15px;
  overflow-y: auto;
}

.PC-container {
  width: 100%;
  height: 100%;
  background-color: rgba(47, 47, 47, 0);
  /* padding: 2rem; */
  border-radius: 15px;
  margin-top: -15rem;
}
</style>