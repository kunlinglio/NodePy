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
  mdiHome,
} from '@mdi/js'
import { usePageStore } from '@/stores/pageStore'

const pageStore = usePageStore()

// 当前打开的教程ID
const currentDocId = ref<number | null>(null)
const hoverDoc = ref<number | null>(null)

// 布局相关
const splitRatio = ref(35) // 左侧比例，默认35%（3.5-6.5开）
const isDragging = ref(false)
const tutorialContentRef = ref<HTMLElement | null>(null)

// 标签相关
const labelPosition = ref(25) // 标签显示位置，百分比（相对于左侧页面）
const isLabelDragging = ref(false)
const labelShowTime = ref<NodeJS.Timeout | null>(null)
const labelHideTime = ref<NodeJS.Timeout | null>(null)
const isLabelVisible = ref(false) // 标签是否显示
const isLabelPinned = ref(false) // 标签是否常驻
const labelLastInteractTime = ref(0) // 标签最后交互时间
const tutorialLeftRef = ref<HTMLElement | null>(null) // 左侧页面ref

// 控制栏相关
const isControlBarIdle = ref(false) // 控制栏是否静默
const controlBarIdleTime = ref<NodeJS.Timeout | null>(null)
const isControlBarHovered = ref(false)

// 教程内容
const tutorialMarkdown = ref('') // 来自后端的 markdown 内容
const tutorialHtml = computed(() => {
  // 简单的 markdown 转 HTML（实际应该使用 markdown-it 库）
  return convertMarkdownToHtml(tutorialMarkdown.value)
})

// markdown 到 HTML 的简单转换函数
const convertMarkdownToHtml = (markdown: string): string => {
  if (!markdown) return ''
  
  let html = markdown
    // 代码块
    .replace(/```(.*?)\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>')
    // 标题
    .replace(/^### (.*?)$/gm, '<h3>$1</h3>')
    .replace(/^## (.*?)$/gm, '<h2>$1</h2>')
    .replace(/^# (.*?)$/gm, '<h1>$1</h1>')
    // 加粗
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // 斜体
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // 列表
    .replace(/^\* (.*?)$/gm, '<li>$1</li>')
    .replace(/(<li>.*?<\/li>)/s, '<ul>$1</ul>')
    // 段落
    .replace(/\n\n/g, '</p><p>')
    .replace(/^(?!<[hu]|<pre|<ul|<p)/gm, '<p>')
    .replace(/$/gm, '</p>')
    // 链接
    .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')
    // 换行符
    .replace(/\n/g, '<br>')
  
  return html
}

// 开始拖拽
const startDragging = () => {
  isDragging.value = true
}

// 结束拖拽
const stopDragging = () => {
  isDragging.value = false
}

// 处理分割线拖动（分割线）
const handleMouseMove = (e: MouseEvent) => {
  if (!isDragging.value || !tutorialContentRef.value) return
  
  const container = tutorialContentRef.value
  const rect = container.getBoundingClientRect()
  const newRatio = ((e.clientX - rect.left) / rect.width) * 100
  
  // 限制比例 2:8 到 5:5（即 20%-50%）
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
  
  // 限制范围 10%-75%
  if (newPosition >= 10 && newPosition <= 75) {
    labelPosition.value = newPosition
  }
}

// 开始拖动标签
const startLabelDragging = () => {
  isLabelDragging.value = true
}

// 停止拖动标签
const stopLabelDragging = () => {
  isLabelDragging.value = false
}

// 显示标签
const showLabel = () => {
  isLabelVisible.value = true
  labelLastInteractTime.value = Date.now()
  
  // 清除之前的隐藏计时器
  if (labelHideTime.value) clearTimeout(labelHideTime.value)
  
  // 如果不是常驻状态，3秒后隐藏
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

// 处理控制栏悬浮
const handleControlBarHover = () => {
  isControlBarHovered.value = true
  isControlBarIdle.value = false
  if (controlBarIdleTime.value) clearTimeout(controlBarIdleTime.value)
}

// 处理控制栏离开
const handleControlBarLeave = () => {
  isControlBarHovered.value = false
  // 3秒后进入静默状态
  controlBarIdleTime.value = setTimeout(() => {
    if (!isControlBarHovered.value) {
      isControlBarIdle.value = true
    }
  }, 3000)
}

// 监听鼠标抬起
const handleMouseUp = () => {
  stopDragging()
}

onMounted(() => {
  window.addEventListener('mousemove', handleMouseMove)
  window.addEventListener('mousemove', handleLabelMouseMove)
  window.addEventListener('mouseup', handleMouseUp)
  window.addEventListener('mouseup', stopLabelDragging)
})

// 处理教程切换时更新内容
watch(currentDocId, async (newId) => {
  if (newId) {
    // 重置控制栏状态
    isControlBarIdle.value = false
    isControlBarHovered.value = false
    if (controlBarIdleTime.value) clearTimeout(controlBarIdleTime.value)
    
    // 显示标签3秒
    showLabel()
    
    // 这里应该从后端 API 获取教程的 markdown 内容
    // 示例：const response = await fetch(`/api/tutorials/${newId}`)
    // const data = await response.json()
    // tutorialMarkdown.value = data.content
    tutorialMarkdown.value = `# ${currentDoc.value?.title}

## 简介
这是第 ${newId} 个教程的内容示例。实际内容会从后端 API 获取。

## 主要功能
- 支持 Markdown 格式
- 自动渲染为 HTML
- 支持代码高亮

\`\`\`python
def hello():
    print("Hello, World!")
\`\`\`

## 使用步骤
1. 选择一个教程
2. 查看左侧的说明文档
3. 在右侧使用图表工具

**更多内容即将推出...**

---

这是额外的内容用来测试滚动功能。

### 小标题1
这是一些文本内容。

### 小标题2
更多的文本内容。`
  }
})

// 教程数据
const docs = ref([
  {
    id: 1,
    title: '用户指南',
    description: '完整的 NodePy 使用指南，涵盖从入门到精通的全套教程。',
    icon: mdiBookOpenPageVariant,
    category: 'guide',
    pages: 45,
    updated: '2024-02-28'
  },
  {
    id: 2,
    title: '节点参考',
    description: '所有节点的详细说明，包括参数配置、输入输出类型和使用示例。',
    icon: mdiCloudDownloadOutline,
    category: 'reference',
    pages: 120,
    updated: '2024-02-25'
  },
  {
    id: 3,
    title: '常见问题',
    description: '常见问题解答，快速解决您在使用过程中遇到的问题。',
    icon: mdiLightbulb,
    category: 'faq',
    pages: 28,
    updated: '2024-02-20'
  },
  {
    id: 4,
    title: 'API 文档',
    description: '开发者 API 文档，用于集成和扩展 NodePy 功能。',
    icon: mdiCheckCircleOutline,
    category: 'api',
    pages: 87,
    updated: '2024-02-15'
  }
])

// 计算当前教程对象
const currentDoc = computed(() => {
  return docs.value.find(doc => doc.id === currentDocId.value)
})

// 计算是否可以查看上一个教程
const hasPrevious = computed(() => {
  if (!currentDoc.value) return false
  return currentDoc.value.id > 1
})

// 计算是否可以查看下一个教程
const hasNext = computed(() => {
  if (!currentDoc.value) return false
  return currentDoc.value.id < docs.value.length
})

// 打开教程
const openDoc = (doc: any) => {
  currentDocId.value = doc.id
}

// 回到教程主页
const backToList = () => {
  currentDocId.value = null
}

// 上一个教程
const previousDoc = () => {
  if (currentDoc.value && currentDoc.value.id > 1) {
    currentDocId.value = currentDoc.value.id - 1
  }
}

// 下一个教程
const nextDoc = () => {
  if (currentDoc.value && currentDoc.value.id < docs.value.length) {
    currentDocId.value = currentDoc.value.id + 1
  }
}

// pageStore.setCurrentPage('Explore')
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
              @mouseenter="hoverDoc = doc.id"
              @mouseleave="hoverDoc = null"
              :class="{ 'doc-card-hover': hoverDoc === doc.id }"
            >
              <div class="doc-header">
                <div class="doc-icon" :class="{ 'doc-icon-hover': hoverDoc === doc.id }">
                  <svg-icon :path="doc.icon" :size="28" type="mdi"></svg-icon>
                </div>
                <div class="doc-meta">
                  <span class="doc-category" :class="{ 'doc-category-hover': hoverDoc === doc.id }">{{ doc.category.toUpperCase() }}</span>
                  <span class="doc-pages">{{ doc.pages }} 页</span>
                </div>
              </div>
              <h3 class="doc-title" :class="{ 'doc-title-hover': hoverDoc === doc.id }">{{ doc.title }}</h3>
              <p class="doc-description">{{ doc.description }}</p>
              <div class="doc-footer">
                <span class="updated">更新于 {{ doc.updated }}</span>
                <button class="read-btn" :class="{ 'read-btn-hover': hoverDoc === doc.id }" @click="openDoc(doc)">立即阅读</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 教程详情视图 -->
        <div v-else class="tutorial-detail-section">
          <!-- 简约标签 -->
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
            <!-- 左侧：文档说明 -->
            <div class="tutorial-left" ref="tutorialLeftRef" :style="{ width: splitRatio + '%' }">
              <div class="markdown-content" v-html="tutorialHtml"></div>
            </div>

            <!-- 分割线 -->
            <div 
              class="divider" 
              @mousedown="startDragging"
              :class="{ 'divider-active': isDragging }"
            ></div>

            <!-- 右侧：图表组件区域 -->
            <div class="tutorial-right" :style="{ width: (100 - splitRatio) + '%' }">
              <div class="graph-placeholder">
                <p>图表组件区域（待接入定制的 Graph 组件）</p>
              </div>
            </div>
          </div>

          <!-- 浮动控制按钮栏 -->
          <div 
            class="floating-control-bar"
            @mouseenter="handleControlBarHover"
            @mouseleave="handleControlBarLeave"
            :class="{ 'control-bar-idle': isControlBarIdle, 'control-bar-hovered': isControlBarHovered }"
            style="left: auto; right: 20px;"
          >
            <button class="nav-btn prev-btn" :disabled="!hasPrevious" @click="previousDoc" title="上一个教程">
              <svg-icon :path="mdiChevronLeft" :size="16" type="mdi"></svg-icon>
              <span class="btn-text">上一个</span>
            </button>
            <button class="nav-btn home-btn" @click="backToList" title="回到教程列表">
              <svg-icon :path="mdiHome" :size="16" type="mdi"></svg-icon>
              <span class="btn-text">主页</span>
            </button>
            <button class="nav-btn next-btn" :disabled="!hasNext" @click="nextDoc" title="下一个教程">
              <span class="btn-text">下一个</span>
              <svg-icon :path="mdiChevronRight" :size="16" type="mdi"></svg-icon>
            </button>
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

// 视频教程部分
.video-section {
  min-height: auto;

  .videos-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 30px;
  }

  .video-card {
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(16, 142, 254, 0.1);
    transition: all 0.3s ease;
    border: 1px solid #e8f0f9;
    display: flex;
    flex-direction: column;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 16px rgba(16, 142, 254, 0.15);
      border-color: #108efe;

      .video-overlay {
        opacity: 1;
      }

      .play-btn {
        transform: scale(1.1);
      }
    }

    .video-thumbnail {
      position: relative;
      width: 100%;
      height: 180px;
      background: linear-gradient(135deg, rgba(16, 142, 254, 0.1), rgba(16, 142, 254, 0.05));
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;

      .emoji {
        font-size: 64px;
        opacity: 0.5;
      }

      .video-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: all 0.3s ease;
      }

      .play-btn {
        width: 60px;
        height: 60px;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        color: #108efe;
      }

      .video-duration {
        position: absolute;
        bottom: 12px;
        right: 12px;
        background: rgba(0, 0, 0, 0.7);
        color: white;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
      }

      .difficulty-badge {
        position: absolute;
        top: 12px;
        right: 12px;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
      }
    }

    .video-info {
      padding: 20px;
      flex: 1;
      display: flex;
      flex-direction: column;

      .video-title {
        font-size: 16px;
        font-weight: 700;
        color: #333;
        margin-bottom: 8px;
        line-height: 1.4;
      }

      .video-description {
        font-size: 13px;
        color: #666;
        line-height: 1.5;
        margin-bottom: 12px;
        flex: 1;
      }

      .video-meta {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 12px;
        color: #999;

        .views {
          display: flex;
          align-items: center;
          gap: 4px;
        }
      }
    }
  }
}

// 文档教程部分
.doc-section {
  background: transparent;
  min-height: auto;

  .docs-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
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

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 16px rgba(16, 142, 254, 0.15);
      border-color: #108efe;
    }

    .doc-header {
      display: flex;
      align-items: flex-start;
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

      .doc-meta {
        display: flex;
        flex-direction: column;
        gap: 4px;
        flex: 1;

        .doc-category {
          font-size: 11px;
          font-weight: 700;
          color: #108efe;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .doc-pages {
          font-size: 12px;
          color: #999;
        }
      }
    }

    .doc-title {
      font-size: 18px;
      font-weight: 700;
      color: #333;
      margin-bottom: 10px;
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

      .updated {
        font-size: 12px;
        color: #999;
      }

      .read-btn {
        background: none;
        border: none;
        color: #108efe;
        font-weight: 600;
        cursor: pointer;
        font-size: 13px;
        padding: 0;
        transition: all 0.2s ease;

        &:hover {
          transform: translateX(4px);
        }
      }
    }
  }
}

// 教程详情部分
.tutorial-detail-section {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  width: 90%;
  height: 85vh;
  padding: 0;
  background: white;
  overflow: hidden;
  margin: 0;
  max-width: none;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(16, 142, 254, 0.12);
  z-index: 10;

  // 简约标签 - 真正的标签风格
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
      overflow-y: auto;
      overflow-x: hidden;
      position: relative;
      background: white;
      padding: 30px;
      border-right: 1px solid #e8f0f9;
      
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

      .markdown-content {
        font-size: 14px;
        line-height: 1.8;
        color: #333;

        h1, h2, h3 {
          margin-top: 20px;
          margin-bottom: 12px;
          font-weight: 700;
          color: #1a1a1a;
        }

        h1 {
          font-size: 24px;
          border-bottom: 2px solid #108efe;
          padding-bottom: 10px;
        }

        h2 {
          font-size: 20px;
          color: #108efe;
        }

        h3 {
          font-size: 16px;
          color: #333;
        }

        p {
          margin-bottom: 10px;
          text-align: justify;
        }

        strong {
          color: #108efe;
          font-weight: 700;
        }

        em {
          font-style: italic;
          color: #666;
        }

        ul {
          margin: 15px 0;
          padding-left: 20px;

          li {
            margin-bottom: 8px;
            list-style-type: disc;
          }
        }

        pre {
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

        code {
          background: #f0f7ff;
          color: #108efe;
          padding: 2px 6px;
          border-radius: 3px;
          font-family: 'Monaco', 'Courier New', monospace;
          font-size: 13px;
        }

        a {
          color: #108efe;
          text-decoration: none;
          border-bottom: 1px solid #108efe;
          transition: all 0.2s ease;

          &:hover {
            background: #f0f7ff;
            padding: 0 2px;
          }
        }

        br {
          display: block;
          content: '';
        }
      }
    }

    // 分割线
    .divider {
      width: 1px;
      background: #e8f0f9;
      cursor: col-resize;
      transition: all 0.2s ease;
      position: relative;

      &:hover {
        width: 2px;
        background: #108efe;
        box-shadow: 0 0 4px rgba(16, 142, 254, 0.3);
      }

      &.divider-active {
        width: 2px;
        background: #108efe;
        box-shadow: 0 0 4px rgba(16, 142, 254, 0.3);
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

  // 浮动控制栏
  .floating-control-bar {
    position: absolute;
    left: 20px;
    bottom: 20px;
    display: flex;
    gap: 8px;
    padding: 8px 10px;
    background: white;
    border-radius: 6px;
    border: 1px solid #d0e0f0;
    box-shadow: 0 2px 8px rgba(16, 142, 254, 0.12);
    z-index: 20;
    transition: all 0.3s ease;
    opacity: 1;
    backdrop-filter: blur(10px);

    &.control-bar-idle {
      opacity: 0.2;
    }

    &.control-bar-hovered {
      opacity: 1;
      box-shadow: 0 4px 12px rgba(16, 142, 254, 0.15);
      border-color: #108efe;
    }

    .nav-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
      background: #108efe;
      border: none;
      border-radius: 4px;
      padding: 6px 10px;
      color: white;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      font-size: 12px;
      white-space: nowrap;

      .btn-text {
        display: none;
      }

      @media (min-width: 1200px) {
        .btn-text {
          display: inline;
        }
      }

      &:hover:not(:disabled) {
        background: #0056d4;
        transform: translateY(-1px);
        box-shadow: 0 2px 6px rgba(16, 142, 254, 0.3);
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }

      svg {
        width: 14px;
        height: 14px;
      }
    }

    .prev-btn {
      flex-direction: row-reverse;
    }

    .home-btn {
      background: #6c757d;

      &:hover:not(:disabled) {
        background: #5a6268;
      }
    }

    .next-btn {
      flex-direction: row;
    }
  }
}

// 标签提示闪烁动画
@keyframes hintBlink {
  0%, 100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
}

// 动画
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

// 关于我们部分
.about-section {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;

  .about-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 80px;
    background: white;
    border-radius: 8px;
    padding: 60px;
    box-shadow: 0 4px 16px rgba(16, 142, 254, 0.1);
    border: 1px solid #e8f0f9;

    @media (max-width: 992px) {
      flex-direction: column;
      gap: 40px;
      padding: 40px;
    }

    .about-content {
      flex: 1;

      .about-title {
        font-size: 32px;
        font-weight: 900;
        color: #333;
        margin-bottom: 24px;
      }

      .about-text {
        font-size: 16px;
        line-height: 1.8;
        color: #666;
        margin-bottom: 20px;
      }

      .about-features {
        display: flex;
        gap: 40px;
        margin-top: 40px;

        @media (max-width: 992px) {
          flex-wrap: wrap;
          gap: 30px;
        }

        .about-feature-item {
          text-align: center;
          flex: 1;
          min-width: 120px;

          .feature-number {
            font-size: 32px;
            font-weight: 900;
            color: #108efe;
            margin-bottom: 8px;
          }

          p {
            font-size: 14px;
            color: #666;
            font-weight: 600;
          }
        }
      }
    }

    .about-illustration {
      flex: 1;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 40px;
      flex-wrap: wrap;

      .illustration-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 16px;
        text-align: center;

        .illus-emoji {
          font-size: 64px;
          filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
        }

        p {
          font-size: 14px;
          font-weight: 700;
          color: #333;
        }
      }
    }
  }
}
</style>