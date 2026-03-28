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

      <!-- 教程详情视图 -->
      <div v-else class="tutorial-detail-section">
        <div class="tutorial-content" ref="tutorialContentRef">
          <!-- 左侧：文档内容区域 -->
          <div class="tutorial-left">
            <div class="chapter-header">
              <!-- 菜单按钮，带悬浮菜单 -->
              <button 
                ref="menuButtonRef"
                class="menu-button" 
                @click.stop="toggleMenu"
              >
                <svg-icon :path="mdiMenu" :size="20" type="mdi"></svg-icon>
              </button>
              <div class="chapter-info">
                <span class="doc-title-text">{{ currentDocTitle }}</span>
                <div class="section-info">
                  <span class="section-title">{{ currentSectionTitle }}</span>
                  <span v-if="chapterProgressText" class="section-progress">({{ chapterProgressText }})</span>
                </div>
              </div>
            </div>

            <div class="markdown-wrapper">
              <div class="loading-state" v-if="isLoading">
                <p>加载教程内容中...</p>
              </div>
              <div class="markdown-content" v-else-if="currentHtml" v-html="currentHtml"></div>
              <div class="empty-state" v-else>
                <p>暂无内容</p>
              </div>
            </div>

            <!-- 底部控制栏：纯文字点击切换，支持跨文档 -->
            <div class="bottom-control-bar-text">
              <div class="nav-text prev-text" :class="{ disabled: !hasPrevSection && !hasPreviousDoc }" @click="goPrevSection">
                <span class="nav-label">{{ prevButtonLabel }}</span>
                <span class="nav-section-title">{{ prevSectionDisplayText }}</span>
              </div>
              <div class="nav-text next-text" :class="{ disabled: !hasNextSection && !hasNextDoc }" @click="goNextSection">
                <span class="nav-label">{{ nextButtonLabel }}</span>
                <span class="nav-section-title">{{ nextSectionDisplayText }}</span>
              </div>
            </div>
          </div>

          <!-- 右侧：图表组件区域 -->
          <div class="tutorial-right">
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

    <!-- 顶部悬浮菜单（仿右键菜单风格） -->
    <Teleport to="body">
      <div
        v-if="menuVisible"
        ref="menuRootRef"
        class="floating-menu"
        :style="{
          position: 'fixed',
          left: menuPositionStyle.left,
          top: menuPositionStyle.top,
          zIndex: 9999,
          minWidth: '180px'
        }"
      >
        <ul class="menu-list">
          <li
            v-for="item in mainMenuItems"
            :key="item.id"
            class="menu-item"
            @mouseenter="onMenuItemMouseEnter(item.id, $event)"
            @mouseleave="onMenuItemMouseLeave"
          >
            <div class="menu-item-content">
              <span class="menu-label">{{ item.label }}</span>
              <span v-if="item.children.length" class="submenu-arrow">
                <svg width="10" height="10" viewBox="0 0 8 8">
                  <path d="M2 1 L6 4 L2 7" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </span>
            </div>
          </li>
        </ul>
      </div>

      <!-- 子菜单（悬浮时显示） -->
      <div
        v-if="menuHoverDocId !== null && currentSubmenuItems.length"
        @mouseenter="onSubMenuMouseEnter"
        @mouseleave="onSubMenuMouseLeave"
      >
        <SubMenu
          :items="currentSubmenuItems"
          :direction="submenuDirection"
          :on-select="handleSubMenuSelect"
          :anchor-rect="submenuAnchorRect"
        />
      </div>
    </Teleport>
  </div>
</template>

<script lang='ts' setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
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
  mdiMenu,
} from '@mdi/js'
import { usePageStore } from '@/stores/pageStore'
import Graph from '@/components/Graph/Graph.vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import SubMenu from '@/components/RightClickMenu/SubMenu.vue'

const router = useRouter()
const route = useRoute()
const pageStore = usePageStore()

const today = new Date().toISOString().slice(0, 10)

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

const tutorialFiles = [
  '1_quick_start.md',
  '2_core_concept.md',
  '3_common_data_flow.md',
  '4_logical_control_and_automation.md',
  '5_machine_learning.md'
]

const hoverDoc = ref<number | null>(null)
const docs = ref([
  {
    id: 1,
    title: '快速上手',
    description: '搭建并运行第一个节点项目，体验节点式编程的核心流程。',
    icon: mdiRocketLaunch,
    category: 'Quickstart',
    pages: 9,
    playgroundProjectId: 588
  },
  {
    id: 2,
    title: '核心概念',
    description: '节点图的工作方式：节点、端口、连线、数据流与类型系统。',
    icon: mdiBrain,
    category: 'Concepts',
    pages: 5,
    playgroundProjectId: 589
  },
  {
    id: 3,
    title: '常见数据流程',
    description: '涵盖数据采集、清洗、分析与可视化全流程，并包含K线数据实战。',
    icon: mdiChartTimeline,
    category: 'Workflow',
    pages: 7,
    playgroundProjectId: 590
  },
  {
    id: 4,
    title: '逻辑控制与自动化',
    description: '使用循环、条件判断和自定义脚本构建智能流程。',
    icon: mdiPlaylistCheck,
    category: 'Automation',
    pages: 8,
    playgroundProjectId: 591
  },
  {
    id: 5,
    title: '机器学习实战',
    description: '从特征工程到模型训练、预测与评估，全程节点搭建机器学习流程。',
    icon: mdiRobot,
    category: 'Machine Learning',
    pages: 8,
    playgroundProjectId: 11
  }
])

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

const tutorialsChaptersMeta = ref<Map<number, Array<{ title: string; index: number }>>>(new Map())
const cachedMarkdowns = ref<Map<number, string>>(new Map())
const isPreloading = ref(false)

const extractSectionTitles = (markdown: string): string[] => {
  const lines = markdown.split('\n')
  const titles: string[] = []
  let inCodeBlock = false
  for (const line of lines) {
    if (line.trim().startsWith('```')) {
      inCodeBlock = !inCodeBlock
      continue
    }
    if (!inCodeBlock) {
      const h2Match = line.match(/^## (.*)$/)
      if (h2Match) {
        titles.push(h2Match[1]!.trim())
      }
    }
  }
  if (titles.length === 0 && markdown.trim()) {
    titles.push('概述')
  }
  return titles
}

const preloadAllTutorials = async () => {
  if (isPreloading.value) return
  isPreloading.value = true
  try {
    const baseUrl = import.meta.env.BASE_URL
    const fetchPromises = tutorialFiles.map(async (file, idx) => {
      const docId = idx + 1
      const response = await fetch(`${baseUrl}guides/${file}`)
      if (!response.ok) throw new Error(`加载 ${file} 失败`)
      const markdown = await response.text()
      cachedMarkdowns.value.set(docId, markdown)
      const titles = extractSectionTitles(markdown)
      const sections = titles.map((title, index) => ({ title, index }))
      tutorialsChaptersMeta.value.set(docId, sections)
      const doc = docs.value.find(d => d.id === docId)
      if (doc) doc.pages = sections.length
    })
    await Promise.all(fetchPromises)
  } catch (error) {
    console.error('预加载教程失败:', error)
  } finally {
    isPreloading.value = false
  }
}

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
        if (currentContent.length > 0) {
          sections.push({
            title: currentTitle,
            content: currentContent.join('\n'),
            html: md.render(currentContent.join('\n'))
          })
        }
        currentTitle = h2Match[1]!.trim()
        currentContent = [line]
        continue
      }
    }

    currentContent.push(line)
  }

  if (currentContent.length > 0) {
    sections.push({
      title: currentTitle,
      content: currentContent.join('\n'),
      html: md.render(currentContent.join('\n'))
    })
  }

  if (sections.length === 0 && markdown.trim()) {
    sections.push({
      title: '概述',
      content: markdown,
      html: md.render(markdown)
    })
  }

  return sections
}

const loadTutorial = async (docId: number) => {
  isLoading.value = true
  try {
    let markdown = cachedMarkdowns.value.get(docId)
    if (!markdown) {
      const fileIndex = docId - 1
      if (fileIndex >= 0 && fileIndex < tutorialFiles.length) {
        const baseUrl = import.meta.env.BASE_URL
        const response = await fetch(`${baseUrl}guides/${tutorialFiles[fileIndex]}`)
        if (!response.ok) throw new Error('加载失败')
        markdown = await response.text()
        cachedMarkdowns.value.set(docId, markdown)
        if (!tutorialsChaptersMeta.value.has(docId)) {
          const titles = extractSectionTitles(markdown)
          const sections = titles.map((title, idx) => ({ title, index: idx }))
          tutorialsChaptersMeta.value.set(docId, sections)
        }
      }
    }
    if (markdown) {
      tutorialMarkdown.value = markdown
      tutorialSections.value = splitIntoSections(markdown)
      const doc = docs.value.find(d => d.id === docId)
      if (doc) doc.pages = tutorialSections.value.length
    } else {
      throw new Error('无法获取教程内容')
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

const currentDocId = ref<number | null>(null)
const currentSectionIndex = ref(0)
const isLoading = ref(false)
const tutorialMarkdown = ref('')
const tutorialSections = ref<Array<{ title: string; content: string; html: string }>>([])

const splitRatio = ref(50)
const isDragging = ref(false)
const tutorialContentRef = ref<HTMLElement | null>(null)

const currentHtml = computed(() => {
  if (tutorialSections.value.length > 0 && currentSectionIndex.value < tutorialSections.value.length) {
    return tutorialSections.value[currentSectionIndex.value]!.html
  }
  return ''
})

const currentSectionTitle = computed(() => {
  if (tutorialSections.value.length > 0 && currentSectionIndex.value < tutorialSections.value.length) {
    const title = tutorialSections.value[currentSectionIndex.value]!.title
    return title && title.trim() ? title.trim() : '小节'
  }
  return ''
})

const currentPlaygroundProjectId = computed(() => {
  const doc = docs.value.find(d => d.id === currentDocId.value)
  return doc ? doc.playgroundProjectId : null
})

const totalSections = computed(() => tutorialSections.value.length)

const chapterProgressText = computed(() => {
  if (totalSections.value > 0) {
    return `第 ${currentSectionIndex.value + 1} / ${totalSections.value} 节`
  }
  return ''
})

const currentDoc = computed(() => {
  return docs.value.find(doc => doc.id === currentDocId.value)
})

const currentDocTitle = computed(() => currentDoc.value?.title || '')

const headerTitle = computed(() => {
  if (!currentDoc.value) return ''
  const docTitle = currentDoc.value.title
  const sectionTitle = currentSectionTitle.value
  const progress = chapterProgressText.value ? ` (${chapterProgressText.value})` : ''
  return `${docTitle} - ${sectionTitle}${progress}`
})

const getDocTotalSections = (docId: number): number => {
  const sections = tutorialsChaptersMeta.value.get(docId)
  return sections ? sections.length : 0
}

const hasPreviousDoc = computed(() => currentDoc.value ? currentDoc.value.id > 1 : false)
const hasNextDoc = computed(() => currentDoc.value ? currentDoc.value.id < docs.value.length : false)

const prevSectionDisplayText = computed(() => {
  if (hasPrevSection.value) {
    const title = tutorialSections.value[currentSectionIndex.value - 1]!.title
    return title && title.trim() ? title.trim() : '概述'
  } else if (hasPreviousDoc.value) {
    const prevDocId = currentDoc.value!.id - 1
    const prevDoc = docs.value.find(d => d.id === prevDocId)
    return prevDoc ? prevDoc.title : ''
  }
  return '无上一节'
})

const nextSectionDisplayText = computed(() => {
  if (hasNextSection.value) {
    const title = tutorialSections.value[currentSectionIndex.value + 1]!.title
    return title && title.trim() ? title.trim() : '概述'
  } else if (hasNextDoc.value) {
    const nextDocId = currentDoc.value!.id + 1
    const nextDoc = docs.value.find(d => d.id === nextDocId)
    return nextDoc ? nextDoc.title : ''
  }
  return '无下一节'
})

const hasPrevSection = computed(() => currentSectionIndex.value > 0)
const hasNextSection = computed(() => currentSectionIndex.value < totalSections.value - 1)

const prevButtonLabel = computed(() => {
  if (hasPrevSection.value) return '上一节'
  if (hasPreviousDoc.value) return '上一篇'
  return '上一节'
})
const nextButtonLabel = computed(() => {
  if (hasNextSection.value) return '下一节'
  if (hasNextDoc.value) return '下一篇'
  return '下一节'
})

// ========== 强制刷新页面跳转到指定文档（可选章节） ==========
const navigateToDoc = (docId: number, sectionIndex: number = 1) => {
  // 如果目标文档与当前相同，且当前在详情页，则使用 SPA 内导航（不刷新）
  if (currentDocId.value === docId && currentDocId.value !== null) {
    // 如果章节索引相同则无需操作
    if (currentSectionIndex.value + 1 === sectionIndex) return
    router.push({
      name: 'explore',
      params: { docId, sectionIndex }
    })
    return
  }
  // 不同文档或从列表页进入，强制刷新页面
  const routeLocation = router.resolve({
    name: 'explore',
    params: { docId, sectionIndex }
  })
  window.location.href = routeLocation.href
}

// ========== 跳转逻辑修改 ==========
const openDoc = (doc: any) => {
  navigateToDoc(doc.id, 1)   // 打开文档，默认显示第一节
}

const goPrevSection = () => {
  if (hasPrevSection.value) {
    // 同一文档内切换章节，使用 router.push（不刷新）
    const newIndex = currentSectionIndex.value - 1
    router.push({
      name: 'explore',
      params: {
        docId: currentDocId.value!,
        sectionIndex: newIndex + 1
      }
    })
  } else if (hasPreviousDoc.value) {
    // 切换到上一篇文档，强制刷新页面
    const prevDocId = currentDoc.value!.id - 1
    const totalSectionsPrev = getDocTotalSections(prevDocId)
    const targetSection = totalSectionsPrev > 0 ? totalSectionsPrev : 1
    navigateToDoc(prevDocId, targetSection)
  }
}

const goNextSection = () => {
  if (hasNextSection.value) {
    // 同一文档内切换章节，使用 router.push（不刷新）
    const newIndex = currentSectionIndex.value + 1
    router.push({
      name: 'explore',
      params: {
        docId: currentDocId.value!,
        sectionIndex: newIndex + 1
      }
    })
  } else if (hasNextDoc.value) {
    // 切换到下一篇文档，强制刷新页面（默认第一节）
    const nextDocId = currentDoc.value!.id + 1
    navigateToDoc(nextDocId, 1)
  }
}

// 返回列表页（SPA 内跳转）
const backToList = () => {
  router.push({ name: 'explore' })
}

const previousDoc = () => {
  if (hasPreviousDoc.value) {
    navigateToDoc(currentDoc.value!.id - 1, 1)
  }
}

const nextDoc = () => {
  if (hasNextDoc.value) {
    navigateToDoc(currentDoc.value!.id + 1, 1)
  }
}

// ========== 顶部菜单（悬浮弹窗）逻辑 ==========
const menuVisible = ref(false)
const menuButtonRef = ref<HTMLElement | null>(null)
const menuRootRef = ref<HTMLElement | null>(null)
const menuHoverDocId = ref<number | null>(null)
const submenuAnchorRect = ref<DOMRect | null>(null)
let hideSubmenuTimer: ReturnType<typeof setTimeout> | null = null

const clearHideTimer = () => {
  if (hideSubmenuTimer) {
    clearTimeout(hideSubmenuTimer)
    hideSubmenuTimer = null
  }
}

const onMenuItemMouseEnter = (docId: number, event: MouseEvent) => {
  clearHideTimer()
  const target = event.currentTarget as HTMLElement
  if (target) {
    submenuAnchorRect.value = target.getBoundingClientRect()
    menuHoverDocId.value = docId
  }
}

const onMenuItemMouseLeave = () => {
  // 留空，避免过早隐藏子菜单
}

const onSubMenuMouseEnter = () => {
  clearHideTimer()
}

const onSubMenuMouseLeave = () => {
  clearHideTimer()
  hideSubmenuTimer = setTimeout(() => {
    menuHoverDocId.value = null
    submenuAnchorRect.value = null
  }, 300)
}

const handleSubMenuSelect = (value: string) => {
  const [docIdStr, sectionIdxStr] = value.split(':')
  const docId = Number(docIdStr)
  const sectionIndex = Number(sectionIdxStr) + 1   // 转为 1-based

  if (!isNaN(docId) && !isNaN(sectionIndex)) {
    if (currentDocId.value === docId) {
      // 同一文档内切换章节，不刷新
      router.push({
        name: 'explore',
        params: { docId, sectionIndex }
      })
    } else {
      // 切换到不同文档，强制刷新页面
      navigateToDoc(docId, sectionIndex)
    }
  }
  menuVisible.value = false
  menuHoverDocId.value = null
  submenuAnchorRect.value = null
  clearHideTimer()
}

const toggleMenu = (event: Event) => {
  event.stopPropagation()
  menuVisible.value = !menuVisible.value
  if (!menuVisible.value) {
    menuHoverDocId.value = null
    submenuAnchorRect.value = null
    clearHideTimer()
  }
}

const onGlobalClick = (e: MouseEvent) => {
  if (!menuVisible.value) return
  const target = e.target as HTMLElement
  if (menuButtonRef.value && menuButtonRef.value.contains(target)) return
  if (menuRootRef.value && menuRootRef.value.contains(target)) return
  const submenuPortal = document.querySelector('.submenu-portal')
  if (submenuPortal && submenuPortal.contains(target)) return
  menuVisible.value = false
  menuHoverDocId.value = null
  submenuAnchorRect.value = null
  clearHideTimer()
}

const menuPositionStyle = computed(() => {
  if (!menuButtonRef.value) return { left: '0px', top: '0px' }
  const rect = menuButtonRef.value.getBoundingClientRect()
  const left = rect.right + 4
  const top = rect.top
  const winWidth = window.innerWidth
  const estimatedWidth = 200
  let finalLeft = left
  if (left + estimatedWidth > winWidth - 8) {
    finalLeft = rect.left - estimatedWidth - 4
  }
  return {
    left: `${finalLeft}px`,
    top: `${top}px`
  }
})

const mainMenuItems = computed(() => {
  return docs.value.map(doc => ({
    id: doc.id,
    label: doc.title,
    children: (tutorialsChaptersMeta.value.get(doc.id) || []).map(section => ({
      label: section.title,
      value: `${doc.id}:${section.index}`
    }))
  }))
})

const currentSubmenuItems = computed(() => {
  if (menuHoverDocId.value === null) return []
  const doc = docs.value.find(d => d.id === menuHoverDocId.value)
  if (!doc) return []
  const sections = tutorialsChaptersMeta.value.get(menuHoverDocId.value) || []
  if (sections.length === 0 && !isPreloading.value) {
    return [{ label: '章节加载中...', value: '', disabled: true }]
  }
  return sections.map(section => ({
    label: section.title,
    value: `${menuHoverDocId.value}:${section.index}`
  }))
})

const submenuDirection = computed(() => {
  if (!submenuAnchorRect.value) return 'right'
  const winWidth = window.innerWidth
  if (submenuAnchorRect.value.right + 200 > winWidth) return 'left'
  return 'right'
})

// ========== 路由监听（调整当前状态）==========
watch(() => route.params.docId, (newDocId) => {
  if (newDocId) {
    const id = Number(newDocId)
    if (!isNaN(id) && id !== currentDocId.value) {
      currentDocId.value = id
    }
  } else {
    currentDocId.value = null
  }
}, { immediate: true })

watch(() => route.params.sectionIndex, (newIndex) => {
  if (newIndex !== undefined && currentDocId.value !== null) {
    const idx = Number(newIndex) - 1
    if (!isNaN(idx) && idx !== currentSectionIndex.value) {
      currentSectionIndex.value = idx
    }
  } else if (newIndex === undefined && currentDocId.value !== null) {
    if (currentSectionIndex.value !== 0) {
      currentSectionIndex.value = 0
    }
  }
}, { immediate: true })

watch(currentDocId, async (newId) => {
  if (newId) {
    await loadTutorial(newId)
    const total = tutorialSections.value.length
    if (total > 0) {
      let targetIndex = currentSectionIndex.value
      if (targetIndex < 0 || targetIndex >= total) {
        targetIndex = 0
        router.replace({
          name: 'explore',
          params: {
            docId: newId,
            sectionIndex: targetIndex + 1
          }
        })
      }
      currentSectionIndex.value = targetIndex
    }
  } else {
    tutorialSections.value = []
    currentSectionIndex.value = 0
  }
}, { immediate: true })

watch(currentSectionIndex, () => {
  const wrapper = document.querySelector('.markdown-wrapper') as HTMLElement
  if (wrapper) wrapper.scrollTop = 0
})

// ========== 拖拽分割（保留原逻辑）==========
const startDragging = (e: MouseEvent) => {
  e.preventDefault()
  isDragging.value = true
}

const stopDragging = () => {
  isDragging.value = false
}

const handleMouseMove = (e: MouseEvent) => {
  if (!isDragging.value || !tutorialContentRef.value) return
  const container = tutorialContentRef.value
  const rect = container.getBoundingClientRect()
  let newRatio = ((e.clientX - rect.left) / rect.width) * 100
  newRatio = Math.min(60, Math.max(40, newRatio))
  splitRatio.value = newRatio
}

onMounted(async () => {
  await preloadAllTutorials()
  window.addEventListener('click', onGlobalClick)
  window.addEventListener('mousemove', handleMouseMove)
  window.addEventListener('mouseup', stopDragging)
})
</script>

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
      width: 500px;
      overflow: hidden;
      position: relative;
      background: white;
      border-right: 1px solid #eef2f8;

      .chapter-header {
        flex-shrink: 0;
        display: flex;
        align-items: center;
        padding: 12px 24px;
        background: #fafbfc;
        border-bottom: 1px solid #eef2f8;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
        z-index: 5;

        .menu-button {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 32px;
          height: 32px;
          margin-left: 12px;
          margin-right: 4px;
          background: transparent;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          color: #5b6e8c;
          transition: all 0.2s;
          flex-shrink: 0;

          &:hover {
            background: #f0f2f5;
            color: #108efe;
          }
        }

        .chapter-info {
          display: flex;
          align-items: baseline;
          gap: 12px;
          flex-wrap: nowrap;
          flex: 1;
          min-width: 0;

          .doc-title-text {
            font-size: 18px;
            font-weight: 700;
            color: #1f2937;
            white-space: nowrap;
          }

          .section-info {
            display: flex;
            align-items: baseline;
            gap: 6px;
            min-width: 0;
            flex: 1;

            .section-title {
              font-size: 14px;
              font-weight: 400;
              color: #6b7280;
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
              flex-shrink: 1;
            }

            .section-progress {
              font-size: 13px;
              color: #9ca3af;
              white-space: nowrap;
              flex-shrink: 0;
            }
          }
        }
      }

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

      .markdown-content {
        font-size: 15px;
        line-height: 1.75;
        color: #2c3e50;

        :deep(h1) {
          font-size: 28px;
          border-bottom: 2px solid #6c757d;
          padding-bottom: 12px;
        }

        :deep(blockquote) {
          border-left: 4px solid #6c757d;
          padding-left: 1.2em;
          margin: 1.2em 0;
          color: #5b6e8c;
          font-style: italic;
        }

        :deep(pre) {
          background: #f8fafc;
          border-left: 4px solid #6c757d;
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

        :deep(a) {
          color: #2c3e50;
          text-decoration: none;
          border-bottom: 1px solid #6c757d;
          transition: all 0.2s ease;

          &:hover {
            background: #f0f7ff;
            padding: 0 2px;
          }
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

        :deep(code) {
          background: #f0f7ff;
          color: #2c3e50;
          padding: 0.2em 0.4em;
          border-radius: 4px;
          font-family: 'Monaco', 'Courier New', monospace;
          font-size: 0.9em;
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

      .bottom-control-bar-text {
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
        padding: 20px 24px;
        background: rgba(255, 255, 255, 0.96);
        backdrop-filter: blur(4px);
        border-top: 1px solid #eef2f8;
        z-index: 10;

        .nav-text {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 6px;
          cursor: pointer;
          transition: all 0.2s ease;
          text-align: left;
          padding: 4px 0;

          &.prev-text {
            text-align: left;
          }
          &.next-text {
            text-align: right;
            align-items: flex-end;
          }

          &:not(.disabled):hover {
            .nav-label {
              color: #108efe;
            }
            .nav-section-title {
              color: #108efe;
            }
          }

          &.disabled {
            opacity: 0.4;
            cursor: not-allowed;
          }

          .nav-label {
            font-size: 13px;
            font-weight: 500;
            color: #9ca3af;
            transition: color 0.2s;
          }

          .nav-section-title {
            font-size: 14px;
            font-weight: 500;
            color: #2c3e50;
            transition: color 0.2s;
            line-height: 1.4;
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }
        }
      }
    }

    .tutorial-right {
      display: flex;
      width: auto;
      flex: 1;
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

.floating-menu {
  @include controller-style;
  padding: 4px 4px;
  box-sizing: border-box;
  animation: menu-fade-in 200ms cubic-bezier(0.2, 0.8, 0.2, 1) both;

  .menu-list {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .menu-item {
    position: relative;

    .menu-item-content {
      padding: 6px 12px;
      margin: 0;
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      border-radius: 8px;
      transition: background-color 0.15s ease;

      &:hover {
        background-color: rgba(0, 0, 0, 0.1);
      }

      .menu-label {
        font-size: 14px;
        font-weight: 400;
        flex: 1;
      }

      .submenu-arrow {
        display: inline-flex;
        align-items: center;
        color: inherit;
        width: 9px;
        height: 9px;

        svg {
          display: block;
          width: 100%;
          height: 100%;
          path {
            stroke: currentColor;
            opacity: 0.6;
          }
        }
      }
    }
  }
}

@keyframes menu-fade-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>