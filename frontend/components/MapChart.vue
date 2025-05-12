<template>
    <h2 style="text-align: center; margin-top: 1rem; color: azure;">Multi-city Pollutant Trend thr. Years</h2>
    <v-chart :option="mapOptions" autoresize class="map-chart" />
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
// const chartRef = ref(null);

const updateMap = async (date, pollutant) => {
  if (!date || !pollutant) return;

  const res = await axios.get("http://localhost:5000/api/monthly_city_values", {
    params: { date, type: pollutant }
  });

  const newData = res.data;
  console.log(newData);
//   const seriesData = newData.map(d => {
//             provinceDetails.value[d.province] = d
//             return {
//                 name: d.province,
//                 value: d.gdp // 可替换为 d.population 显示人口
//             }
//         })
  const currentOptions = chart.value.getOption();
//   chart.value.setOption({
//     series: [{
//         ...currentOptions.series[0],
//         data: newData.map(d => {
//             const province = provinceDetails.value[d.name]
//             return {
//                 name: d.name,
//                 value: d.value,
//                 population: province ? province.population : 0,
//                 gdp: province ? province.gdp : 0
//             }
//         })
//     }]
//   })

  chart.value.setOption({
    title: {
      text: `
      Date: ${String(date).slice(0, 4)}-${String(date).slice(4, 6)}

      Pollutant: ${pollutant}
      `,
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
};


// // ⏰ 页面初次加载时默认显示
// onMounted(() => {
//   chart.value = echarts.init(document.querySelector('.map-chart'));
//   updateMap(202001, "AQI"); // ✅ 设置一个合适的默认值（你可以换成最近的数据）
// });


onMounted(async () => {
  chart.value = echarts.init(document.querySelector('.map-chart'));
  updateMap(202001, "AQI"); // ✅ 设置一个合适的默认值（你可以换成最近的数据）
    // try {
    //     const res = await axios.get('http://localhost:5000/api/province_info')
    //     const list = res.data

    //     const seriesData = list.map(d => {
    //         provinceDetails.value[d.province] = d
    //         return {
    //             name: d.province,
    //             value: d.gdp // 可替换为 d.population 显示人口
    //         }
    //     })

    //     const vmax = Math.max(...seriesData.map(d => d.value), 100)

    //     mapOptions.value = {
    //         tooltip: {
    //             trigger: 'item',
    //             formatter: params => {
    //                 const info = provinceDetails.value[params.name]
    //                 if (!info) return `${params.name}`
    //                 return `
    //         <strong>${params.name}</strong><br/>
    //         Population: ${info.population.toLocaleString()} Mil.<br/>
    //         GDP: ${info.gdp} Tri. ￥
    //       `
    //             }
    //         },
    //         visualMap: {
    //             min: 0,
    //             max: vmax,
    //             left: 'right',
    //             bottom: '45%',
    //             inRange: {
    //               color: ['#fff5eb', '#fcae91', '#fb6a4a', '#de2d26', '#a50f15']
    //             },
    //             text: ['High', 'Low'],
    //             calculable: false
    //           },
    //         series: [{
    //             type: 'map',
    //             map: 'china',
    //             roam: false,
    //             zoom: 1.2,
    //             center: [104.114129, 30.550339],
    //             data: seriesData
    //         }]
    //     }
    // } catch (err) {
    //     console.error('加载省级信息失败：', err)
    // }
})



// 🔄 点击折线图后触发地图更新
watch(() => props.selectedDateInfo, async (info) => {
  if (info?.date && info?.pollutant) {
    updateMap(info.date, info.pollutant);
  }
}, { deep: true });

// watch(() => props.selectedDateInfo, async (info) => {
//     if (!info || !info.date || !info.pollutant) return;

//     const res = await axios.get("http://localhost:5000/api/monthly_city_values", {
//         params: {
//             date: info.date,
//             type: info.pollutant
//         }
//     });

//     const dataByProvince = {}; // 先按省汇总城市数据
//     res.data.forEach(item => {
//         const { city, value } = item;
//         // 使用一个省市映射（可以前端维护一个映射表，或后端直接返回）
//         const province = cityToProvinceMap[city];
//         if (!province) return;
//         if (!dataByProvince[province]) dataByProvince[province] = [];
//         dataByProvince[province].push(value);
//     });

//     const provinceAvg = Object.entries(dataByProvince).map(([province, values]) => {
//         const avg = values.reduce((a, b) => a + b, 0) / values.length;
//         return { name: province, value: avg.toFixed(2) };
//     });

//     chart.value.setOption({
//         series: [{
//             data: provinceAvg
//         }]
//     });
// }, { deep: true });
</script>

<style scoped>
.map-chart {
    width: 100%;
    height: 100%;
    margin-top: -5rem;
}
</style>