<template>
    <div class="sunburst-chart-container">
        <h2 style="text-align: center; margin-top: -1rem; color: azure;">Top-5 of Each Air Pollutant</h2>
        <div class="sunburst-sector" style="position:relative;">
            <v-chart
            v-if="option"
            :option="option"
            autoresize
            @click="handleClick"
            class="sunburst-chart"
        />
            <div v-if="isLoading" class="loading-overlay">
                <div class="spinner"></div>
            </div>
        </div>
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
const isLoading = ref(false)

onMounted(async () => {
  isLoading.value = true
  try {
    const { data } = await axios.get('http://localhost:5000/api/sunburst-data')

    console.log('获取旭日图数据:', data)

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
        formatter: '{b}: {c}'
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
            itemStyle: { color: '#eeeeee' },
            label: { color: '#000000', fontWeight: 'bold' }
          },
          {
            // 第 2 层：污染物
            r0: '15%',
            r: '50%',
            label: { rotate: 'tangential', fontSize: 12 }
          },
          {
            // 第 3 层：省份
            r0: '50%',
            r: '90%',
            label: { fontSize: 11 }
          }
        ]
      }
    }
  } catch (error) {
    console.error('❌ 获取旭日图数据失败:', error)
  } finally {
    isLoading.value = false
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
  if (pollutant && province && pollutant !== '全国') {
    console.log(`点击了 ${pollutant} / ${province}`)
    // 可使用 emit、Pinia、eventBus 或 route 传递参数到折线图组件
    // emit('selected', { province, pollutant })
  }
}
</script>



<style scoped>
.sunburst-chart-container {
    height: 40%;
    background-color: rgba(47, 47, 47, 0); /* 深色背景 2f2f2f */
    padding: 2rem;
    border-radius: 15px;
    display: flex;
    flex-direction: column;
}

.sunburst-sector {
    display: flex;
    gap: 1rem;
    margin-bottom: -10rem;
    flex: 1;
    overflow: hidden;
    position: relative;
}

.sunburst-chart {
  width: 100%;
  height: 100%;
  /* margin-top: 10%; */
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
