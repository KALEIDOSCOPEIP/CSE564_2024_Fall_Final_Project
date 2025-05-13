<template>
    <div class="sunburst-sector">
            <v-chart
            v-if="option"
            :option="option"
            autoresize
            @click="handleClick"
            class="sunburst-chart"
        />
        </div>
</template>

<!-- <script setup>
import { ref, onMounted } from 'vue'
import VChart from 'vue-echarts'
import axios from 'axios'

// 固定污染物颜色（主色）
const pollutantColors = {
  'PM2.5': '#e74c3c',
  'PM10': '#f39c12',
  'NO2': '#3498db',
  'SO2': '#1abc9c',
  'CO': '#9b59b6',
  'O3': '#2ecc71'
}

// 注册组件
const option = ref(null)

onMounted(async () => {
  try {
    const { data } = await axios.get('http://localhost:5000/api/sunburst-data')

    // 给第二层和第三层赋予颜色（污染物主色 & 渐变）
    data.children.forEach(pollutantNode => {
      const baseColor = pollutantColors[pollutantNode.name] || '#888'

      // 第二层（污染物类型）
      pollutantNode.itemStyle = {
        color: baseColor
      }

      // 第三层（前5省份）按值排序并加深颜色
      pollutantNode.children.sort((a, b) => b.value - a.value)
      const total = pollutantNode.children.length
      pollutantNode.children.forEach((provinceNode, idx) => {
        const factor = 0.5 + 0.5 * (1 - idx / (total - 1))  // 从 1.0 到 0.5
        provinceNode.itemStyle = {
          color: shadeColor(baseColor, factor)
        }
      })
    })

    option.value = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c}',
      },
      series: {
        type: 'sunburst',
        radius: [0, '95%'],
        data: [data],
        label: {
          rotate: 'radial',
          color: 'rgb(220, 220, 220)',
          fontSize: 10,
        },
        emphasis: {
          focus: 'ancestor'
        }
        levels: [
          {
            itemStyle: {
              borderColor: '#eeeeee',
              borderWidth: 2
            },
            label: {
              fontSize: 12,
              color: '#000000'
            }
          },
          {
            itemStyle: {
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              fontSize: 12,
              color: '#fff'
            }
          },
          {
            itemStyle: {
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              fontSize: 12,
              color: '#fff'
            }
          }
        ]
      }
    }
  } catch (error) {
    console.error('❌ 获取旭日图数据失败:', error)
  }
})

function handleClick(params) {
  const province = params.data.name
  const pollutant = params.treePathInfo?.[1]?.name
  if (pollutant && province && pollutant !== '全国') {
    console.log(`点击了 ${pollutant} / ${province}`)
    // emit 或 Vuex/Pinia 联动更新折线图
    // emit('provinceSelected', { province, pollutant })
  }
}
</script> -->










<script setup>
import { ref, onMounted } from 'vue'
import VChart from 'vue-echarts'
import axios from 'axios'
import { min } from 'd3'

// 固定污染物颜色
const pollutantColors = {
  'PM2.5': '#e74c3c',
  'PM10': '#f39c12',
  'NO2': '#3498db',
  'SO2': '#1abc9c',
  'CO': '#9b59b6',
  'O3': '#2ecc71'
}

const option = ref(null)

onMounted(async () => {
  try {
    const { data } = await axios.get('http://localhost:5000/api/sunburst-data')

    // console.log('获取旭日图数据:', data)

    // 给每个节点设置颜色
    data.children.forEach(pollutantNode => {
      const baseColor = pollutantColors[pollutantNode.name] || '#888888'

      // 污染物层颜色（第2层）
      pollutantNode.itemStyle = {
        color: baseColor
      }

      // 按值排序 + 渐变颜色（第3层）
      pollutantNode.children.sort((a, b) => b.value - a.value)
      const total = pollutantNode.children.length
      pollutantNode.children.forEach((provinceNode, idx) => {
        const factor = 0.5 + 0.5 * (1 - idx / Math.max(1, total - 1))  // 深 → 浅
        provinceNode.itemStyle = {
          color: shadeColor(baseColor, factor)
        }
      })
    })

    // 构建图表配置项
    option.value = {
    //   title: {
    //     text: '污染物 Top5 省份分布',
    //     left: 'center',
    //     textStyle: { fontSize: 18 }
    //   },
      tooltip: {
        trigger: 'item',
        // formatter: '{b}: {c}'
        formatter: params => {
            return `${params.name} ${Number(params.value).toFixed(2)}`
        }
      },
      series: {
        type: 'sunburst',
        data: [data],
        radius: [0, '90%'],
        label: {
          rotate: 'radial',
          color: '#000'
        },
        levels: [
          {
            // 第 1 层：全国
            r0: '0%',
            r: '0%',
            itemStyle: { color: '#eeeeee' },
            label: { color: '#000000', fontWeight: 'bold' }
          },
          {
            // 第 2 层：污染物
            r0: '0%',
            r: '15%',
            label: { rotate: 'tangential', fontSize: 12 }
          },
          {
            // 第 3 层：省份
            r0: '15%',
            r: '40%',
            label: { rotate: 'radial', fontSize: 11 }
          },
          {
            // 第 4 层：省份细节
            r0: '40%',
            r: '100%',
            minShow: false,
            minAngle: 20,
            label: { 
                // show: (params) => {
                //     const parent = params.treePathInfo?.[1]
                //     const total = parent.value || 1
                //     const current = params.data.value || 0
                //     return current / total > 0.05 // 只显示占比大于5%的省份
                // },
                formatter: params => {
                    const parent = params.treePathInfo?.[1]
                    const total = parent?.value || 1
                    const current = params?.data?.value || 0
                    const ratio = current / total
                    // console.log('当前省份:', params.name, '占比:', ratio)
                    return ratio > 0.5 ? params.name : ''
                },
                rotate: 'radial',
                fontSize: 12 },
          }
        ]
      }
    }
  } catch (error) {
    console.error('❌ Fail to fetch information', error)
  }
})

// 颜色渐变工具函数
function shadeColor(hex, factor = 1.0) {
  const f = parseInt(hex.slice(1), 16)
  const r = f >> 16
  const g = (f >> 8) & 0x00FF
  const b = f & 0x0000FF
  const toHex = v => Math.min(255, Math.round(v)).toString(16).padStart(2, '0')
  return `#${toHex(r * factor)}${toHex(g * factor)}${toHex(b * factor)}`
}

// 点击事件：触发联动
function handleClick(params) {
  const province = params.data.name
  const pollutant = params.treePathInfo?.[1]?.name
  if (pollutant && province && pollutant !== 'Nation') {
    // console.log(`点击了 ${pollutant} / ${province}`)
    // 可使用 emit、Pinia、eventBus 或 route 传递参数到折线图组件
    // emit('selected', { province, pollutant })
  }
}
</script>



<style scoped>
.sunburst-chart-container {
    /* height: 27vh;
    background-color: rgba(47, 47, 47, 0);
    padding: 2rem;
    border-radius: 15px;
    display: flex;
    flex-direction: column;
    margin-left: -20rem; */
    width: 400px;
  height: 400px;
  position: relative;
  margin-top: -2rem;
}

.sunburst-sector {
    /* display: flex;
    gap: 1rem;
    margin-bottom: -6rem;
    flex: 1;
    overflow: hidden; */
    width: 350px;
    height: 450px;
    position: relative;
    margin-top: -3rem;
    margin-bottom: -5rem;
}

.sunburst-chart {
  width: 100%;
  height: 100%;
  /* margin-top: 10%; */
}
</style>
