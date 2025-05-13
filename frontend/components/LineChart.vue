// LineChart.vue - Vue 3 折线图组件（支持缩放、平移、动态横轴标签）
<template>
    <div class="chart-container">
        <h2 style="text-align: center; margin-top: -3rem; color: azure;">Multi-city Pollutant Trend thr. Years</h2>
        <div class="selectors">
            <div id="city-select">
                <Multiselect 
                v-model="selectedCities" 
                :options="allCities" 
                :multiple="true" 
                :close-on-select="false" 
                @input="onCityToggle"
                placeholder="Choose cities" 
                class="select" />
            </div>
            <div id="pollutant-select">
                <Multiselect v-model="selectedType" :options="pollutants" placeholder="Pollutant" class="select" trake-by="value" style="z-index: 1;"/>
            </div>
        </div>
        <div class="chart">
            <Line v-if="chartData" ref="chartRef" :data="chartData" :options="chartOptions" />
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import Multiselect from 'vue-multiselect'
import { Line } from 'vue-chartjs'
import { Chart, registerables } from 'chart.js'
import zoomPlugin from 'chartjs-plugin-zoom'

Chart.register(...registerables, zoomPlugin)

const allCities = ref([])
const selectedCities = ref([
    'Beijing',
    'Shanghai',
    'Guangzhou',
    'Harbin'
])
const selectedType = ref('AQI')
const pollutants = ['AQI', 'PM2.5', 'PM10', 'SO2', 'NO2', 'O3', 'CO']
const chartData = ref(null)
const chartRef = ref(null)
const COLORS = [
    '#3366CC', '#DC3912', '#FF9900', '#109618', '#990099',
    '#0099C6', '#DD4477', '#66AA00', '#B82E2E', '#316395'
]

const emit_selectedCities = defineEmits(['update:selectedCities'])
function onCityToggle(city) {
    emit('update:selectedCities', newList)
}

function resetZoom() {
    if (chartRef.value) {
        chartRef.value.resetZoom()
    }
}

const fetchCities = async () => {
    const res = await fetch('http://localhost:5000/api/cities')
    allCities.value = await res.json()
}

const fetchChartData = async () => {
    if (!selectedCities.value.length) return
    const params = new URLSearchParams()
    selectedCities.value.forEach(c => params.append('cities', c))
    params.append('type', selectedType.value)
    const res = await fetch(`http://localhost:5000/api/multi_city_timeseries?${params}`)
    const data = await res.json()

    const dates = [...new Set(data.map(row => row.date))].sort()
    chartData.value = {
        labels: dates,
        datasets: selectedCities.value.map((city, i) => {
            const values = dates.map(d => {
                const item = data.find(r => r.city === city && r.date === d)
                return item ? item.value : null
            })
            return {
                label: city,
                data: values,
                borderColor: COLORS[i % COLORS.length],
                borderWidth: 2,
                pointRadius: 2
            }
        })
    }
}

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
        x: {
            title: { display: true, text: 'Year', color: 'rgb(180, 180, 180)' },
            type: 'category',
            ticks: {
                color: 'rgb(180, 180, 180)',
                autoSkip: true,
                autoSkipPadding: 25,
                maxTicksLimit: 15,
                stepSize: 100,
                callback: function(value, index, ticks) {
                    const raw = this.getLabelForValue(value);
                    const label = String(raw);
                    const zoomLevel = ticks.length;
                    if (zoomLevel < 100) return label.slice(0, 4) + '/' + label.slice(4, 6);
                    return label.slice(0, 4);
                },
                maxRotation: 0,
            },
            grid: {
                color: 'rgba(255,255,255,0.1)', // 网格线颜色（可选）
            },
        },
        y: {
            beginAtZero: true,
            ticks: {
                color: 'rgb(180, 180, 180)', // ⬅ 纵轴刻度文字颜色
            },
            grid: {
                color: 'rgba(210,210,210,0.1)', // 网格线颜色（可选）
            },
        },
    },
    plugins: {
        legend: {
            position: 'top',
            labels: {
                color: 'rgb(180, 180, 180)', // ⬅ 图例文字颜色
            },
        },
        zoom: {
            pan: {
                enabled: true,
                mode: 'x',
            },
            zoom: {
                wheel: {
                    enabled: true,
                },
                drag: {
                    enabled: true,
                },
                pinch: {
                    enabled: true,
                },
                mode: 'x',
            },
            limits: {
                x: { min: 'original', max: 'original', minRange: 10 },
                y: { min: 0, max: 'original' },
            },
        },
    },
};


// const chartOptions = {
//     responsive: true,
//     maintainAspectRatio: false,
//     scales: {
//         x: {
//             title: { display: true, text: 'Year', color: 'rgb(180, 180, 180)' },
//             type: 'category',
//             ticks: {
//                 color: 'rgb(180, 180, 180)',
//                 autoSkip: true,
//                 autoSkipPadding: 25,
//                 maxTicksLimit: 15,
//                 stepSize: 100,
//                 callback: function(value, index, ticks) {
//                     const raw = this.getLabelForValue(value);
//                     const label = String(raw);
//                     const zoomLevel = ticks.length;
//                     const year = label.slice(0, 4)
//                     if (zoomLevel < 100) return label.slice(0, 4) + '/' + label.slice(4, 6);
//                     return label.slice(0, 4);
//                 },
//                 maxRotation: 0,
//             },
//             grid: {
//                 color: 'rgba(255,255,255,0.1)', // 网格线颜色（可选）
//             },
//         },
//         y: {
//             beginAtZero: true,
//             ticks: {
//                 color: 'rgb(180, 180, 180)', // ⬅ 纵轴刻度文字颜色
//             },
//             grid: {
//                 color: 'rgba(210,210,210,0.1)', // 网格线颜色（可选）
//             },
//         },
//     },
//     plugins: {
//         legend: {
//             position: 'top',
//             labels: {
//                 color: 'rgb(180, 180, 180)', // ⬅ 图例文字颜色
//             }
//         },
//         tooltip: {
//             callbacks: {
//                 label: function(context) {
//                     return `${context.dataset.label}: ${context.formattedValue}`;
//                 },
//             },
//         },
//         onClick: (evt, elements) => {
//             if (elements.length > 0) {
//                 const idx = elements[0].index;
//                 const dateLabel = chartData.value.labels[idx];
//                 const yearMonth = dateLabel.slice(0, 7); // "YYYY-MM"

//                 emit("date-selected", {
//                     date: yearMonth,
//                     pollutant: selectedType.value, // 当前选定污染物
//                 });
//             }
//         }
//         zoom: {
//             pan: {
//                 enabled: true,
//                 mode: 'x',
//             },
//             zoom: {
//                 wheel: {
//                     enabled: true,
//                 },
//                 drag: {
//                     enabled: true,
//                 },
//                 pinch: {
//                     enabled: true,
//                 },
//                 mode: 'x',
//             },
//             limits: {
//                 x: { min: 'original', max: 'original', minRange: 10 },
//                 y: { min: 0, max: 'original' }
//             },
//         },
//     },
// };

onMounted(() => {
    fetchCities()
    fetchChartData()
})

watch([selectedCities, selectedType], fetchChartData)
</script>

<style scoped>
.chart-container {
    height: 40vh;
    background-color: rgba(47, 47, 47, 0);
    padding: 2rem;
    border-radius: 15px;
    display: flex;
    flex-direction: column;
}

.selectors {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
}

.select {
    flex: 1;
}

.chart {
    flex: 1;
    overflow: hidden;
}

#city-select {
    width: 70%;
}

#pollutant-select {
    width: 30%;
}
</style>