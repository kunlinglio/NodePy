<script lang="ts" setup>
import { computed, ref, onMounted, onUnmounted, nextTick } from 'vue'

const props = defineProps<{
  data: string
}>()

// 虚拟滚动相关状态
const containerRef = ref<HTMLElement | null>(null)
const lineHeight = ref(20) // 行高（px）
const containerHeight = ref(0)
const containerWidth = ref(0)
const scrollTop = ref(0)
const bufferCount = ref(10) // 缓冲行数
const renderKey = ref(0) // 用于强制重新渲染虚拟滚动

// 防抖和 ResizeObserver
let resizeTimer: number | null = null
let scrollTimer: number | null = null
let resizeObserver: ResizeObserver | null = null

// 所有行数据计算
const allLines = computed(() => {
  // 使用 split('\n') 会保留空行
  return props.data.split('\n')
})

// 计算虚拟滚动的可见范围
const totalRows = computed(() => allLines.value.length || 0)

const visibleRange = computed(() => {
  const ch = containerHeight.value || 0
  const rh = lineHeight.value
  const visibleCount = Math.ceil(ch / rh)
  const start = Math.max(0, Math.floor((scrollTop.value || 0) / rh) - bufferCount.value)
  const end = Math.min(totalRows.value, start + visibleCount + bufferCount.value * 2)
  return { start, end }
})

const visibleLines = computed(() => {
  const { start, end } = visibleRange.value
  return allLines.value.slice(start, end)
})

const topSpacerHeight = computed(() => visibleRange.value.start * lineHeight.value)
const bottomSpacerHeight = computed(() => Math.max(0, (totalRows.value - visibleRange.value.end) * lineHeight.value))

// 初始化虚拟滚动
const initVirtualScroll = async () => {
  if (!containerRef.value) return
  
  try {
    await nextTick()
    
    if (!containerRef.value) return
    
    // 获取容器高度和宽度
    containerHeight.value = containerRef.value.clientHeight
    containerWidth.value = containerRef.value.clientWidth
    scrollTop.value = 0 // 重新渲染时重置滚动位置
    
    // 添加滚动事件监听器
    containerRef.value.addEventListener('scroll', handleScroll, { passive: true })
  } catch (err) {
    console.error('初始化虚拟滚动失败:', err)
  }
}

// 处理滚动事件
const handleScroll = (e: Event) => {
  if (!containerRef.value) return
  
  if (scrollTimer) return
  
  scrollTimer = requestAnimationFrame(() => {
    try {
      const target = e.target as HTMLElement
      scrollTop.value = target.scrollTop
    } catch (err) {
      console.error('处理滚动事件失败:', err)
    } finally {
      scrollTimer = null
    }
  })
}

// 处理容器宽度/高度变化 - 使用防抖，只在宽度变化明显时才重新渲染
const handleWindowResize = () => {
  if (!containerRef.value) return
  
  if (resizeTimer) clearTimeout(resizeTimer)
  
  resizeTimer = window.setTimeout(() => {
    try {
      const newHeight = containerRef.value!.clientHeight
      const newWidth = containerRef.value!.clientWidth
      const widthChanged = Math.abs(newWidth - containerWidth.value) > 10
      
      if (widthChanged) {
        // 宽度变化超过10px时，改变key强制重新渲染虚拟滚动
        renderKey.value += 1
        containerHeight.value = newHeight
        containerWidth.value = newWidth
      } else {
        // 只有高度变化时
        containerHeight.value = newHeight
        containerWidth.value = newWidth
      }
    } catch (err) {
      console.error('处理窗口大小变化失败:', err)
    }
  }, 300) // 300ms防抖延迟，确保拖动结束后才更新
}

// 组件挂载时初始化虚拟滚动
onMounted(() => {
  initVirtualScroll()
  
  window.addEventListener('resize', handleWindowResize, { passive: true })
  
  // 使用 ResizeObserver 监听容器自身的尺寸变化
  try {
    if (typeof ResizeObserver !== 'undefined' && containerRef.value) {
      resizeObserver = new ResizeObserver(() => {
        handleWindowResize()
      })
      resizeObserver.observe(containerRef.value)
    }
  } catch (e) {
    // ignore if ResizeObserver not available
  }
})

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', handleWindowResize)
  if (containerRef.value) {
    containerRef.value.removeEventListener('scroll', handleScroll)
  }
  try {
    if (resizeObserver) {
      resizeObserver.disconnect()
      resizeObserver = null
    }
  } catch (e) {
    // ignore
  }
  if (resizeTimer) clearTimeout(resizeTimer)
  if (scrollTimer) cancelAnimationFrame(scrollTimer)
})
</script>

<template>
  <div class="txt-view" ref="containerRef" :key="renderKey">
    <div class="txt-content">
      <!-- 顶部间隔 -->
      <div :style="{ height: topSpacerHeight + 'px', margin: 0, padding: 0 }"></div>
      <!-- 可见行 -->
      <div v-for="(line, index) in visibleLines" :key="visibleRange.start + index" class="txt-line">
        <span v-if="line === ''">&nbsp;</span>
        <span v-else>{{ line }}</span>
      </div>
      <!-- 底部间隔 -->
      <div :style="{ height: bottomSpacerHeight + 'px', margin: 0, padding: 0 }"></div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '../../../common/global.scss' as *;
.txt-view {
  flex: 1;
  overflow: hidden; /* 改为hidden，让内部控制滚动 */
  background: white;
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  height: 100%; /* 确保占满容器高度 */
  @include controller-style;
  /* 优化渲染性能 */
  transform: translateZ(0);
  backface-visibility: hidden;
}

.txt-content {
  flex: 1;
  overflow: auto; /* 让内容区域控制滚动 */
  font-family: 'Courier New', Consolas, Monaco, monospace;
  white-space: pre-wrap; /* 允许自动换行 */
  word-wrap: break-word; /* 允许长单词换行 */
  line-height: 1.5;
  /* 修复滚动条问题 */
  scrollbar-gutter: stable; /* 保持滚动条空间一致 */
  padding: 8px; /* 添加一些内边距 */
  box-sizing: border-box;
  /* 优化渲染性能 */
  transform: translateZ(0);
  backface-visibility: hidden;
  /* 使用contain属性优化渲染性能 */
  contain: layout style paint;
}

.txt-line {
  margin: 0;
  padding: 2px 0;
  font-family: inherit;
  /* 确保空行也能正确显示 */
  min-height: 1.2em;
  /* 不再强制每行占据整行 */
  display: block;
  /* 优化渲染性能 */
  transform: translateZ(0);
  backface-visibility: hidden;
  /* 使用contain属性优化渲染性能 */
  contain: layout style;
}
</style>