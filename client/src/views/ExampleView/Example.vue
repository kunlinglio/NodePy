<script lang="ts" setup>
    import { useRouter } from 'vue-router'
    import { ref, onMounted, onBeforeUnmount, computed, watch, nextTick } from 'vue';
    import AuthenticatedServiceFactory from '@/utils/AuthenticatedServiceFactory';
    import { useLoginStore } from '@/stores/loginStore'
    import Mask from '@/views/Mask.vue'
    import ExampleDemoFrame from './ExampleDemoFrame.vue';
    import { handleNetworkError } from '@/utils/networkError';
    import { ApiError } from '@/utils/api';
    import notify from '@/components/Notification/notify';
    import { ProjectListFilter, type ExploreListItem } from '@/utils/api';
    import SvgIcon from '@jamescoyle/vue-icon';
    import { mdiMenuDown, mdiMenuUp } from '@mdi/js';
    import { useProjectStore } from '@/stores/projectStore';

    const loginStore = useLoginStore();
    const projectStore = useProjectStore();
    const router = useRouter()
    const authService = AuthenticatedServiceFactory.getService()

    // 枚举常量，供模板使用
    const OrderedBy = ProjectListFilter.ordered_by;

    // 静态配置
    const default_tags: string[] = ['默认标签1', '默认标签2', '默认标签3', '默认标签4', '默认标签5']

    const availableTags = ref<string[]>(default_tags)
    onMounted(async () => {
        await projectStore.getAllTags()
        availableTags.value = projectStore.allProjectTags
    })
    
    // 项目列表（当前页项目）
    const projects = ref<ExploreListItem[]>([])
    const totalCount = ref<number>(0)
    const loading = ref<boolean>(false)
    
    // 多选标签状态
    const activeTags = ref<string[]>([])
    const searchKeyword = ref<string>('')
    const searchInput = ref<string>('')
    const sortBy = ref<ProjectListFilter.ordered_by>(OrderedBy.CREATED_AT)
    
    // 分页相关状态
    const currentPage = ref<number>(0)           // 当前页码，从0开始
    const pageSize = ref<number>(20)             // 动态计算的每页数量
    const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))
    
    // 滚动防抖标志
    let scrollDebounceTimer: number | null = null
    
    // 缓存相关
    interface CacheKey {
        tags: string[]
        search: string
        sort: ProjectListFilter.ordered_by
        offset: number
        limit: number
    }
    
    const dataCache = new Map<string, ExploreListItem[]>()
    
    // 生成缓存键
    function getCacheKey(offset: number, limit: number): string {
        return JSON.stringify({
            tags: activeTags.value.sort(),
            search: searchKeyword.value,
            sort: sortBy.value,
            offset,
            limit
        })
    }
    
    // 清空缓存
    function clearCache() {
        dataCache.clear()
    }
    
    // 动态计算每页可显示的项目数量
    const gridContainerRef = ref<HTMLElement | null>(null)
    const cardHeight = ref<number>(280) // 默认卡片高度，后续动态测量
    
    async function computePageSize() {
        await nextTick()
        if (!gridContainerRef.value) return
        
        const container = gridContainerRef.value
        const containerHeight = container.clientHeight
        if (containerHeight === 0) return
        
        // 获取第一张卡片的高度（如果有的话）
        const firstCard = container.querySelector('.example-card') as HTMLElement
        if (firstCard) {
            const rect = firstCard.getBoundingClientRect()
            const style = getComputedStyle(firstCard)
            const marginBottom = parseFloat(style.marginBottom) || 0
            cardHeight.value = rect.height + marginBottom
        }
        
        // 计算每行卡片数量
        const containerWidth = container.clientWidth
        const cardMinWidth = 260 // 与CSS中的min-width一致
        const gap = 20 // gap值
        const cols = Math.floor((containerWidth + gap) / (cardMinWidth + gap))
        
        // 计算可显示的行数
        const rows = Math.floor(containerHeight / cardHeight.value)
        
        // 计算每页数量，至少为1
        const newPageSize = Math.max(1, rows * cols)
        
        if (newPageSize !== pageSize.value) {
            pageSize.value = newPageSize
            // 页面大小改变时，重置当前页码并重新加载
            currentPage.value = 0
            await loadPageData()
        }
    }
    
    // 通用请求函数：根据偏移量和限制获取数据
    async function fetchProjectsRange(offset: number, limit: number, updateTotal: boolean = true) {
        const filterConditions: ProjectListFilter = {
            tags: activeTags.value,
            search_keyword: searchKeyword.value,
            ordered_by: sortBy.value,
            ranging: [offset, limit]
        }
        
        const cacheKey = getCacheKey(offset, limit)
        
        // 检查缓存
        if (dataCache.has(cacheKey)) {
            const cachedData = dataCache.get(cacheKey)!
            projects.value = cachedData
            return
        }
        
        try {
            const response = await authService.getExploreProjectsApiExploreProjectsGet(filterConditions) as any;
            const newProjects = response.projects || [];
            const newTotal = response.total ?? 0;
            
            // 存入缓存
            dataCache.set(cacheKey, newProjects)
            
            // 更新项目列表
            projects.value = newProjects
            
            // 更新总数（仅在需要时）
            if (updateTotal) {
                totalCount.value = newTotal
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
    
    // 加载当前页数据
    async function loadPageData() {
        if (loading.value) return
        
        loading.value = true
        try {
            const offset = currentPage.value * pageSize.value
            await fetchProjectsRange(offset, pageSize.value, true)
        } catch (error) {
            console.error('加载数据失败:', error)
        } finally {
            loading.value = false
        }
    }
    
    // 重置所有筛选条件，重新加载第一页
    async function resetAndLoad() {
        if (loading.value) return
        
        // 重置页码
        currentPage.value = 0
        // 清空缓存
        clearCache()
        
        // 重新计算页面大小后再加载
        await computePageSize()
        await loadPageData()
    }
    
    // 处理标签点击（多选）
    function handleTagClick(tag: string) {
        const index = activeTags.value.indexOf(tag)
        if (index === -1) {
            activeTags.value.push(tag)
        } else {
            activeTags.value.splice(index, 1)
        }
        resetAndLoad()
    }
    
    // 处理搜索输入（防抖）
    function handleSearchInput(value: string) {
        if (scrollDebounceTimer) clearTimeout(scrollDebounceTimer);
        scrollDebounceTimer = window.setTimeout(() => {
            searchKeyword.value = value;
            resetAndLoad();
        }, 300);
    }
    
    // 处理排序变更
    function handleSortChange(value: ProjectListFilter.ordered_by) {
        if (sortBy.value === value) return;
        sortBy.value = value;
        resetAndLoad();
    }
    
    // 滚动容器引用
    const scrollContainerRef = ref<HTMLElement | null>(null)
    let isScrolling = false
    
    // 滚动监听（实现分页切换）
    function onScroll() {
        if (!scrollContainerRef.value || loading.value) return
        
        const container = scrollContainerRef.value
        const scrollTop = container.scrollTop
        const scrollHeight = container.scrollHeight
        const clientHeight = container.clientHeight
        
        // 滚动到底部阈值（100px）
        const bottomThreshold = 100
        // 滚动到顶部阈值（50px）
        const topThreshold = 50
        
        // 防抖处理，避免频繁调用
        if (scrollDebounceTimer) clearTimeout(scrollDebounceTimer)
        
        scrollDebounceTimer = window.setTimeout(() => {
            // 检查是否需要加载下一页
            if (scrollTop + clientHeight + bottomThreshold >= scrollHeight && 
                currentPage.value < totalPages.value - 1) {
                goToNextPage()
            }
            // 检查是否需要加载上一页
            else if (scrollTop <= topThreshold && currentPage.value > 0) {
                goToPrevPage()
            }
        }, 150)
    }
    
    // 前往下一页
    async function goToNextPage() {
        if (currentPage.value < totalPages.value - 1 && !loading.value) {
            currentPage.value++
            await loadPageData()
            // 滚动到顶部
            if (scrollContainerRef.value) {
                scrollContainerRef.value.scrollTop = 0
            }
        }
    }
    
    // 前往上一页
    async function goToPrevPage() {
        if (currentPage.value > 0 && !loading.value) {
            currentPage.value--
            await loadPageData()
            // 滚动到底部
            if (scrollContainerRef.value) {
                scrollContainerRef.value.scrollTop = scrollContainerRef.value.scrollHeight
            }
        }
    }
    
    // 跳转到指定页
    async function goToPage(page: number) {
        if (page === currentPage.value || loading.value) return
        if (page >= 0 && page < totalPages.value) {
            currentPage.value = page
            await loadPageData()
            // 滚动到顶部
            if (scrollContainerRef.value) {
                scrollContainerRef.value.scrollTop = 0
            }
        }
    }
    
    // ========== 修改点 1：visibleDots 无数据时返回 [0] ==========
    const visibleDots = computed(() => {
        const total = totalPages.value
        if (total === 0) {
            return [0]  // 至少显示一个圆点
        }
        
        const maxDots = 5
        const current = currentPage.value
        
        if (total <= maxDots) {
            return Array.from({ length: total }, (_, i) => i)
        }
        
        // 计算起始和结束索引，让当前页居中
        let start = Math.max(0, current - Math.floor(maxDots / 2))
        let end = start + maxDots
        
        if (end > total) {
            end = total
            start = Math.max(0, end - maxDots)
        }
        
        return Array.from({ length: end - start }, (_, i) => start + i)
    })
    // ========== 修改点 1 结束 ==========
    
    // 窗口大小变化时重新计算每页数量
    let resizeObserver: ResizeObserver | null = null
    
    // 监听滚动容器
    onMounted(async () => {
        await loginStore.checkAuthStatus();
        if (loginStore.loggedIn) {
            // ========== 修改点 2：默认选中第一个标签 ==========
            if (default_tags.length > 0) {
                activeTags.value = [default_tags[0]!];
            } else {
                activeTags.value = [];
            }
            // ========== 修改点 2 结束 ==========
            
            // 重置并加载数据（内部会计算页面大小、清缓存等）
            await resetAndLoad();
            
            // 设置滚动监听
            if (scrollContainerRef.value) {
                scrollContainerRef.value.addEventListener('scroll', onScroll)
            }
            
            // 监听窗口大小变化
            window.addEventListener('resize', handleResize)
            
            // 使用 ResizeObserver 监听网格容器大小变化
            if (gridContainerRef.value) {
                resizeObserver = new ResizeObserver(() => {
                    computePageSize()
                })
                resizeObserver.observe(gridContainerRef.value)
            }
        } else {
            router.replace({ name: 'login' });
        }
    });
    
    function handleResize() {
        computePageSize()
    }
    
    onBeforeUnmount(() => {
        if (scrollContainerRef.value) {
            scrollContainerRef.value.removeEventListener('scroll', onScroll)
        }
        window.removeEventListener('resize', handleResize)
        if (resizeObserver) {
            resizeObserver.disconnect()
        }
        if (scrollDebounceTimer) clearTimeout(scrollDebounceTimer);
    });
    
    // 排序下拉菜单状态
    const showSortMenu = ref(false)
    const sortMenuRef = ref<HTMLElement | null>(null)
    
    const sortLabelMap: Record<ProjectListFilter.ordered_by, string> = {
        [OrderedBy.CREATED_AT]: '按创建时间排序',
        [OrderedBy.UPDATED_AT]: '按更新时间排序',
        [OrderedBy.PROJECT_NAME]: '按项目名称排序',
        [OrderedBy.OWNER]: '按所有者排序'
    }
    
    // 全局点击关闭排序菜单
    const onGlobalClick = (e: MouseEvent) => {
        if (!showSortMenu.value) return
        const el = sortMenuRef.value
        if (!el) return
        const target = e.target as Node
        if (el.contains(target)) return
        showSortMenu.value = false
    }
    
    // 动画效果
    function animateButton(e: MouseEvent) {
        const el = (e.currentTarget as HTMLElement | null);
        if(!el) return;
        el.classList.add('clicked');
        el.addEventListener('animationend', () => {
            el.classList.remove('clicked');
        }, { once: true });
    }
    
    onMounted(() => {
        document.addEventListener('click', onGlobalClick)
    })
    
    onBeforeUnmount(() => {
        document.removeEventListener('click', onGlobalClick)
    })
</script>

<template>
    <div class="example-container" v-if="loginStore.loggedIn">
        <div class="example-content">
            <!-- 搜索框和筛选区域 -->
            <div class="search-section">
                <div class="search-wrapper">
                    <input
                        type="text"
                        v-model="searchInput"
                        @input="handleSearchInput(searchInput)"
                        placeholder="搜索项目..."
                        class="search-input"
                    />
                </div>
            </div>

            <!-- 标签栏 + 右侧排序控件 -->
            <div class="tag-filter-container">
                <div class="filter">
                    <div class="tab-list" role="tablist">
                        <button
                            v-for="tag in default_tags"
                            :key="tag"
                            class="tab-item"
                            :class="{ active: activeTags.includes(tag) }"
                            @click="handleTagClick(tag)"
                            role="tab"
                            :aria-selected="activeTags.includes(tag)"
                        >
                            <span class="tab-title">{{ tag }}</span>
                        </button>
                    </div>
                </div>
                <div class="filter-options">
                    <div class="sort-dropdown" ref="sortMenuRef">
                        <button class="sort-btn" type="button" @click="(e) => { animateButton(e); showSortMenu = !showSortMenu }" aria-haspopup="true" :aria-expanded="showSortMenu">
                            <div class="sort-text">{{ sortLabelMap[sortBy] }}</div>
                            <SvgIcon type="mdi" :path="showSortMenu ? mdiMenuUp : mdiMenuDown" class="btn-icon" />
                        </button>

                        <div v-if="showSortMenu" class="sort-menu">
                            <ul class="menu-list">
                                <li class="menu-item" @click="() => { handleSortChange(OrderedBy.CREATED_AT); showSortMenu = false }">按创建时间排序</li>
                                <li class="menu-item" @click="() => { handleSortChange(OrderedBy.UPDATED_AT); showSortMenu = false }">按更新时间排序</li>
                                <li class="menu-item" @click="() => { handleSortChange(OrderedBy.PROJECT_NAME); showSortMenu = false }">按项目名称排序</li>
                                <li class="menu-item" @click="() => { handleSortChange(OrderedBy.OWNER); showSortMenu = false }">按所有者排序</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 项目网格容器，带滚动 -->
            <div class="projects-wrapper" ref="scrollContainerRef">
                <div class="examples-grid" ref="gridContainerRef">
                    <!-- 加载状态 -->
                    <div v-if="loading" class="loading-state">加载中...</div>
                    
                    <!-- 无数据提示 -->
                    <div v-else-if="projects.length === 0" class="empty-state">
                        <div class="empty-info">暂无项目</div>
                    </div>
                    
                    <!-- 项目卡片 -->
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
        
        <!-- ========== 修改点 3：圆点导航显示条件改为 visibleDots 长度大于 0 ========== -->
        <div class="dot-navigation" v-if="visibleDots.length > 0">
            <div
                v-for="page in visibleDots"
                :key="page"
                class="dot"
                :class="{ active: page === currentPage, large: page === currentPage }"
                @click="goToPage(page)"
            ></div>
        </div>
        <!-- ========== 修改点 3 结束 ========== -->
    </div>
    <Mask v-else />
</template>

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
    }
    
    .example-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        padding: 20px 28px;
        box-sizing: border-box;
        overflow: hidden;
    }
    
    /* 搜索框区域 */
    .search-section {
        margin-bottom: 20px;
        display: flex;
        justify-content: center;
        
        .search-wrapper {
            width: 320px;
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
            
            &:focus {
                border-color: #409eff;
                box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
            }
        }
    }
    
    /* 标签栏 + 右侧排序 */
    .tag-filter-container {
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
        
        .filter {
            flex: 1;
            min-width: 0;
        }
        
        .filter-options {
            display: flex;
            gap: 12px;
            align-items: center;
        }
        
        .tab-list {
            display: flex;
            gap: 10px;
            margin: 0;
            align-items: flex-start;
            justify-content: flex-start;
            overflow-x: auto;
            overflow-y: hidden;
            padding: 8px 0px 0px 0px;
            flex-wrap: wrap;
            
            &::-webkit-scrollbar {
                height: 6px;
            }
            
            &::-webkit-scrollbar-thumb {
                background: rgba(0,0,0,0.08);
                border-radius: 3px;
            }
        }
        
        .tab-item {
            height: 34px;
            font-size: 13px;
            font-weight: 500;
            color: rgba(20, 20, 20, 0.8);
            padding: 6px 16px;
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
            
            .tab-title {
                display: inline-block;
                overflow: hidden;
                text-overflow: ellipsis;
            }
        }
    }
    
    /* 排序下拉菜单样式 */
    .sort-dropdown {
        position: relative;
    }
    
    .sort-btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 12px;
        border-radius: 8px;
        background: white;
        cursor: pointer;
        border: 1px solid #e4e7ed;
        transition: all 0.2s ease;
        
        &:hover {
            background-color: #f0f2f5;
            border-color: #c0c4cc;
        }
        
        &.clicked {
            animation: clickPulse 0.2s ease;
        }
        
        .btn-icon {
            width: 20px;
            height: 20px;
            color: rgba(0,0,0,0.65);
        }
        
        .sort-text {
            font-size: 13px;
            color: rgba(0,0,0,0.8);
            font-weight: 500;
        }
    }
    
    .sort-menu {
        position: absolute;
        right: 0;
        margin-top: 8px;
        z-index: 1000;
        min-width: 160px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        padding: 4px;
        animation: menuFadeIn 0.2s ease;
        
        .menu-list {
            list-style: none;
            margin: 0;
            padding: 0;
        }
        
        .menu-item {
            padding: 8px 12px;
            cursor: pointer;
            border-radius: 6px;
            font-size: 13px;
            color: rgba(0,0,0,0.8);
            transition: background-color 0.2s;
            
            &:hover {
                background-color: #f0f2f5;
            }
        }
    }
    
    @keyframes menuFadeIn {
        from {
            opacity: 0;
            transform: translateY(-8px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* 项目列表滚动容器 */
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
    
    /* 项目网格 */
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
    
    /* 右侧圆点导航 */
    .dot-navigation {
        position: fixed;
        right: 20px;
        top: 50%;
        transform: translateY(-50%);
        display: flex;
        flex-direction: column;
        gap: 12px;
        z-index: 100;
        background: rgba(255, 255, 255, 0.9);
        padding: 12px 8px;
        border-radius: 30px;
        backdrop-filter: blur(4px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        
        .dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #c0c4cc;
            cursor: pointer;
            transition: all 0.2s ease;
            
            &:hover {
                background-color: #909399;
                transform: scale(1.2);
            }
            
            &.active {
                background-color: #409eff;
            }
            
            &.large {
                width: 12px;
                height: 12px;
                background-color: #409eff;
                box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
            }
        }
    }
    
    /* 响应式调整 */
    @media (max-width: 768px) {
        .example-content {
            padding: 16px;
        }
        
        .tag-filter-container {
            .tab-item {
                min-width: 60px;
                padding: 4px 12px;
                font-size: 12px;
            }
        }
        
        .dot-navigation {
            right: 10px;
            gap: 8px;
            padding: 8px 6px;
            
            .dot {
                width: 6px;
                height: 6px;
                
                &.large {
                    width: 10px;
                    height: 10px;
                }
            }
        }
    }
</style>