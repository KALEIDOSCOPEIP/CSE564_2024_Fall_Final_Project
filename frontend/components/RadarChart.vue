<template>
    <div class="radar-container">
        <multiselect
            v-model="cities"
            :options="all_cities"
            :multiple="true"
            :close-on-select="true"
            placeholder="Choose cities (maximum 4)"
            class="select" 
            @input="onSelectLimit"
            style="margin-bottom:-2rem; margin-top: 1.5rem; z-index: 1;"/>
        <v-chart v-if="radarOptions" :option="radarOptions" autoresize />
    </div>
</template>

<script setup>
import { ref, onMounted, toRefs, defineProps, watch } from 'vue'
import VChart from 'vue-echarts'
import axios from 'axios'
import Multiselect from 'vue-multiselect'

// const props = defineProps({
//     cities: {
//         type: Array,
//         default: () => ['北京', '上海', '广州', '哈尔滨'],
//         required: true
//     },
//     cityColors: {
//         type: Array,
//         default: () => ['#3366CC', '#DC3912', '#FF9900', '#109618',],
//         required: true
//     }
// })

// 初始城市列表
// const cities = ['北京', '上海', '广州', '哈尔滨']

// const {cities, cityColors} = toRefs(props)
const radarOptions = ref({})

const cities = ref(['Beijing', 'Shanghai',])
const cityColors = ref(['#3366CC', '#DC3912', '#FF9900', '#109618'])
const all_cities = ref([])
function onSelectLimit(selectedCities) {
  if (selectedCities.length > 4) {
    selectedCities.pop()
    alert('Maximum 4 cities for now.')
  }
  cities.value = selectedCities
}

// 拉数据并渲染
async function fetchRadar() {
  // 请求例如 /api/radar-data?cities=Beijing,Shanghai,...
  const res = await axios.get('http://localhost:5000/api/radar-data', {
    params: { cities: cities.value.join(',') }
  })
  const data = res.data  // 假设格式：[{ city: 'Beijing', PM2.5: xx, ...}, ...]
  const seriesData = data.series.map(cityItem => ({
      name: cityItem.city,
      value: cityItem.values
    }))
//   console.log('雷达图数据:', data)
//   console.log('城市颜色', cityColors)

  radarOptions.value = {
    tooltip: {},
    legend: { 
        data: cities.value,
        orient: 'vertical',
        left: '70%',
        top: '72%',
        textStyle: {
            color: '#fff'
        }
    },
    radar: {
      indicator: [
        { name: 'PM2.5' },{ name: 'O3' },{ name: 'CO' },
        { name: 'SO2' },{ name: 'NO2' },{ name: 'PM10' }
      ],
      shape: 'polygon',
      radius: '65%',
      
    },
    series: [{
      type: 'radar',
      data: seriesData
    //   data: data.series.map((d, idx) => ({
    //     name: d.city,
    //     value: [
    //       d['PM2.5'], d.O3, d.CO, d.SO2, d.NO2, d.PM10
    //     ],
    //     // ② 给每条线设置对应颜色
    //     lineStyle: { color: cityColors.value[idx] },
    //     itemStyle: { color: cityColors.value[idx] }
    //   }))
    }]
  }
}

// onMounted(() => {
//   fetchRadar()
// })

// watch([cities, cityColors], () => {
//   fetchRadar()
// })

// // 图表配置
// const option = ref(null)

// //拉数据


// onMounted(async () => {
//   try {
//     const { data } = await axios.get('http://localhost:5000/api/radar-data', {
//       params: { cities: cities.join(',') }
//     })

//     const indicators = data.pollutants.map(p => ({
//       name: p,
//       max: data.maxValue  // 可统一最大值，方便比较
//     }))

//     const seriesData = data.series.map(cityItem => ({
//       name: cityItem.city,
//       value: cityItem.values
//     }))

//     // console.log('雷达图数据:', data)

//     option.value = {
//     //   title: { text: '主要城市各类污染物雷达图', left: 'center' },
//       tooltip: {},
//       legend: {
//         data: cities,
//         orient: 'vertical',
//         left: 'right',
//         top: 'middle',
//         textStyle: {
//             color: '#fff'
//         }
//       },
//       radar: {
//         indicator: indicators,
//         shape: 'polygon',
//         radius: '65%',
//         axisName: {
//             fontSize: 13,
//         }
//       },
//       series: [{
//         type: 'radar',
//         data: seriesData
//       }]
//     }

//     // console.log("🔍 Radar Option: ", JSON.stringify(option.value, null, 2))
//   } catch (error) {
//     console.error('❌ 获取雷达图数据失败:', error)
//   }
// })

const fetchCities = async () => {
  const res = await axios.get('http://localhost:5000/api/cities')
  all_cities.value = await res.data
}

onMounted( async () => {
  fetchCities()
  fetchRadar()
})

watch(
    () => cities.value,
    () => {
        onSelectLimit(cities.value)
        fetchRadar()
    }
)
</script>

<style scoped>
.radar-container {
  width: 400px;
  height: 400px;
  position: relative;
  margin-top: -2rem;
  margin-bottom: -5rem;
  /* margin-right: 2rem;; */
  /* border: 10px solid #374151; */
}

.v-chart {
  width: 100%;
  height: 100%;
  overflow: visible;
  overflow-x: visible;;
  z-index: 1;
  /* border: 10px dashed white; */
}
</style>