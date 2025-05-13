<template>
  <div ref="vantaRef" class="vanta-bg">
    <!-- 这里可以放插槽内容，或者留空背景 -->
    <slot></slot>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as THREE from 'three'
import NET from 'vanta/dist/vanta.net.min'  // 以“网格”效果为例
import WAVES from 'vanta/dist/vanta.waves.min' // 以“波浪”效果为例

const vantaRef = ref(null)
let vantaEffect = null

onMounted(() => {
  if (!vantaEffect) {
    // vantaEffect = WAVES({
    //   el: vantaRef.value,
    //   THREE,                // three 库必须传入
    //   color: 0x1a1a1a,      // 网格主色，可配置
    //   backgroundColor: 0x0a0a0a,
    //   points: 15.0,
    //   maxDistance: 20.0,
    //   spacing: 18.0
    // })
    vantaEffect = WAVES({
      el: vantaRef.value,
      THREE,
      color: 0xffffff,
      backgroundColor: 0xffffff,
      shininess: 20.0,
      waveHeight: 20.0,
      waveSpeed: 0.8,
      zoom: 1.2
    })
  }
})

onBeforeUnmount(() => {
  if (vantaEffect) {
    vantaEffect.destroy()
    vantaEffect = null
  }
})
</script>

<style scoped>
.vanta-bg {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: -1;  /* 确保在可视化图表后面 */
}
</style>
