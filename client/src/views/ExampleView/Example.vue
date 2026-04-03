<template>
    <div class="example-container" v-if="loginStore.loggedIn">
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
                <div 
                    ref="tagsScrollContainerRef" 
                    class="tags-scroll-container" 
                    @mousedown="startTagsDrag"
                    @wheel.prevent="handleTagsWheel"
                >
                    <div class="tags-scroll-wrapper" :style="{ cursor: isDraggingTags ? 'grabbing' : 'grab' }">
                        <button
                            v-for="tag in availableTags"
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
            </div>
        </div>
    </div>
    <Mask v-else />
</template>

<script lang="ts" setup>
import { useRouter } from 'vue-router'
import { ref, onMounted, onBeforeUnmount, computed, nextTick } from 'vue';
import AuthenticatedServiceFactory from '@/utils/AuthenticatedServiceFactory';
import { useLoginStore } from '@/stores/loginStore'
import Mask from '@/views/Mask.vue'
import ExampleDemoFrame from './ExampleDemoFrame.vue';
import { handleNetworkError } from '@/utils/networkError';
import { ApiError } from '@/utils/api';
import notify from '@/components/Notification/notify';
import { ProjectListFilter, type ExploreListItem } from '@/utils/api';
import { useProjectStore } from '@/stores/projectStore';

const loginStore = useLoginStore();
const projectStore = useProjectStore();
const router = useRouter()
const authService = AuthenticatedServiceFactory.getService()

const OrderedBy = ProjectListFilter.ordered_by;

// 所有可用标签
const availableTags = ref<string[]>([])

const projects = ref<ExploreListItem[]>([])
const totalCount = ref<number>(0)
const loading = ref<boolean>(false)

const activeTags = ref<string[]>([])
const searchKeyword = ref<string>('')
const searchInput = ref<string>('')
const sortBy = ref<ProjectListFilter.ordered_by>(OrderedBy.CREATED_AT)

const currentPage = ref<number>(0)
const pageSize = ref<number>(20)
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

let scrollDebounceTimer: number | null = null

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
const cardHeight = ref<number>(280)

async function computePageSize(): Promise<boolean> {
    await nextTick()
    if (!gridContainerRef.value) return false
    const container = gridContainerRef.value
    const containerHeight = container.clientHeight
    if (containerHeight === 0) return false
    const firstCard = container.querySelector('.example-card') as HTMLElement
    if (firstCard) {
        const rect = firstCard.getBoundingClientRect()
        const style = getComputedStyle(firstCard)
        const marginBottom = parseFloat(style.marginBottom) || 0
        cardHeight.value = rect.height + marginBottom
    }
    const containerWidth = container.clientWidth
    const cardMinWidth = 260
    const gap = 20
    const cols = Math.floor((containerWidth + gap) / (cardMinWidth + gap)) || 1
    const rows = Math.floor(containerHeight / cardHeight.value) + 1
    const newPageSize = Math.max(1, rows * cols)
    if (newPageSize !== pageSize.value) {
        pageSize.value = newPageSize
        return true
    }
    return false
}

async function fetchProjectsRange(offset: number, limit: number, updateTotal: boolean = true) {
    const filterConditions: ProjectListFilter = {
        tags: activeTags.value,
        search_keyword: searchKeyword.value,
        ordered_by: sortBy.value,
        ranging: [offset, limit]
    }
    const cacheKey = getCacheKey(offset, limit)
    if (dataCache.has(cacheKey)) {
        projects.value = dataCache.get(cacheKey)!
        return
    }
    try {
        console.log('Fetching projects with conditions:', filterConditions)
        const response = await authService.getExploreProjectsApiExploreProjectsPost(filterConditions) as any;
        const newProjects = response.projects || [];
        const newTotal = response.total ?? 0;
        dataCache.set(cacheKey, newProjects)
        projects.value = newProjects
        if (updateTotal) totalCount.value = newTotal
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

async function loadPageData() {
    if (loading.value) return
    loading.value = true
    try {
        const offset = currentPage.value * pageSize.value
        await fetchProjectsRange(offset, pageSize.value, true)
        const pageSizeChanged = await computePageSize()
        if (pageSizeChanged) {
            const newOffset = currentPage.value * pageSize.value
            if (newOffset !== offset) {
                await fetchProjectsRange(newOffset, pageSize.value, true)
            }
        }
    } catch (error) {
        console.error('加载数据失败:', error)
    } finally {
        loading.value = false
    }
}

async function resetAndLoad() {
    if (loading.value) return
    currentPage.value = 0
    clearCache()
    await computePageSize()
    await loadPageData()
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
    if (!scrollContainerRef.value || loading.value) return
    const container = scrollContainerRef.value
    const scrollTop = container.scrollTop
    const scrollHeight = container.scrollHeight
    const clientHeight = container.clientHeight
    if (scrollHeight <= clientHeight) return
    const bottomThreshold = 100
    const topThreshold = 50
    if (scrollDebounceTimer) clearTimeout(scrollDebounceTimer)
    scrollDebounceTimer = window.setTimeout(() => {
        if (scrollTop + clientHeight + bottomThreshold >= scrollHeight && currentPage.value < totalPages.value - 1) {
            goToNextPage()
        } else if (scrollTop <= topThreshold && currentPage.value > 0) {
            goToPrevPage()
        }
    }, 150)
}

async function goToNextPage() {
    if (currentPage.value < totalPages.value - 1 && !loading.value) {
        currentPage.value++
        await loadPageData()
        if (scrollContainerRef.value) scrollContainerRef.value.scrollTop = 0
    }
}

async function goToPrevPage() {
    if (currentPage.value > 0 && !loading.value) {
        currentPage.value--
        await loadPageData()
        if (scrollContainerRef.value) scrollContainerRef.value.scrollTop = scrollContainerRef.value.scrollHeight
    }
}

let resizeObserver: ResizeObserver | null = null

async function handleResize() {
    const changed = await computePageSize()
    if (changed) {
        currentPage.value = 0
        await loadPageData()
    }
}

// ---------- 标签横向滚动（拖拽 + 滚轮）无滚动条 ----------
const tagsScrollContainerRef = ref<HTMLElement | null>(null)
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

function animateButton(e: MouseEvent) {
    const el = e.currentTarget as HTMLElement | null;
    if(!el) return;
    el.classList.add('clicked');
    el.addEventListener('animationend', () => {
        el.classList.remove('clicked');
    }, { once: true });
}

onMounted(async () => {
    await loginStore.checkAuthStatus();
    if (loginStore.loggedIn) {
        await projectStore.getAllTags()
        availableTags.value = projectStore.allProjectTags
        activeTags.value = []
        await nextTick()
        await resetAndLoad();
        if (scrollContainerRef.value) scrollContainerRef.value.addEventListener('scroll', onScroll)
        window.addEventListener('resize', handleResize)
        if (gridContainerRef.value) {
            resizeObserver = new ResizeObserver(async () => {
                const changed = await computePageSize()
                if (changed) {
                    currentPage.value = 0
                    await loadPageData()
                }
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
        padding: 20px 28px;
        box-sizing: border-box;
        overflow-x: hidden;
        max-width: 100%;
    }
    
    .search-section {
        margin-bottom: 20px;
        display: flex;
        justify-content: center;
        width: 100%;
        
        .search-wrapper {
            width: 75vh;
            max-width: 100%;
        }
        
        .search-input {
            width: 100%;
            padding: 10px 16px;
            border: 1px solid #e4e7ed;
            border-radius: 24px;
            font-size: 14px;
            outline: none;
            transition: all 0.2s ease;
            background: white;
            box-sizing: border-box;
            
            &:focus {
                border-color: #409eff;
                box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
            }
        }
    }
    
    /* 筛选行布局：标题与内容同行 */
    .filter-row {
        display: flex;
        align-items: center;
        gap: 16px;
        width: 100%;
        margin-bottom: 20px;
        
        .filter-label {
            width: 80px;
            font-size: 14px;
            font-weight: 600;
            color: #303133;
            white-space: nowrap;
            flex-shrink: 0;
            letter-spacing: 0.3px;
            position: relative;
            padding-left: 8px;
            border-left: 3px solid #409eff;
        }
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
            gap: 10px;
            padding: 4px 0;
        }
        
        .tag-filter-btn {
            height: 34px;
            font-size: 13px;
            font-weight: 500;
            color: rgba(20, 20, 20, 0.8);
            padding: 0 16px;
            transition: all 0.2s ease;
            min-width: 70px;
            text-align: center;
            border-radius: 18px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #e4e7ed;
            cursor: pointer;
            white-space: nowrap;
            background-color: white;
            flex-shrink: 0;
            
            &:hover {
                background-color: #f0f2f5;
                border-color: #c0c4cc;
            }
            
            &.active {
                color: #ffffff;
                background-color: #409eff;
                border-color: #409eff;
                box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
            }
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
            height: 34px;
            font-size: 13px;
            font-weight: 500;
            color: rgba(20, 20, 20, 0.8);
            padding: 0 20px;
            border-radius: 18px;
            background: white;
            border: 1px solid #e4e7ed;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            white-space: nowrap;
            
            &:hover {
                background-color: #f0f2f5;
                border-color: #c0c4cc;
            }
            
            &.active {
                color: #ffffff;
                background-color: #409eff;
                border-color: #409eff;
                box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
            }
            
            &.clicked {
                animation: clickPulse 0.2s ease;
            }
        }
    }
    
    .projects-wrapper {
        flex: 1;
        overflow-y: auto;
        overflow-x: hidden;
        
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
        grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
        gap: 20px;
        align-items: start;
        justify-items: center;
        padding: 6px;
        min-height: 100%;
        
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
</style>