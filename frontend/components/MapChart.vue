<template>
    <div class="map-chart-container">
        <h2 style="text-align: center; margin-top: -2rem; color: azure;">Multi-city Pollutant Trend thr. Years</h2>
        <div style="text-align: center; width: 100%; z-index: 1;">
            <table style="text-align: center; width: 100%;">
                <tr style="align-items: flex-start; display: flex;">
                    <td>
                        <div style="width: 6vw; margin-left: 25rem;">
                            <Multiselect
                            :options="allYears"
                            :multiple="false"
                            :close-on-select="true"
                            v-model="selectedYear"
                            />
                        </div>
                    </td>
                    <td>
                        <div style="width: 6vw;">
                            <Multiselect
                            :options="allMonths"
                            :multiple="false"
                            :max-choice="10"
                            :close-on-select="true"
                            v-model="selectedMonth"
                            />
                        </div>
                    </td>
                    <td>
                        <div style="width: 6vw;">
                            <Multiselect
                            :options="allPollutants"
                            :multiple="false"
                            :close-on-select="true"
                            v-model="selectedPollutant"
                            />
                        </div>
                    </td>
                </tr>
            </table>
        </div>
        <v-chart :option="mapOptions" autoresize class="map-chart" />
        <span 
        style="text-align: center;
        color: rgba(180, 180, 180, 0.5);
        font-family: 'Times New Roman', Times, serif;
        font-size: 1.5rem;">
            Zikai Liao, Rishav Pramanik - 05/2025
        </span>
    </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import { use } from 'echarts/core'
import VChart from 'vue-echarts'
import Multiselect, { multiselectMixin } from 'vue-multiselect'
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

const allYears = [
    '2014', '2015', '2016', '2017', '2018', '2019',
    '2020', '2021', '2022', '2023', '2024', '2025',
]
const allMonths = [
    '01', '02', '03', '04', '05', '06',
    '07', '08', '09', '10', '11', '12',
]
const allPollutants = [
    'PM2.5', 'PM10', 'NO2', 'CO', 'SO2', 'AQI', 'O3',
]
const selectedYear = ref('2014')
const selectedMonth = ref('05')
const selectedPollutant = ref('AQI')

const chart = ref(null);
// const chartRef = ref(null);

const updateMap = async (date, pollutant) => {
  if (!date || !pollutant) return;
  console.log('lol');

  const res = await axios.get("http://localhost:5000/api/monthly_city_values", {
    params: { date, type: pollutant }
  });
  console.log('地图数据:', res.data);

  const provinces_res = await axios.get("http://localhost:5000/api/province_info");
  const provinces = provinces_res.data;

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
      Date: ${selectedYear.value}-${selectedMonth.value}

      Pollutant: ${selectedPollutant.value}
      `,
      left: 'center',
      top: '15%',
      left: '40%',
      textStyle: {
        color: 'azure',
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: params => {
        const info = provinces.find(p => p.province === params.name)
        if (!info) return `${params.name}`
        return `
          <strong>${params.name}</strong><br/>
          ${pollutant}: ${params.value}<br/>
          Population: ${info.population.toLocaleString()} Mil.<br/>
          GDP: ${info.gdp} Tri. ￥<br/>
          Coastline: ${info.is_coastal}<br/>
          Climate: ${info.climate_type}<br/>
          Region: ${info.region}<br/>
        `
      }
    },
    visualMap: {
      min: Math.min(...res.data.map(d => d.value), 50),
      max: Math.max(...res.data.map(d => d.value), 2),
      left: '80%',
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
        roam: false,
        zoom: 1,
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
  const year = selectedYear.value;
  const month = selectedMonth.value;
  const date = `${year}${month}`
  const pollutant = selectedPollutant.value;
//   console.log('地图数据:', date, pollutant);
  updateMap(date, pollutant); // ✅ 设置一个合适的默认值（你可以换成最近的数据）
//   updateMap(202001, "AQI"); // ✅ 设置一个合适的默认值（你可以换成最近的数据）
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



// // 🔄 点击折线图后触发地图更新
// watch(() => props.selectedDateInfo, async (info) => {
//   if (info?.date && info?.pollutant) {
//     updateMap(info.date, info.pollutant);
//   }
// }, { deep: true });

watch(
    () => selectedYear.value,
    () => {
    console.log('change');
  const year = selectedYear.value;
  const month = selectedMonth.value;
  const date = parseInt(`${year}${month}`);
  const pollutant = selectedPollutant.value;
  console.log('here');
  updateMap(date, pollutant);
});

watch(
    () => selectedMonth.value,
    () => {
    console.log('change');
  const year = selectedYear.value;
  const month = selectedMonth.value;
  const date = parseInt(`${year}${month}`);
  const pollutant = selectedPollutant.value;
  console.log('here');
  updateMap(date, pollutant);
});

watch(
    () => selectedPollutant.value,
    () => {
    console.log('change');
  const year = selectedYear.value;
  const month = selectedMonth.value;
  const date = parseInt(`${year}${month}`);
  const pollutant = selectedPollutant.value;
  console.log('here');
  updateMap(date, pollutant);
});

</script>

<style scoped>
.map-chart-container {
    width: 100%;
    height: 100vh;
    padding: 2rem;
    border-radius: 15px;
    display: flex;
    flex-direction: column;
}
.map-chart {
    width: 100%;
    height: 100%;
    margin-top: -5rem;
}
</style>