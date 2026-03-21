<script lang='ts' setup>
import { ref, computed, onMounted, watch } from 'vue'
//@ts-ignore
import SvgIcon from '@jamescoyle/vue-icon'
import {
  mdiBookOpenPageVariant,
  mdiCloudDownloadOutline,
  mdiCheckCircleOutline,
  mdiLightbulb,
  mdiChevronLeft,
  mdiChevronRight,
  mdiChevronDoubleLeft,
  mdiChevronDoubleRight,
  mdiHome,
  mdiRocketLaunch,
  mdiBrain,
  mdiChartTimeline,
  mdiPlaylistCheck,
  mdiRobot,
} from '@mdi/js'
import { usePageStore } from '@/stores/pageStore'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

const pageStore = usePageStore()

// 当前日期（YYYY-MM-DD）
const today = new Date().toISOString().slice(0, 10)

// 初始化 markdown-it
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return '<pre class="hljs"><code>' +
               hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
               '</code></pre>'
      } catch (__) {}
    }
    return '<pre class="hljs"><code>' + md.utils.escapeHtml(str) + '</code></pre>'
  }
})

// 教程文件映射
const tutorialFiles = [
  '1_quick_start.md',
  '2_core_concept.md',
  '3_common_data_flow.md',
  '4_logical_control_and_automation.md',
  '5_machine_learning.md'
]

const docs = ref([
  {
    id: 1,
    title: '快速上手',
    description: '搭建并运行第一个节点项目，体验节点式编程的核心流程。',
    icon: mdiRocketLaunch,
    category: 'Quickstart',
    pages: 9, // ✅ 根据实际文档统计
  },
  {
    id: 2,
    title: '核心概念',
    description: '节点图的工作方式：节点、端口、连线、数据流与类型系统。',
    icon: mdiBrain,
    category: 'Concepts',
    pages: 5,
  },
  {
    id: 3,
    title: '常见数据流程',
    description: '涵盖数据采集、清洗、分析与可视化全流程，并包含K线数据实战。',
    icon: mdiChartTimeline,
    category: 'Workflow',
    pages: 7,
  },
  {
    id: 4,
    title: '逻辑控制与自动化',
    description: '使用循环、条件判断和自定义脚本构建智能流程。',
    icon: mdiPlaylistCheck,
    category: 'Automation',
    pages: 8,
  },
  {
    id: 5,
    title: '机器学习实战',
    description: '从特征工程到模型训练、预测与评估，全程节点搭建机器学习流程。',
    icon: mdiRobot,
    category: 'Machine Learning',
    pages: 8,
  }
])

// 辅助函数：根据章节数生成阅读时间信息
const getDocInfo = (pages: number) => {
  if (pages === 0) return '加载中...'
  const minutesPerSection = 2 // 每章节约3分钟
  const totalMinutes = pages * minutesPerSection
  if (totalMinutes < 60) {
    return `共 ${pages-2} 小节，阅读约需 ${totalMinutes} 分钟`
  } else {
    const hours = Math.floor(totalMinutes / 60)
    const mins = totalMinutes % 60
    return `共 ${pages-2} 小节，阅读约需 ${hours} 小时 ${mins} 分钟`
  }
}

// 当前打开的教程ID
const currentDocId = ref<number | null>(null)
const hoverDoc = ref<number | null>(null)
const isLoading = ref(false)
const tutorialMarkdown = ref('')
const tutorialSections = ref<Array<{ title: string; content: string; html: string }>>([])
const currentSectionIndex = ref(0)

// 布局相关
const splitRatio = ref(35)
const isDragging = ref(false)
const tutorialContentRef = ref<HTMLElement | null>(null)

// 标签相关
const labelPosition = ref(25)
const isLabelDragging = ref(false)
const labelShowTime = ref<NodeJS.Timeout | null>(null)
const labelHideTime = ref<NodeJS.Timeout | null>(null)
const isLabelVisible = ref(false)
const isLabelPinned = ref(false)
const labelLastInteractTime = ref(0)
const tutorialLeftRef = ref<HTMLElement | null>(null)

// 当前显示的 HTML 内容
const currentHtml = computed(() => {
  if (tutorialSections.value.length > 0 && currentSectionIndex.value < tutorialSections.value.length) {
    return tutorialSections.value[currentSectionIndex.value]!.html
  }
  return ''
})

// 分页信息
const totalSections = computed(() => tutorialSections.value.length)
const hasPrevSection = computed(() => currentSectionIndex.value > 0)
const hasNextSection = computed(() => currentSectionIndex.value < totalSections.value - 1)

// 将 Markdown 按标题拆分为章节
const splitIntoSections = (markdown: string) => {
  const lines = markdown.split('\n')
  const sections: Array<{ title: string; content: string }> = []
  let currentContent: string[] = []
  let currentTitle = '概述'
  let inCodeBlock = false
  let hasContent = false

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]

    if (line!.trim().startsWith('```')) {
      inCodeBlock = !inCodeBlock
      currentContent.push(line!)
      continue
    }

    if (!inCodeBlock) {
      const h1Match = line!.match(/^# (.*)$/)
      const h2Match = line!.match(/^## (.*)$/)

      if (h1Match || h2Match) {
        if (hasContent || currentContent.length > 0) {
          sections.push({
            title: currentTitle,
            content: currentContent.join('\n')
          })
        }
        currentTitle = h1Match ? h1Match[1]! : (h2Match ? h2Match[2] : '')!
        currentContent = [line!]
        hasContent = true
        continue
      }
    }

    currentContent.push(line!)
    if (line!.trim()) hasContent = true
  }

  if (hasContent || currentContent.length > 0) {
    sections.push({
      title: currentTitle,
      content: currentContent.join('\n')
    })
  }

  if (sections.length === 0 && markdown.trim()) {
    sections.push({
      title: '概述',
      content: markdown
    })
  }

  return sections.map(section => ({
    title: section.title,
    content: section.content,
    html: md.render(section.content)
  }))
}

// 加载教程内容
const loadTutorial = async (docId: number) => {
  isLoading.value = true
  try {
    const fileIndex = docId - 1
    if (fileIndex >= 0 && fileIndex < tutorialFiles.length) {
      // 获取 Vite 配置的基准路径 (Vite 注入的常量)
      const baseUrl = import.meta.env.BASE_URL
      const response = await fetch(`${baseUrl}guides/${tutorialFiles[fileIndex]}`)
      if (!response.ok) throw new Error('加载失败')
      const markdown = await response.text()
      tutorialMarkdown.value = markdown
      tutorialSections.value = splitIntoSections(markdown)
      currentSectionIndex.value = 0

      const doc = docs.value.find(d => d.id === docId)
      if (doc) {
        doc.pages = tutorialSections.value.length
      }
    }
  } catch (error) {
    console.error('加载教程失败:', error)
    tutorialSections.value = [{
      title: '加载失败',
      content: '无法加载教程内容，请稍后重试。',
      html: '<p>无法加载教程内容，请稍后重试。</p>'
    }]
  } finally {
    isLoading.value = false
  }
}

// 开始拖拽
const startDragging = () => {
  isDragging.value = true
}

const stopDragging = () => {
  isDragging.value = false
}

// 处理分割线拖动
const handleMouseMove = (e: MouseEvent) => {
  if (!isDragging.value || !tutorialContentRef.value) return

  const container = tutorialContentRef.value
  const rect = container.getBoundingClientRect()
  const newRatio = ((e.clientX - rect.left) / rect.width) * 100

  if (newRatio >= 20 && newRatio <= 50) {
    splitRatio.value = newRatio
  }
}

// 处理标签拖动
const handleLabelMouseMove = (e: MouseEvent) => {
  if (!isLabelDragging.value || !tutorialLeftRef.value) return

  const container = tutorialLeftRef.value
  const rect = container.getBoundingClientRect()
  const newPosition = ((e.clientY - rect.top) / rect.height) * 100

  if (newPosition >= 10 && newPosition <= 75) {
    labelPosition.value = newPosition
  }
}

const startLabelDragging = () => {
  isLabelDragging.value = true
}

const stopLabelDragging = () => {
  isLabelDragging.value = false
}

// 显示标签
const showLabel = () => {
  isLabelVisible.value = true
  labelLastInteractTime.value = Date.now()

  if (labelHideTime.value) clearTimeout(labelHideTime.value)

  if (!isLabelPinned.value) {
    labelHideTime.value = setTimeout(() => {
      isLabelVisible.value = false
    }, 3000)
  }
}

// 切换标签常驻状态
const toggleLabelPin = () => {
  isLabelPinned.value = !isLabelPinned.value
  if (isLabelPinned.value) {
    isLabelVisible.value = true
    if (labelHideTime.value) clearTimeout(labelHideTime.value)
  } else {
    showLabel()
  }
}

const handleMouseUp = () => {
  stopDragging()
}

// 章节导航
const prevSection = () => {
  if (hasPrevSection.value) {
    currentSectionIndex.value--
    const wrapper = tutorialLeftRef.value?.querySelector('.markdown-wrapper') as HTMLElement
    if (wrapper) wrapper.scrollTop = 0
  }
}

const nextSection = () => {
  if (hasNextSection.value) {
    currentSectionIndex.value++
    const wrapper = tutorialLeftRef.value?.querySelector('.markdown-wrapper') as HTMLElement
    if (wrapper) wrapper.scrollTop = 0
  }
}

onMounted(() => {
  window.addEventListener('mousemove', handleMouseMove)
  window.addEventListener('mousemove', handleLabelMouseMove)
  window.addEventListener('mouseup', handleMouseUp)
  window.addEventListener('mouseup', stopLabelDragging)
})

// 监听教程切换
watch(currentDocId, async (newId) => {
  if (newId) {
    showLabel()
    await loadTutorial(newId)
  } else {
    tutorialSections.value = []
    currentSectionIndex.value = 0
  }
})

const currentDoc = computed(() => {
  return docs.value.find(doc => doc.id === currentDocId.value)
})

const hasPrevious = computed(() => {
  if (!currentDoc.value) return false
  return currentDoc.value.id > 1
})

const hasNext = computed(() => {
  if (!currentDoc.value) return false
  return currentDoc.value.id < docs.value.length
})

const openDoc = (doc: any) => {
  currentDocId.value = doc.id
}

const backToList = () => {
  currentDocId.value = null
}

const previousDoc = () => {
  if (currentDoc.value && currentDoc.value.id > 1) {
    currentDocId.value = currentDoc.value.id - 1
  }
}

const nextDoc = () => {
  if (currentDoc.value && currentDoc.value.id < docs.value.length) {
    currentDocId.value = currentDoc.value.id + 1
  }
}
</script>

<template>
    <div class="explore-container">
      <!-- 背景装饰元素 -->
      <div class="background-elements">
        <div class="bg-circle circle-1"></div>
        <div class="bg-circle circle-2"></div>
        <div class="bg-circle circle-3"></div>
      </div>

      <!-- 主内容区 -->
      <div class="explore-content">
        <!-- 教程列表视图 -->
        <div v-if="!currentDocId" class="section doc-section">
          <div class="section-header">
            <h2 class="section-title">
              <svg-icon :path="mdiBookOpenPageVariant" :size="32" type="mdi" class="title-icon"></svg-icon>
              教程
            </h2>
            <p class="section-subtitle">详细的参考文档，帮助您深入了解每个功能的细节</p>
          </div>

          <div class="docs-grid">
            <div
              v-for="doc in docs"
              :key="doc.id"
              class="doc-card"
              @click="openDoc(doc)"
              @mouseenter="hoverDoc = doc.id"
              @mouseleave="hoverDoc = null"
              :class="{ 'doc-card-hover': hoverDoc === doc.id }"
            >
              <div class="doc-header">
                <div class="doc-icon" :class="{ 'doc-icon-hover': hoverDoc === doc.id }">
                  <svg-icon :path="doc.icon" :size="28" type="mdi"></svg-icon>
                </div>
                <div class="doc-info">
                  <h3 class="doc-title">{{ doc.title }}</h3>
                  <div class="doc-subtitle">{{ doc.category }}</div>
                </div>
              </div>
              <p class="doc-description">{{ doc.description }}</p>
              <div class="doc-footer">
                <div class="footer-left">
                  <span class="read-time">{{ getDocInfo(doc.pages) }}</span>
                </div>
                <span class="date">{{ today }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 教程详情视图（全屏） -->
        <div v-else class="tutorial-detail-section">
          <!-- 简约标签 + 静默模式蓝色提示 -->
          <div
            class="tutorial-label"
            :style="{ top: labelPosition + '%' }"
            :class="{ 'label-visible': isLabelVisible, 'label-dragging': isLabelDragging, 'label-pinned': isLabelPinned }"
            @mouseenter="showLabel"
            @dblclick="toggleLabelPin"
            @mousedown="startLabelDragging"
          >
            <div class="label-content">
              <div class="label-text">{{ currentDoc?.title }}</div>
              <div class="label-hint" v-if="!isLabelVisible && !isLabelPinned">◀</div>
            </div>
          </div>

          <!-- 主内容容器 -->
          <div class="tutorial-content" ref="tutorialContentRef" @mousemove="handleLabelMouseMove" @mouseleave="() => { stopDragging(); stopLabelDragging(); }">
            <!-- 左侧：文档说明 + 底部固定控制栏 -->
            <div class="tutorial-left" ref="tutorialLeftRef" :style="{ width: splitRatio + '%' }">
              <div class="markdown-wrapper">
                <div class="loading-state" v-if="isLoading">
                  <p>加载教程内容中...</p>
                </div>
                <div class="markdown-content" v-else-if="currentHtml" v-html="currentHtml"></div>
                <div class="empty-state" v-else>
                  <p>暂无内容</p>
                </div>
              </div>

              <!-- 常驻底部控制栏（顺序：双左、单左、单右、双右、主页） -->
              <div class="bottom-control-bar">
                <button class="control-btn" :disabled="!hasPrevious" @click="previousDoc" title="上一个教程">
                  <svg-icon :path="mdiChevronDoubleLeft" :size="18" type="mdi"></svg-icon>
                </button>
                <button class="control-btn" :disabled="!hasPrevSection" @click="prevSection" title="上一章节">
                  <svg-icon :path="mdiChevronLeft" :size="18" type="mdi"></svg-icon>
                </button>
                <button class="control-btn" :disabled="!hasNextSection" @click="nextSection" title="下一章节">
                  <svg-icon :path="mdiChevronRight" :size="18" type="mdi"></svg-icon>
                </button>
                <button class="control-btn" :disabled="!hasNext" @click="nextDoc" title="下一个教程">
                  <svg-icon :path="mdiChevronDoubleRight" :size="18" type="mdi"></svg-icon>
                </button>
                <button class="control-btn" @click="backToList" title="回到教程列表">
                  <svg-icon :path="mdiHome" :size="18" type="mdi"></svg-icon>
                </button>
              </div>
            </div>

            <!-- 分割线 + 纯三角形指示器（无圆形背景） -->
            <div
              class="divider"
              @mousedown="startDragging"
              :class="{ 'divider-active': isDragging }"
            >
              <div class="drag-handle">▶</div>
            </div>

            <!-- 右侧：图表组件区域 -->
            <div class="tutorial-right" :style="{ width: (100 - splitRatio) + '%' }">
              <div class="graph-placeholder">
                <p>图表组件区域（待接入定制的 Graph 组件）</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<style lang='scss' scoped>
@use '@/common/global.scss' as *;
@use '@/common/node.scss' as *;

.explore-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  width: 100%;
  min-height: 0;
  overflow-x: hidden;
  background-color: #f5f7fa;
  user-select: none;
}

.background-elements {
  position: absolute;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;

  .bg-circle {
    position: absolute;
    border-radius: 50%;
    filter: blur(60px);
    opacity: 0.4;
  }

  .circle-1 {
    width: 400px;
    height: 400px;
    top: -100px;
    right: -100px;
    background: rgba(16, 142, 254, 0.08);
  }

  .circle-2 {
    width: 300px;
    height: 300px;
    bottom: 100px;
    left: -50px;
    background: rgba(16, 142, 254, 0.06);
  }

  .circle-3 {
    width: 200px;
    height: 200px;
    top: 30%;
    left: 20%;
    background: rgba(16, 142, 254, 0.04);
  }
}

.explore-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  z-index: 1;
  position: relative;
  overflow-y: auto;
  background-color: #f5f7fa;
}

.section {
  width: 100%;
  padding: 80px 40px;
  box-sizing: border-box;
  max-width: 1500px;
  margin: 0 auto;

  @media (max-width: 768px) {
    padding: 50px 20px;
  }
}

.section-header {
  text-align: center;
  margin-bottom: 60px;

  .section-title {
    font-size: 32px;
    font-weight: 800;
    color: #333;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;

    .title-icon {
      color: #108efe;
      opacity: 0.9;
    }
  }

  .section-subtitle {
    font-size: 18px;
    color: #666;
  }
}

// 文档教程部分
.doc-section {
  background: transparent;
  min-height: auto;

  .docs-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 30px;
  }

  .doc-card {
    background: white;
    border-radius: 8px;
    padding: 28px;
    box-shadow: 0 2px 8px rgba(16, 142, 254, 0.1);
    transition: all 0.3s ease;
    border: 1px solid #e8f0f9;
    display: flex;
    flex-direction: column;
    cursor: pointer;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 16px rgba(16, 142, 254, 0.15);
      border-color: #108efe;
    }

    .doc-header {
      display: flex;
      align-items: center; // ✅ 垂直居中
      gap: 16px;
      margin-bottom: 16px;

      .doc-icon {
        width: 50px;
        height: 50px;
        border-radius: 8px;
        background: linear-gradient(135deg, rgba(16, 142, 254, 0.1), rgba(16, 142, 254, 0.05));
        display: flex;
        align-items: center;
        justify-content: center;
        color: #108efe;
        flex-shrink: 0;
      }

      .doc-info {
        flex: 1;
        min-width: 0;
        overflow: hidden;

        .doc-title {
          font-size: 16px;
          font-weight: 700;
          color: #333;
          margin: 0 0 4px 0; // 可选：减少下边距
          line-height: 1.3;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .doc-subtitle {
          font-size: 11px;
          font-weight: 500;
          color: #108efe;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
      }
    }

    .doc-description {
      font-size: 13px;
      color: #666;
      line-height: 1.6;
      margin-bottom: 16px;
      flex: 1;
    }

    .doc-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 16px;
      border-top: 1px solid #f0f0f0;

      .footer-left {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        color: #999;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .read-time {
        font-size: 12px;
        color: #999;
      }

      .date {
        font-size: 12px;
        color: #999;
        flex-shrink: 0;
      }
    }
  }
}

// 教程详情部分 - 全屏无边距
.tutorial-detail-section {
  position: relative;
  width: 100%;
  height: 100%;
  background: white;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: 0;
  box-shadow: none;

  // 简约标签 + 静默模式蓝色提示
  .tutorial-label {
    position: absolute;
    left: -20px;
    top: 25%;
    transform: translateY(-50%);
    z-index: 25;
    transition: all 0.3s ease;
    cursor: grab;
    user-select: none;
    padding: 8px 4px;
    background: white;
    border: 1px solid #d0e0f0;
    border-left: none;
    border-radius: 0 6px 6px 0;
    box-shadow: -2px 2px 8px rgba(16, 142, 254, 0.12);

    &.label-dragging {
      cursor: grabbing;
      z-index: 30;
      box-shadow: -2px 2px 12px rgba(16, 142, 254, 0.2);
    }

    &:not(.label-visible):not(.label-pinned) {
      left: -32px;
      opacity: 0.5;

      &:hover {
        opacity: 1;
        left: -20px;
        box-shadow: -2px 2px 12px rgba(16, 142, 254, 0.2);
      }

      // 静默模式蓝色箭头提示
      &::before {
        content: "▶";
        position: absolute;
        right: -20px;
        top: 50%;
        transform: translateY(-50%);
        color: #108efe;
        font-size: 12px;
        font-weight: bold;
        opacity: 0.7;
        animation: pulse-blue 1.5s ease-in-out infinite;
      }
    }

    &.label-visible,
    &.label-pinned {
      opacity: 1;
      left: 0;
      box-shadow: 2px 2px 8px rgba(16, 142, 254, 0.15);
    }

    .label-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2px;
      min-height: 60px;
      justify-content: center;

      .label-text {
        writing-mode: vertical-rl;
        text-orientation: mixed;
        font-size: 11px;
        font-weight: 700;
        color: #108efe;
        letter-spacing: 1px;
        text-align: center;
        max-width: 20px;
        word-break: break-all;
        line-height: 1.2;
      }

      .label-hint {
        color: #a0a0a0;
        font-size: 8px;
        animation: hintBlink 1.5s ease-in-out infinite;
        margin-top: 2px;
      }
    }

    &:hover .label-content {
      color: #0066cc;
    }
  }

  // 主内容容器
  .tutorial-content {
    display: flex;
    flex: 1;
    gap: 0;
    overflow: hidden;
    user-select: none;

    .tutorial-left {
      display: flex;
      flex-direction: column;
      overflow: hidden;
      position: relative;
      background: white;
      border-right: 1px solid #e8f0f9;

      // 滚动区域
      .markdown-wrapper {
        flex: 1;
        overflow-y: auto;
        padding: 30px;

        &::-webkit-scrollbar {
          width: 6px;
        }

        &::-webkit-scrollbar-track {
          background: transparent;
        }

        &::-webkit-scrollbar-thumb {
          background: #d0e0f0;
          border-radius: 3px;

          &:hover {
            background: #a0c0f0;
          }
        }
      }

      .loading-state,
      .empty-state {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 200px;
        color: #999;
      }

      .markdown-content {
        font-size: 14px;
        line-height: 1.8;
        color: #333;

        :deep(h1), :deep(h2), :deep(h3) {
          margin-top: 20px;
          margin-bottom: 12px;
          font-weight: 700;
          color: #1a1a1a;
        }

        :deep(h1) {
          font-size: 24px;
          border-bottom: 2px solid #108efe;
          padding-bottom: 10px;
        }

        :deep(h2) {
          font-size: 20px;
          color: #108efe;
        }

        :deep(h3) {
          font-size: 16px;
          color: #333;
        }

        :deep(p) {
          margin-bottom: 10px;
          text-align: justify;
        }

        :deep(strong) {
          color: #108efe;
          font-weight: 700;
        }

        :deep(em) {
          font-style: italic;
          color: #666;
        }

        :deep(ul), :deep(ol) {
          margin: 15px 0;
          padding-left: 20px;

          li {
            margin-bottom: 8px;
          }
        }

        :deep(ul li) {
          list-style-type: disc;
        }

        :deep(ol li) {
          list-style-type: decimal;
        }

        :deep(pre) {
          background: #f5f8fc;
          border-left: 3px solid #108efe;
          padding: 15px;
          border-radius: 4px;
          overflow-x: auto;
          margin: 15px 0;

          code {
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            color: #333;
          }
        }

        :deep(code) {
          background: #f0f7ff;
          color: #108efe;
          padding: 2px 6px;
          border-radius: 3px;
          font-family: 'Monaco', 'Courier New', monospace;
          font-size: 13px;
        }

        :deep(a) {
          color: #108efe;
          text-decoration: none;
          border-bottom: 1px solid #108efe;
          transition: all 0.2s ease;

          &:hover {
            background: #f0f7ff;
            padding: 0 2px;
          }
        }

        :deep(blockquote) {
          border-left: 4px solid #108efe;
          padding-left: 16px;
          margin: 16px 0;
          color: #666;
          font-style: italic;
        }

        :deep(table) {
          border-collapse: collapse;
          width: 100%;
          margin: 16px 0;

          th, td {
            border: 1px solid #e0e0e0;
            padding: 8px 12px;
            text-align: left;
          }

          th {
            background: #f5f8fc;
            font-weight: 600;
          }
        }

        :deep(hr) {
          border: none;
          border-top: 1px solid #e8f0f9;
          margin: 20px 0;
        }
      }

      // 常驻底部控制栏
      .bottom-control-bar {
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        padding: 12px 16px;
        background: white;
        border-top: 1px solid #e8f0f9;
        z-index: 10;

        .control-btn {
          width: 32px;
          height: 32px;
          border-radius: 4px;
          background: transparent;
          border: 1px solid #d0e0f0;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease;
          color: #666;

          &:hover:not(:disabled) {
            border-color: #108efe;
            color: #108efe;
            background: rgba(16, 142, 254, 0.05);
          }

          &:disabled {
            opacity: 0.4;
            cursor: not-allowed;
          }
        }
      }
    }

    // 分割线 + 纯三角形指示器（无圆形背景）
    .divider {
      width: 1px;
      background: #e8f0f9;
      cursor: col-resize;
      transition: all 0.2s ease;
      position: relative;

      // 热区：扩大可点击区域
      &::after {
        content: '';
        position: absolute;
        left: 50%;
        top: 0;
        transform: translateX(-50%);
        width: 10px;
        height: 100%;
        background: transparent;
        cursor: col-resize;
        pointer-events: auto;
      }

      .drag-handle {
        position: absolute;
        left: 100%;          // 三角形左侧与分割线右侧对齐
        top: 50%;
        transform: translateY(-50%);  // 垂直居中，不水平移动
        margin-left: -2px;    // 可选，让三角形稍远离分割线，视觉更清晰
        font-size: 14px;
        color: #e8f0f9;
        pointer-events: auto;
        cursor: col-resize;
        font-weight: bold;
        transition: color 0.2s ease;
        z-index: 5;
        background: transparent;
        text-shadow: 0 0 2px rgba(255,255,255,0.5);
      }

      &:hover {
        width: 2px;
        background: #108efe;
        box-shadow: 0 0 4px rgba(16, 142, 254, 0.3);

        .drag-handle {
          color: #108efe; // hover 时与分割线颜色一致
        }
      }

      &.divider-active {
        width: 2px;
        background: #108efe;
        box-shadow: 0 0 4px rgba(16, 142, 254, 0.3);

        .drag-handle {
          color: #108efe;
        }
      }
    }

    // 右侧图表区域
    .tutorial-right {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: #f8fbfe;
      position: relative;
      overflow: hidden;

      .graph-placeholder {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
        text-align: center;

        p {
          font-size: 14px;
          color: #999;
          margin: 0;
        }
      }
    }
  }
}

@keyframes hintBlink {
  0%, 100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
}

@keyframes pulse-blue {
  0%, 100% {
    opacity: 0.5;
    transform: translateY(-50%) translateX(0);
  }
  50% {
    opacity: 1;
    transform: translateY(-50%) translateX(2px);
  }
}
</style>
