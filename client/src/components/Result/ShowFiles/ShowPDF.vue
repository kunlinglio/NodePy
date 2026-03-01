<script lang="ts" setup>
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import VuePdfEmbed from 'vue-pdf-embed'

const props = defineProps<{
  src: string
}>()

const pageCount = ref<number>(0)
const pdfWrapperRef = ref<HTMLElement | null>(null)
const containerWidth = ref<number>(0)
// 使用 key 强制重新渲染 PDF
const pdfKey = ref<number>(0)
let resizeObserver: ResizeObserver | null = null

const handlePdfLoad = (pdf: any) => {
  pageCount.value = pdf.numPages
}

const handlePdfError = (error: any) => {
  console.error('PDF加载失败:', error)
}

// 监听容器宽度变化，在宽度变化时重新渲染 PDF
const updateContainerWidth = () => {
  if (pdfWrapperRef.value) {
    const newWidth = pdfWrapperRef.value.clientWidth
    // 只有宽度变化超过 10px 时才触发重新渲染，避免频繁刷新
    if (Math.abs(newWidth - containerWidth.value) > 10) {
      containerWidth.value = newWidth
      // 通过改变 key 强制 Vue 重新渲染 VuePdfEmbed 组件
      pdfKey.value += 1
    }
  }
}

onMounted(() => {
  // 初始化容器宽度
  if (pdfWrapperRef.value) {
    containerWidth.value = pdfWrapperRef.value.clientWidth
  }
  
  // 监听窗口大小变化
  window.addEventListener('resize', updateContainerWidth)
  
  // 使用 ResizeObserver 监听容器自身的宽度变化（更精准，可捕获模态框拖拽改变大小）
  try {
    if (typeof ResizeObserver !== 'undefined') {
      resizeObserver = new ResizeObserver(() => {
        updateContainerWidth()
      })
      if (pdfWrapperRef.value) {
        resizeObserver.observe(pdfWrapperRef.value)
      }
    }
  } catch (e) {
    // ignore if ResizeObserver not available
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', updateContainerWidth)
  try {
    if (resizeObserver) {
      resizeObserver.disconnect()
      resizeObserver = null
    }
  } catch (e) {
    // ignore
  }
})
</script>

<template>
  <div class="pdf-view" ref="pdfWrapperRef">
    <div class="pdf-content">
      <div class="pdf-center">
        <!-- 使用 :key 强制在宽度变化时重新渲染 PDF -->
        <VuePdfEmbed
          :key="pdfKey"
          :source="src"
          @loaded="handlePdfLoad"
          @error="handlePdfError"
          class="pdf-embed"
        />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '../../../common/global.scss' as *;
.pdf-view {
  flex: 1;
  overflow: hidden;
  background: white;
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  position: relative;
  height: 100%; /* 确保占满容器高度 */
  @include controller-style;
}

.pdf-content {
  flex: 1;
  overflow: auto;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  /* 修复滚动条问题 */
  scrollbar-gutter: stable; /* 保持滚动条空间一致 */
}

.pdf-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  /* 添加最小宽度以确保内容正确显示 */
  min-width: fit-content;
}

.pdf-embed {
  width: 100%;
  /* 确保PDF适应容器 */
  object-fit: contain;
  margin-bottom: 20px;
}
</style>