<template>
    <div class="example-container" v-if="authState.isUserAuthenticated">
        <div class="example-content">
            <!-- 搜索框 -->
            <div class="search-section">
                <div class="search-wrapper">
                    <input
                        type="text"
                        v-model="searchInput"
                        @input="handleSearchInput"
                        placeholder="搜索项目..."
                        class="search-input"
                    />
                </div>
            </div>

            <!-- 标签筛选区域：标题与滚动标签同行 -->
            <div class="filter-row tags-row">
                <div class="filter-label">按标签筛选</div>
                <div class="tags-holder">
                    <button class="tag-add-btn" @click="openTagPicker" @mousedown.stop>+</button>
                    <div
                        ref="tagsScrollContainerRef"
                        class="tags-scroll-container"
                        @mousedown="startTagsDrag"
                        @wheel.prevent="handleTagsWheel"
                    >
                        <div class="tags-scroll-wrapper" :style="{ cursor: isDraggingTags ? 'grabbing' : 'grab' }">
                            <button
                                v-for="tag in displayTags"
                                :key="tag"
                                class="tag-filter-btn"
                                :class="{ active: activeTags.includes(tag) }"
                                @click="handleTagClickWithDragCheck(tag, $event)"
                            >
                                {{ tag }}
                            </button>
                            <span v-if="availableTags.length === 0" class="tag-placeholder">暂无标签</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 排序区域：标题与按钮组同行 -->
            <div class="filter-row sort-row">
                <div class="filter-label">排序方式</div>
                <div class="sort-buttons-group">
                    <button
                        class="sort-option-btn"
                        :class="{ active: sortBy === OrderedBy.CREATED_AT }"
                        @click="(e) => { animateButton(e); handleSortChange(OrderedBy.CREATED_AT); }"
                    >
                        按创建时间排序
                    </button>
                    <button
                        class="sort-option-btn"
                        :class="{ active: sortBy === OrderedBy.UPDATED_AT }"
                        @click="(e) => { animateButton(e); handleSortChange(OrderedBy.UPDATED_AT); }"
                    >
                        按更新时间排序
                    </button>
                    <button
                        class="sort-option-btn"
                        :class="{ active: sortBy === OrderedBy.NAME }"
                        @click="(e) => { animateButton(e); handleSortChange(OrderedBy.NAME); }"
                    >
                        按项目名称排序
                    </button>
                </div>
            </div>

            <!-- 项目网格容器 -->
            <div class="projects-wrapper" ref="scrollContainerRef">
                <div class="examples-grid" ref="gridContainerRef">
                    <div v-if="loading" class="loading-state">加载中...</div>
                    <div v-else-if="projects.length === 0" class="empty-state">
                        <div class="empty-info">暂无项目</div>
                    </div>
                    <template v-else>
                        <ExampleDemoFrame
                            v-for="item in projects"
                            :key="item.project_id"
                            :item="item"
                            class="example-card"
                        />
                    </template>
                </div>

                <div class="carousel-indicators" v-if="totalPages > 1" @mousedown.stop @touchstart.stop>
                    <span
                        v-for="i in totalPages"
                        :key="i"
                        class="indicator-dot"
                        :class="{ active: currentPage === (i-1) }"
                        @click="goToPage(i-1)"
                        :aria-label="`第 ${i} 页`"
                    ></span>
                </div>
            </div>

            <!-- 标签选择弹窗由 TagSelectionModal 组件通过 modalStore 管理 -->
        </div>
    </div>
    <Mask v-else />
</template>

<script lang="ts" setup>
import { useRouter } from 'vue-router'
import { ref, onMounted, onBeforeUnmount, computed, nextTick } from 'vue';
import AuthenticatedServiceFactory from '@/utils/AuthenticatedServiceFactory';
import { useLoginStore } from '@/stores/loginStore'
import { useAuthState } from '@/stores/authState'
import Mask from '@/views/Mask.vue'
import ExampleDemoFrame from './ExampleDemoFrame.vue';
import { handleNetworkError } from '@/utils/networkError';
import { ApiError } from '@/utils/api';
import notify from '@/components/Notification/notify';
import { ProjectListFilter, type ExploreListItem } from '@/utils/api';
import { useProjectStore } from '@/stores/projectStore';
import { useModalStore } from '@/stores/modalStore'
import TagSelectionModal from '@/components/TagSelectionModal.vue'

const loginStore = useLoginStore();
const authState = useAuthState();
const projectStore = useProjectStore();
const router = useRouter()
const authService = AuthenticatedServiceFactory.getService()

const OrderedBy = ProjectListFilter.ordered_by;

// 所有可用标签
const availableTags = ref<string[]>([])

const projects = ref<ExploreListItem[]>([])
const totalCount = ref<number>(0)
const loading = ref<boolean>(false)

// 选中的标签（默认取 availableTags 的前三个）
const activeTags = ref<string[]>([])
const searchKeyword = ref<string>('')
const searchInput = ref<string>('')
const sortBy = ref<ProjectListFilter.ordered_by>(OrderedBy.CREATED_AT)

// 仅展示的标签（页面顶部）：如果选中多个则在一行内全部显示（横向滚动）
const displayTags = computed(() => activeTags.value)

// modal store for opening TagSelectionModal
const modalStore = useModalStore()

const currentPage = ref<number>(0)
const pageSize = ref<number>(20)
const totalPages = computed(() => {
    const safePageSize = Math.max(1, Math.floor(pageSize.value) || 1)
    if (!totalCount.value || totalCount.value <= 0) return 0
    return Math.ceil(totalCount.value / safePageSize)
})

let scrollDebounceTimer: number | null = null
let loadWatchTimer: number | null = null
let resizeDebounceTimer: number | null = null
let windowResizeTimer: number | null = null

interface CacheKey {
    tags: string[]
    search: string
    sort: ProjectListFilter.ordered_by
    offset: number
    limit: number
}

const dataCache = new Map<string, ExploreListItem[]>()

function getCacheKey(offset: number, limit: number): string {
    return JSON.stringify({
        tags: activeTags.value.sort(),
        search: searchKeyword.value,
        sort: sortBy.value,
        offset,
        limit
    })
}

function clearCache() {
    dataCache.clear()
}

const gridContainerRef = ref<HTMLElement | null>(null)
const tagsScrollContainerRef = ref<HTMLElement | null>(null)
const cardHeight = ref<number>(280)
let resizeObserver: ResizeObserver | null = null
let suppressAutoReload = false

async function computePageSize(): Promise<boolean> {
    await nextTick()
    // 宽度使用 grid 容器， 高度优先使用外层的 scroll 容器以反映可视区域
    const widthSource = gridContainerRef.value ?? scrollContainerRef.value
    const heightSource = scrollContainerRef.value ?? gridContainerRef.value
    if (!widthSource || !heightSource) return false
    let containerWidth = widthSource.clientWidth
    let containerHeight = heightSource.clientHeight

    // 回退：如果高度过小或为 0，则基于视口计算可用高度（避免因 DOM 高度未填充导致计算错误）
    if (!containerHeight || containerHeight < 50) {
        const rect = heightSource.getBoundingClientRect()
        const viewportAvailable = Math.max(120, Math.floor(window.innerHeight - rect.top - 24))
        containerHeight = Math.max(containerHeight || 0, viewportAvailable)
    }
    if (!containerWidth || containerWidth === 0) return false

    // 布局参数（与样式保持一致）
    const cardMinWidth = 260
    const gap = 16

    // 计算列数与每列实际宽度（考虑 gap）
    const cols = Math.max(1, Math.floor((containerWidth + gap) / (cardMinWidth + gap)))
    const cardWidth = (containerWidth - (cols - 1) * gap) / cols

    // 估算卡片高度：使用宽高比与信息区固定估算值，避免临时 DOM 测量带来的抖动
    // Thumb 高度按 16:9 比例计算（padding-top:56.25%），信息区域按经验值估算
    const thumbHeight = Math.round(cardWidth * 0.5625)
    const infoAreaEstimate = 120 // 包括 title/tags/meta 的估算高度
    const measuredCardHeight = Math.max(220, thumbHeight + infoAreaEstimate)

    // 计算行数与每页容量（rows * cols）
    const rows = Math.max(1, Math.floor((containerHeight + gap) / (measuredCardHeight + gap)))
    const newPageSize = rows * cols

    if (newPageSize !== pageSize.value) {
        cardHeight.value = measuredCardHeight
        pageSize.value = newPageSize
        console.log('[Example] computePageSize -> cols=', cols, 'rows=', rows, 'cardWidth=', Math.round(cardWidth), 'cardHeight=', Math.round(measuredCardHeight), 'pageSize=', newPageSize)
        return true
    }
    cardHeight.value = measuredCardHeight
    return false
}

async function fetchProjectsRange(offset: number, limit: number, updateTotal: boolean = false) {
    const filterConditions: ProjectListFilter = {
        tags: activeTags.value,
        search_keyword: searchKeyword.value,
        ordered_by: sortBy.value,
        // 服务端期望的 ranging 是 (startIndex, endIndex)，因此传入 offset 和 offset+limit
        ranging: [offset, offset + limit]
    }
    const cacheKey = getCacheKey(offset, limit)
    if (dataCache.has(cacheKey)) {
        const cached = dataCache.get(cacheKey)!
        console.log(`[Example] cache hit offset=${offset} limit=${limit} items=${cached.length}`)
        projects.value = cached
        return
    }
    try {
        console.log(`[Example] fetchProjectsRange offset=${offset} limit=${limit} (ranging -> ${filterConditions.ranging})`, filterConditions)
        const response = await authService.getExploreProjectsApiExploreProjectsPost(filterConditions) as any;
        console.log('[Example] fetchProjectsRange raw response:', response)
        const newProjects = response.projects || [];
        const newTotal = response.total ?? 0;
        console.log(`[Example] fetched ${newProjects.length} items, response total=${newTotal}`)
        dataCache.set(cacheKey, newProjects)
        projects.value = newProjects
        if (updateTotal) {
            const prev = totalCount.value
            totalCount.value = newTotal
            console.log(`[Example] totalCount updated: ${prev} -> ${totalCount.value}`)
        }
    } catch (error) {
        if (error instanceof ApiError) {
            switch (error.status) {
                case 422:
                    notify({ message: '验证错误', type: 'error' });
                    break;
                default:
                    notify({ message: handleNetworkError(error), type: 'error' });
                    break;
            }
        } else {
            notify({ message: handleNetworkError(error), type: 'error' });
        }
        throw error
    }
}

/**
 * 只获取符合当前筛选条件的项目总数（不拉取项目数据）
 */
async function fetchTotalCountOnly() {
    try {
        const countFilter: ProjectListFilter = {
            tags: activeTags.value,
            search_keyword: searchKeyword.value,
            ordered_by: sortBy.value
        }
        console.log('[Example] fetchTotalCountOnly filter=', countFilter)
        const cnt = await (authService as any).getExploreProjectsNumApiExploreProjectsNumPost(countFilter) as number
        console.log('[Example] fetchTotalCountOnly returned=', cnt)
        const prev = totalCount.value
        totalCount.value = cnt ?? 0
        if (prev !== totalCount.value) console.log(`[Example] totalCount updated: ${prev} -> ${totalCount.value}`)
    } catch (e) {
        console.warn('[Example] fetchTotalCountOnly failed, keeping previous totalCount', e)
    }
}

/**
 * 按页面索引获取对应页的数据（仅在用户点击分页时调用）
 */
async function fetchPageByIndex(pageIndex: number) {
    if (pageIndex < 0) pageIndex = 0
    const safePageSize = Math.max(1, Math.floor(pageSize.value) || 1)
    const maxPageIndex = Math.max(0, Math.ceil(totalCount.value / safePageSize) - 1)
    if (pageIndex > maxPageIndex) pageIndex = maxPageIndex

    currentPage.value = pageIndex
    clearCache()
    const offset = currentPage.value * safePageSize
    console.log('[Example] fetchPageByIndex page=', pageIndex, 'offset=', offset, 'limit=', safePageSize)
    await fetchProjectsRange(offset, safePageSize, false)
    // 保证滚动回到顶部
    if (scrollContainerRef.value) scrollContainerRef.value.scrollTop = 0
}


async function resetAndLoad() {
    if (loading.value) return
    currentPage.value = 0
    clearCache()
        await fetchTotalCountOnly()
        await computePageSize()
        await fetchPageByIndex(0)
}

function handleTagClick(tag: string) {
    const index = activeTags.value.indexOf(tag)
    if (index === -1) activeTags.value.push(tag)
    else activeTags.value.splice(index, 1)
    resetAndLoad()
}

function handleSearchInput() {
    if (scrollDebounceTimer) clearTimeout(scrollDebounceTimer);
    scrollDebounceTimer = window.setTimeout(() => {
        searchKeyword.value = searchInput.value;
        resetAndLoad();
    }, 300);
}

function handleSortChange(value: ProjectListFilter.ordered_by) {
    if (sortBy.value === value) return;
    sortBy.value = value;
    resetAndLoad();
}

const scrollContainerRef = ref<HTMLElement | null>(null)
function onScroll() {
    // 禁用基于滚动的分页。分页仅通过右侧圆点点击触发。
    return
}

async function goToNextPage() {
    if (currentPage.value < totalPages.value - 1 && !loading.value) {
           await fetchPageByIndex(currentPage.value + 1)
    }
}

async function loadPageData() {
    // 兼容保留：如果需要完整 reload（count + page），调用此函数
    if (loading.value) return
    console.log('[Example] loadPageData START')
    loading.value = true
    // 看门狗：如果超过 15s 还未完成则自动清除 loading，避免无限加载卡死 UI
    if (loadWatchTimer) clearTimeout(loadWatchTimer)
    loadWatchTimer = window.setTimeout(() => {
        if (loading.value) {
            console.warn('[Example] loadPageData watchdog timeout, clearing loading flag')
            loading.value = false
        }
    }, 15000)
    try {
        await fetchTotalCountOnly()
        await computePageSize()
        await fetchPageByIndex(currentPage.value)
    } catch (error) {
        console.error('加载数据失败:', error)
    } finally {
        if (loadWatchTimer) {
            clearTimeout(loadWatchTimer)
            loadWatchTimer = null
        }
        loading.value = false
        console.log('[Example] loadPageData END')
    }
}
const isDraggingTags = ref(false)
let tagsDragStartX = 0
let tagsDragStartScrollLeft = 0
let skipTagClick = false
const DRAG_THRESHOLD = 5

function startTagsDrag(e: MouseEvent) {
    if (!tagsScrollContainerRef.value || e.button !== 0) return
    isDraggingTags.value = true
    tagsDragStartX = e.pageX - tagsScrollContainerRef.value.offsetLeft
    tagsDragStartScrollLeft = tagsScrollContainerRef.value.scrollLeft
    skipTagClick = false
    window.addEventListener('mousemove', onTagsDragMove)
    window.addEventListener('mouseup', onTagsDragEnd)
    e.preventDefault()
}

function onTagsDragMove(e: MouseEvent) {
    if (!isDraggingTags.value || !tagsScrollContainerRef.value) return
    const x = e.pageX - tagsScrollContainerRef.value.offsetLeft
    const walk = (x - tagsDragStartX) * 1.5
    tagsScrollContainerRef.value.scrollLeft = tagsDragStartScrollLeft - walk
    if (Math.abs(walk) > DRAG_THRESHOLD) skipTagClick = true
    e.preventDefault()
}

function onTagsDragEnd() {
    isDraggingTags.value = false
    window.removeEventListener('mousemove', onTagsDragMove)
    window.removeEventListener('mouseup', onTagsDragEnd)
    setTimeout(() => { skipTagClick = false }, 50)
}

function handleTagsWheel(e: WheelEvent) {
    if (!tagsScrollContainerRef.value) return
    tagsScrollContainerRef.value.scrollLeft += e.deltaY
    e.preventDefault()
}

function handleTagClickWithDragCheck(tag: string, event: MouseEvent) {
    if (skipTagClick) {
        skipTagClick = false
        return
    }
    handleTagClick(tag)
}

function openTagPicker() {
    const modalId = 'example-tag-selection'
    if (modalStore.findModal(modalId)) return

    modalStore.createModal({
        id: modalId,
        title: '选择标签',
        isActive: true,
        isDraggable: true,
        isResizable: false,
        isModal: true,
        position: {
            x: (window.innerWidth - 520) / 2,
            y: (window.innerHeight - 520) / 2,
        },
        size: { width: 520, height: 520 },
        component: TagSelectionModal,
        props: {
            modalId: modalId,
            initialTags: activeTags.value,
            onConfirm: (newTags: string[]) => {
                activeTags.value = newTags
                resetAndLoad()
            }
        }
    })
}

async function goToPage(pageIndex: number) {
    if (pageIndex < 0 || pageIndex >= totalPages.value) return
    if (currentPage.value === pageIndex) return
    await fetchPageByIndex(pageIndex)
}

function animateButton(e: MouseEvent) {
    const el = e.currentTarget as HTMLElement | null;
    if(!el) return;
    el.classList.add('clicked');
    el.addEventListener('animationend', () => {
        el.classList.remove('clicked');
    }, { once: true });
}

function handleResize() {
    if (windowResizeTimer) clearTimeout(windowResizeTimer)
    windowResizeTimer = window.setTimeout(async () => {
        if (loading.value) return
        try {
            const changed = await computePageSize()
            if (changed) {
                const safePageSize = Math.max(1, Math.floor(pageSize.value) || 1)
                const maxPageIndex = Math.max(0, Math.ceil(totalCount.value / safePageSize) - 1)
                if (currentPage.value > maxPageIndex) currentPage.value = maxPageIndex
                if (!suppressAutoReload) {
                    suppressAutoReload = true
                    try {
                        await fetchPageByIndex(currentPage.value)
                    } catch (e) {
                        console.warn('[Example] handleResize fetchPageByIndex failed', e)
                    } finally {
                        suppressAutoReload = false
                    }
                }
            }
        } catch (e) {
            console.warn('[Example] handleResize error', e)
        }
    }, 200)
}

onMounted(async () => {
    await loginStore.checkAuthStatus();
    if (authState.isUserAuthenticated) {
        await projectStore.getAllTags()
        availableTags.value = projectStore.allProjectTags || []
        // 默认选中前三个标签
        activeTags.value = availableTags.value.slice(0, 3)
        await nextTick()
        await resetAndLoad();
        if (scrollContainerRef.value) {
            scrollContainerRef.value.addEventListener('scroll', onScroll)
        }
        window.addEventListener('resize', handleResize)
        if (gridContainerRef.value) {
            resizeObserver = new ResizeObserver(() => {
                if (resizeDebounceTimer) clearTimeout(resizeDebounceTimer)
                resizeDebounceTimer = window.setTimeout(async () => {
                    if (loading.value) return
                    try {
                        const changed = await computePageSize()
                        if (changed) {
                            const safePageSize = Math.max(1, Math.floor(pageSize.value) || 1)
                            const maxPageIndex = Math.max(0, Math.ceil(totalCount.value / safePageSize) - 1)
                            if (currentPage.value > maxPageIndex) currentPage.value = maxPageIndex
                            if (!suppressAutoReload) {
                                suppressAutoReload = true
                                try {
                                    await fetchPageByIndex(currentPage.value)
                                } catch (e) {
                                    console.warn('[Example] resizeObserver fetchPageByIndex failed', e)
                                } finally {
                                    suppressAutoReload = false
                                }
                            }
                        }
                    } catch (e) {
                        console.warn('[Example] resizeObserver handler error', e)
                    }
                }, 200)
            })
            resizeObserver.observe(gridContainerRef.value)
        }
    } else {
        router.replace({ name: 'login' });
    }
});

onBeforeUnmount(() => {
    if (scrollContainerRef.value) scrollContainerRef.value.removeEventListener('scroll', onScroll)
    window.removeEventListener('resize', handleResize)
    if (resizeObserver) resizeObserver.disconnect()
    if (scrollDebounceTimer) clearTimeout(scrollDebounceTimer);
    window.removeEventListener('mousemove', onTagsDragMove)
    window.removeEventListener('mouseup', onTagsDragEnd)
});
</script>

<style lang="scss" scoped>
    @keyframes clickPulse {
        0% { transform: scale(1); }
        50% { transform: scale(0.95); }
        100% { transform: scale(1); }
    }
    
    .example-container {
        display: flex;
        flex: 1;
        position: relative;
        background-color: #f5f7fa;
        overflow-x: hidden;
    }
    
    .example-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        padding: 12px 28px;
        box-sizing: border-box;
        overflow-x: hidden;
        max-width: 100%;
    }
    
    .search-section {
        margin-bottom: 12px;
        display: flex;
        justify-content: center;
        width: 100%;
        
        .search-wrapper {
            width: 75vh;
            max-width: 100%;
        }
        
        .search-input {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #e4e7ed;
            border-radius: 20px;
            font-size: 13px;
            outline: none;
            transition: all 0.2s ease;
            background: white;
            box-sizing: border-box;
            height: 34px;
            
            &:focus {
                border-color: #cbd5e1;
                box-shadow: none;
            }
        }
    }
    
    /* 筛选行布局：标题与内容同行 */
    .filter-row {
        display: flex;
        align-items: center;
        gap: 8px;
        width: 100%;
        margin-bottom: 12px;
        
        .filter-label {
            width: 84px;
            font-size: 13px;
            font-weight: 600;
            color: #6b7280; /* 改为灰色 */
            white-space: nowrap;
            flex-shrink: 0;
            letter-spacing: 0.3px;
            position: relative;
            padding-left: 6px;
        }
    }

    .tags-holder {
        display: flex;
        align-items: center;
        gap: 8px;
        width: 100%;
    }

    .tags-holder .tag-add-btn {
        height: 28px;
        width: 28px;
        font-size: 16px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        border: 1px dashed #cbd5e1;
        background: white;
        color: #6b7280;
        cursor: pointer;
        flex-shrink: 0;
    }
    
    /* 标签滚动容器 - 无滚动条，仅通过拖拽和滚轮滚动，占据剩余宽度 */
    .tags-scroll-container {
        flex: 1;
        overflow-x: auto;
        overflow-y: hidden;
        white-space: nowrap;
        cursor: grab;
        /* 隐藏滚动条 */
        &::-webkit-scrollbar {
            display: none;
        }
        scrollbar-width: none;
        -ms-overflow-style: none;
        
        .tags-scroll-wrapper {
            display: inline-flex;
            gap: 8px;
            padding: 2px 0;
            align-items: center;
        }
        
        .tag-filter-btn {
            height: 28px;
            font-size: 12px;
            font-weight: 500;
            color: rgba(20, 20, 20, 0.85);
            padding: 0 12px;
            transition: all 0.16s ease;
            min-width: 64px;
            text-align: center;
            border-radius: 16px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #e4e7ed;
            cursor: pointer;
            white-space: nowrap;
            background-color: white;
            flex-shrink: 0;
            
            &:hover {
                background-color: #f7fafc;
                border-color: #d1d5db;
            }
            
            &.active {
                color: #ffffff;
                background-color: #409eff;
                border-color: #409eff;
                box-shadow: 0 2px 8px rgba(64, 158, 255, 0.16);
            }
        }

        .tag-add-btn {
            height: 28px;
            width: 28px;
            font-size: 16px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            border: 1px dashed #cbd5e1;
            background: white;
            color: #6b7280;
            cursor: pointer;
            flex-shrink: 0;
        }
        
        .tag-placeholder {
            display: inline-block;
            font-size: 13px;
            color: #909399;
            padding: 0 8px;
            line-height: 34px;
        }
    }
    
    /* 排序按钮组 - 占据剩余宽度，允许换行 */
    .sort-buttons-group {
        flex: 1;
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        
        .sort-option-btn {
            height: 28px;
            font-size: 12px;
            font-weight: 500;
            color: rgba(20, 20, 20, 0.85);
            padding: 0 14px;
            border-radius: 16px;
            background: white;
            border: 1px solid #e4e7ed;
            cursor: pointer;
            transition: all 0.16s ease;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            white-space: nowrap;
            
            &:hover {
                background-color: #f7fafc;
                border-color: #d1d5db;
            }
            
            &.active {
                color: #ffffff;
                background-color: #409eff;
                border-color: #409eff;
                box-shadow: 0 2px 8px rgba(64, 158, 255, 0.16);
            }
            
            &.clicked {
                animation: clickPulse 0.2s ease;
            }
        }
    }
    
    .projects-wrapper {
        flex: 1;
        /* 不允许内部出现滚动条：分页由右侧圆点或按钮控制 */
        overflow: hidden;
        overflow-x: hidden;
        position: relative; /* 使右侧分页点可绝对定位 */
        padding-right: 72px; /* 为右侧圆点留出空间，避免遮挡 */
        display: flex;
        align-items: stretch;
        
        &::-webkit-scrollbar {
            width: 8px;
        }
        
        &::-webkit-scrollbar-track {
            background: transparent;
        }
        
        &::-webkit-scrollbar-thumb {
            background: rgba(0, 0, 0, 0.15);
            border-radius: 4px;
            
            &:hover {
                background: rgba(0, 0, 0, 0.25);
            }
        }
        
        scrollbar-width: thin;
        scrollbar-color: rgba(0, 0, 0, 0.15) transparent;
    }
    
    .examples-grid {
        display: grid;
        /* 填充可用宽度并允许多列 */
        grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
        gap: 16px; /* 缩小行间距，修复大屏时的过大行距 */
        align-items: start;
        justify-items: center;
        padding: 6px 6px 12px 6px;
        /* 占据父容器高度，避免内部滚动，按页渲染多行 */
        flex: 1;
        height: 100%;
        box-sizing: border-box;
        overflow: hidden;
        /* 当项目不足以填满容器时，垂直居中 */
        align-content: center;
    
        .loading-state,
        .empty-state {
            grid-column: 1 / -1;
            text-align: center;
            padding: 60px 20px;
            color: #909399;
            font-size: 14px;
        }
        
        .empty-info {
            font-size: 16px;
            color: #c0c4cc;
        }
    }

    /* 右侧圆点分页（采用 ExampleCarousel 相同的圆点渲染，仅圆点，无背景） */
    .carousel-indicators {
        position: absolute;
        right: 12px;
        top: 50%;
        transform: translateY(-50%);
        z-index: 12;
        display: flex;
        flex-direction: column;
        gap: 10px;
        align-items: center;
        justify-content: center;
        padding: 0;
        background: none;
    }

    .carousel-indicators .indicator-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #cbd5e1;
        transition: all 0.18s ease;
        cursor: pointer;
        display: inline-block;
    }

    .carousel-indicators .indicator-dot.active {
        width: 14px;
        height: 14px;
        background: #2563eb;
    }

    /* 分页控件 */
    .pagination {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        padding: 12px 0 24px 0;

        .page-btn {
            padding: 6px 12px;
            border-radius: 6px;
            border: 1px solid #e4e7ed;
            background: white;
            cursor: pointer;
            color: #374151;
        }

        .page-numbers {
            display: flex;
            gap: 8px;
            align-items: center;
        }

        .page-number {
            padding: 6px 10px;
            border-radius: 6px;
            border: 1px solid transparent;
            background: white;
            cursor: pointer;
            color: #374151;

            &.active {
                background: #409eff;
                color: white;
                border-color: #409eff;
            }
        }
    }

    /* 标签选择弹窗由 `TagSelectionModal` 组件提供样式 */
    
    @media (max-width: 768px) {
        .example-content {
            padding: 16px;
        }
        
        .filter-row {
            gap: 12px;
            flex-wrap: wrap;   /* 小屏时标题和内容可换行，避免挤压 */
            
            .filter-label {
                width: 100%;
                margin-bottom: 4px;
            }
            
            .tags-scroll-container,
            .sort-buttons-group {
                flex: auto;
                width: 100%;
            }
        }
        
        .sort-buttons-group {
            gap: 8px;
            
            .sort-option-btn {
                padding: 0 14px;
                font-size: 12px;
            }
        }
        
        .tags-scroll-container .tag-filter-btn {
            min-width: 60px;
            padding: 0 12px;
            font-size: 12px;
        }
    }

//     // 背景粒子层（新增）
// .example-bg-particles {
//     position: absolute;
//     top: 0;
//     left: 0;
//     width: 100%;
//     height: 100%;
//     background-image: radial-gradient(#6366f1 0.8px, transparent 0.8px);  // 使用紫色调，与 Home 的蓝色区分
//     background-size: 28px 28px;
//     opacity: 0.25;
//     pointer-events: none;
//     z-index: 0;
// }

// // 渐变 orb 通用样式（新增）
// .example-orb {
//     position: absolute;
//     border-radius: 50%;
//     filter: blur(80px);
//     opacity: 0.35;
//     pointer-events: none;
//     z-index: 0;
// }

// // 各个 orb 的具体样式（数量和颜色与 Home 不同）
// .orb-1 {
//     width: 480px;
//     height: 480px;
//     background: #3b82f6;      // 蓝色
//     top: -200px;
//     right: -120px;
// }

// .orb-2 {
//     width: 420px;
//     height: 420px;
//     background: #ec489a;      // 粉红色（Home 没有）
//     bottom: -100px;
//     left: -150px;
// }

// .orb-3 {
//     width: 360px;
//     height: 360px;
//     background: #10b981;      // 翠绿色（Home 没有）
//     top: 50%;
//     left: 30%;
//     transform: translate(-30%, -50%);
// }

// .orb-4 {                      // 新增第四个 orb，进一步区分 Home
//     width: 300px;
//     height: 300px;
//     background: #f59e0b;      // 琥珀色
//     bottom: 20%;
//     right: 10%;
// }
</style>