<script lang='ts' setup>
import { ref, computed, onMounted, watch } from 'vue'
//@ts-ignore
import SvgIcon from '@jamescoyle/vue-icon'
import {
  mdiBookOpenPageVariant,
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
import Graph from '@/components/Graph/Graph.vue'
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
    pages: 9,
    playgroundProjectId: 1029
  },
  {
    id: 2,
    title: '核心概念',
    description: '节点图的工作方式：节点、端口、连线、数据流与类型系统。',
    icon: mdiBrain,
    category: 'Concepts',
    pages: 5,
    playgroundProjectId: 1031
  },
  {
    id: 3,
    title: '常见数据流程',
    description: '涵盖数据采集、清洗、分析与可视化全流程，并包含K线数据实战。',
    icon: mdiChartTimeline,
    category: 'Workflow',
    pages: 7,
    playgroundProjectId: 1028
  },
  {
    id: 4,
    title: '逻辑控制与自动化',
    description: '使用循环、条件判断和自定义脚本构建智能流程。',
    icon: mdiPlaylistCheck,
    category: 'Automation',
    pages: 8,
    playgroundProjectId: 1032
  },
  {
    id: 5,
    title: '机器学习实战',
    description: '从特征工程到模型训练、预测与评估，全程节点搭建机器学习流程。',
    icon: mdiRobot,
    category: 'Machine Learning',
    pages: 8,
    playgroundProjectId: 1030
  }
])

// 辅助函数：根据章节数生成阅读时间信息（pages 已包含概述+总结，因此减去2计算有效章节）
const getDocInfo = (pages: number) => {
  if (pages === 0) return '加载中...'
  const minutesPerSection = 2
  const effectiveSections = Math.max(0, pages)
  const totalMinutes = effectiveSections * minutesPerSection
  if (totalMinutes < 60) {
    return `共 ${effectiveSections} 小节，阅读约需 ${totalMinutes} 分钟`
  } else {
    const hours = Math.floor(totalMinutes / 60)
    const mins = totalMinutes % 60
    return `共 ${effectiveSections} 小节，阅读约需 ${hours} 小时 ${mins} 分钟`
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
const splitRatio = ref(50) // 初始 50%，范围 40% ~ 60%
const isDragging = ref(false)
const tutorialContentRef = ref<HTMLElement | null>(null)

// 当前显示的 HTML 内容
const currentHtml = computed(() => {
  if (tutorialSections.value.length > 0 && currentSectionIndex.value < tutorialSections.value.length) {
    return tutorialSections.value[currentSectionIndex.value]!.html
  }
  return ''
})

// 当前章节标题
const currentSectionTitle = computed(() => {
  if (tutorialSections.value.length > 0 && currentSectionIndex.value < tutorialSections.value.length) {
    const title = tutorialSections.value[currentSectionIndex.value]!.title
    // 确保标题不为空，如果为空则返回默认值
    return title && title.trim() ? title.trim() : '小节'
  }
  return ''
})

const currentPlaygroundProjectId = computed(() => {
  const doc = docs.value.find(d => d.id === currentDocId.value)
  return doc ? doc.playgroundProjectId : null
})

// 总章节数
const totalSections = computed(() => tutorialSections.value.length)

// 章节进度显示文本
const chapterProgressText = computed(() => {
  if (totalSections.value > 0) {
    return `第 ${currentSectionIndex.value + 1} / ${totalSections.value} 节`
  }
  return ''
})

// 获取当前文档标题
const currentDocTitle = computed(() => {
  return currentDoc.value?.title || ''
})

// 顶部栏显示：大标题 + 小节标题 (进度)
const headerTitle = computed(() => {
  if (!currentDoc.value) return ''
  const docTitle = currentDoc.value.title
  const sectionTitle = currentSectionTitle.value
  const progress = chapterProgressText.value ? ` (${chapterProgressText.value})` : ''
  return `${docTitle} - ${sectionTitle}${progress}`
})

// 分页导航可用性
const hasPrevSection = computed(() => {
  return currentSectionIndex.value > 0
})

const hasNextSection = computed(() => {
  return currentSectionIndex.value < totalSections.value - 1
})

// 将 Markdown 按二级标题拆分为章节，首节为“概述”，末节自动处理总结，内容原样保留
const splitIntoSections = (markdown: string) => {
  const lines = markdown.split('\n')
  const sections: Array<{ title: string; content: string; html: string }> = []
  let currentTitle = '概述'
  let currentContent: string[] = []
  let inCodeBlock = false

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]!

    if (line.trim().startsWith('```')) {
      inCodeBlock = !inCodeBlock
      currentContent.push(line)
      continue
    }

    if (!inCodeBlock) {
      const h2Match = line.match(/^## (.*)$/)
      if (h2Match) {
        // 遇到二级标题，结束当前节，开始新节
        if (currentContent.length > 0) {
          sections.push({
            title: currentTitle,
            content: currentContent.join('\n'),
            html: md.render(currentContent.join('\n'))
          })
        }
        currentTitle = h2Match[1]!.trim()
        currentContent = [line]  // 保留标题行
        continue
      }
    }

    currentContent.push(line)
  }

  // 处理最后一个节
  if (currentContent.length > 0) {
    sections.push({
      title: currentTitle,
      content: currentContent.join('\n'),
      html: md.render(currentContent.join('\n'))
    })
  }

  // 如果没有任何节（比如空文档），添加一个默认节
  if (sections.length === 0 && markdown.trim()) {
    sections.push({
      title: '概述',
      content: markdown,
      html: md.render(markdown)
    })
  }

  return sections
}

// 加载教程内容
const loadTutorial = async (docId: number) => {
  isLoading.value = true
  try {
    const fileIndex = docId - 1
    if (fileIndex >= 0 && fileIndex < tutorialFiles.length) {
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

// 开始拖拽分割线
const startDragging = (e: MouseEvent) => {
  e.preventDefault()
  isDragging.value = true
}

const stopDragging = () => {
  isDragging.value = false
}

// 处理分割线拖动 (范围 40% ~ 60%)
const handleMouseMove = (e: MouseEvent) => {
  if (!isDragging.value || !tutorialContentRef.value) return

  const container = tutorialContentRef.value
  const rect = container.getBoundingClientRect()
  let newRatio = ((e.clientX - rect.left) / rect.width) * 100
  newRatio = Math.min(60, Math.max(40, newRatio))
  splitRatio.value = newRatio
}

onMounted(() => {
  window.addEventListener('mousemove', handleMouseMove)
  window.addEventListener('mouseup', stopDragging)
})

// 监听教程切换
watch(currentDocId, async (newId) => {
  if (newId) {
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

// 前后教程标题（用于鼠标悬浮提示）
const prevDocTitle = computed(() => {
  if (!hasPrevious.value) return ''
  const prevId = currentDoc.value!.id - 1
  const prevDoc = docs.value.find(d => d.id === prevId)
  return prevDoc ? prevDoc.title : ''
})

const nextDocTitle = computed(() => {
  if (!hasNext.value) return ''
  const nextId = currentDoc.value!.id + 1
  const nextDoc = docs.value.find(d => d.id === nextId)
  return nextDoc ? nextDoc.title : ''
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

// 章节导航（简化为直接加减索引）
const prevSection = () => {
  if (hasPrevSection.value) {
    currentSectionIndex.value--
    // 滚动到顶部
    const wrapper = document.querySelector('.markdown-wrapper') as HTMLElement
    if (wrapper) wrapper.scrollTop = 0
  }
}

const nextSection = () => {
  if (hasNextSection.value) {
    currentSectionIndex.value++
    // 滚动到顶部
    const wrapper = document.querySelector('.markdown-wrapper') as HTMLElement
    if (wrapper) wrapper.scrollTop = 0
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
          <!-- 主内容容器 -->
          <div class="tutorial-content" ref="tutorialContentRef">
            <!-- 左侧：顶部章节栏 + 文档内容 + 底部控制栏 -->
            <div class="tutorial-left" :style="{ width: splitRatio + '%' }">
              <!-- 顶部章节栏（大标题与小标题区分样式） -->
              <div class="chapter-header">
                <div class="chapter-info">
                  <span class="doc-title-text">{{ currentDocTitle }}</span>
                  <span class="section-title-text">
                    {{ currentSectionTitle }}
                    <span v-if="chapterProgressText" class="section-progress">({{ chapterProgressText }})</span>
                  </span>
                </div>
              </div>

              <!-- 滚动区域 -->
              <div class="markdown-wrapper">
                <div class="loading-state" v-if="isLoading">
                  <p>加载教程内容中...</p>
                </div>
                <div class="markdown-content" v-else-if="currentHtml" v-html="currentHtml"></div>
                <div class="empty-state" v-else>
                  <p>暂无内容</p>
                </div>
              </div>

              <!-- 底部控制栏 -->
              <div class="bottom-control-bar">
                <button class="control-btn" :disabled="!hasPrevious" @click="previousDoc" :title="prevDocTitle">
                  <svg-icon :path="mdiChevronDoubleLeft" :size="18" type="mdi"></svg-icon>
                  <span>上篇</span>
                </button>
                <button class="control-btn" :disabled="!hasPrevSection" @click="prevSection" title="上一章节">
                  <svg-icon :path="mdiChevronLeft" :size="18" type="mdi"></svg-icon>
                  <span>上一节</span>
                </button>
                <button class="control-btn" :disabled="!hasNextSection" @click="nextSection" title="下一章节">
                  <span>下一节</span>
                  <svg-icon :path="mdiChevronRight" :size="18" type="mdi"></svg-icon>
                </button>
                <button class="control-btn" :disabled="!hasNext" @click="nextDoc" :title="nextDocTitle">
                  <span>下篇</span>
                  <svg-icon :path="mdiChevronDoubleRight" :size="18" type="mdi"></svg-icon>
                </button>
                <button class="control-btn" @click="backToList" title="回到教程列表">
                  <svg-icon :path="mdiHome" :size="18" type="mdi"></svg-icon>
                  <span>目录</span>
                </button>
              </div>
            </div>

            <!-- 分割线（仅手柄可拖拽，比例区间40%~60%） -->
            <div class="divider" :class="{ 'divider-active': isDragging }">
              <div class="drag-handle" @mousedown="startDragging">
                <div class="drag-grip"></div>
                <div class="drag-tooltip">拖动调整布局</div>
              </div>
            </div>

            <!-- 右侧：图表组件区域 -->
            <div class="tutorial-right" :style="{ width: (100 - splitRatio) + '%' }">
              <div class="graph-placeholder">
                <Graph
                  :isPlaygroundProject="true"
                  :playgroundProjectId="currentPlaygroundProjectId!"
                  :key="currentPlaygroundProjectId||-1"
                ></Graph>
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
      align-items: center;
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
          margin: 0 0 4px 0;
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
      border-right: 1px solid #eef2f8;

      // 顶部章节栏（大标题与小标题区分样式）
      .chapter-header {
        flex-shrink: 0;
        padding: 12px 24px;
        background: #fafbfc;
        border-bottom: 1px solid #eef2f8;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
        z-index: 5;

        .chapter-info {
          display: flex;
          align-items: baseline;
          gap: 12px;
          flex-wrap: wrap;

          .doc-title-text {
            font-size: 18px;
            font-weight: 700;
            color: #1f2937;
            letter-spacing: 0.2px;
          }

          .section-title-text {
            font-size: 14px;
            font-weight: 400;
            color: #6b7280;
            letter-spacing: 0.2px;

            .section-progress {
              font-size: 13px;
              color: #9ca3af;
              margin-left: 4px;
            }
          }
        }
      }

      // 滚动区域
      .markdown-wrapper {
        flex: 1;
        overflow-y: auto;
        padding: 12px 40px 32px 40px;

        &::-webkit-scrollbar {
          width: 8px;
        }

        &::-webkit-scrollbar-track {
          background: #f1f1f1;
          border-radius: 4px;
        }

        &::-webkit-scrollbar-thumb {
          background: #cbd5e1;
          border-radius: 4px;

          &:hover {
            background: #94a3b8;
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

      // 内容样式优化
      .markdown-content {
        font-size: 16px;
        line-height: 1.9;
        color: #2c3e50;

        :deep(h1), :deep(h2), :deep(h3) {
          margin-top: 1.8em;
          margin-bottom: 0.8em;
          font-weight: 700;
          color: #1e293b;
        }

        :deep(h1) {
          font-size: 28px;
          border-bottom: 2px solid #108efe;
          padding-bottom: 12px;
        }

        :deep(h2) {
          font-size: 24px;
          color: #1e293b;
        }

        :deep(h3) {
          font-size: 20px;
          color: #334155;
        }

        :deep(p) {
          margin-bottom: 1.2em;
          text-align: justify;
        }

        :deep(strong) {
          color: #2c3e50;
          font-weight: 700;
        }

        :deep(em) {
          font-style: italic;
          color: #5b6e8c;
        }

        :deep(ul), :deep(ol) {
          margin: 1.2em 0;
          padding-left: 1.8em;

          li {
            margin-bottom: 0.5em;
          }
        }

        :deep(pre) {
          background: #f8fafc;
          border-left: 4px solid #108efe;
          padding: 1.2em;
          border-radius: 8px;
          overflow-x: auto;
          margin: 1.2em 0;

          code {
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            color: #1e293b;
          }
        }

        :deep(code) {
          background: #f0f7ff;
          color: #2c3e50;
          padding: 0.2em 0.4em;
          border-radius: 4px;
          font-family: 'Monaco', 'Courier New', monospace;
          font-size: 0.9em;
        }

        :deep(a) {
          color: #2c3e50;
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
          padding-left: 1.2em;
          margin: 1.2em 0;
          color: #5b6e8c;
          font-style: italic;
        }

        :deep(table) {
          border-collapse: collapse;
          width: 100%;
          margin: 1.2em 0;

          th, td {
            border: 1px solid #e2e8f0;
            padding: 10px 12px;
            text-align: left;
          }

          th {
            background: #f8fafc;
            font-weight: 600;
          }
        }

        :deep(hr) {
          border: none;
          border-top: 1px solid #eef2f8;
          margin: 1.5em 0;
        }
      }

      // 底部控制栏
      .bottom-control-bar {
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        padding: 12px 24px;
        background: rgba(255, 255, 255, 0.96);
        backdrop-filter: blur(4px);
        border-top: 1px solid #eef2f8;
        z-index: 10;
        flex-wrap: nowrap;
        overflow-x: auto;

        .control-btn {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 8px 20px;
          border-radius: 40px;
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          cursor: pointer;
          font-size: 13px;
          font-weight: 500;
          color: #2c3e50;
          transition: all 0.2s ease;
          box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
          white-space: nowrap;
          flex-shrink: 0;

          &:hover:not(:disabled) {
            background: #108efe;
            border-color: #108efe;
            color: white;
            box-shadow: 0 2px 8px rgba(16, 142, 254, 0.25);
            transform: translateY(-1px);

            svg {
              color: white;
            }
          }

          &:active:not(:disabled) {
            transform: translateY(0);
          }

          &:disabled {
            opacity: 0.4;
            cursor: not-allowed;
            background: #f1f5f9;
          }

          svg {
            transition: color 0.2s;
          }
        }
      }
    }

    // 分割线
    .divider {
      width: 1px;
      background: #e2e8f0;
      transition: all 0.2s ease;
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;

      .drag-handle {
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        cursor: col-resize;
        z-index: 10;
        padding: 8px 4px;
        background: transparent;
        transition: all 0.2s;
        pointer-events: auto;

        .drag-grip {
          width: 4px;
          height: 32px;
          background: #cbd5e1;
          border-radius: 4px;
          transition: all 0.2s ease;
          box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        }

        .drag-tooltip {
          position: absolute;
          top: calc(100% + 12px);
          left: 50%;
          transform: translateX(-50%);
          background: rgba(0, 0, 0, 0.75);
          backdrop-filter: blur(4px);
          color: white;
          font-size: 11px;
          padding: 4px 10px;
          border-radius: 20px;
          white-space: nowrap;
          opacity: 0;
          transition: opacity 0.2s ease;
          pointer-events: none;
          font-weight: 500;
          letter-spacing: 0.3px;
        }

        &:hover .drag-grip {
          background: #108efe;
          width: 5px;
          height: 40px;
          box-shadow: 0 0 6px rgba(16, 142, 254, 0.5);
        }

        &:hover .drag-tooltip {
          opacity: 1;
        }
      }

      &:hover {
        background: #cbd5e1;
      }

      &.divider-active {
        background: #108efe;
        box-shadow: 0 0 8px rgba(16, 142, 254, 0.3);

        .drag-handle .drag-grip {
          background: #108efe;
          width: 5px;
          height: 40px;
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
        flex: 1;
        width: 100%;
        height: 100%;
      }
    }
  }
}
</style>
