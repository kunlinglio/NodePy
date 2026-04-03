<script lang="ts" setup>
    import { useUserStore } from '@/stores/userStore';
    import type { ExploreListItem } from '@/utils/api';
    import Tag from '@/components/Tag.vue';
    import { computed, onMounted, onBeforeUnmount, ref } from 'vue';
    import { useRouter } from 'vue-router';

    const props = defineProps<{
        item: ExploreListItem
    }>()

    const router = useRouter()
    const userStore = useUserStore()

    // 标签滚动容器引用
    const tagsScrollRef = ref<HTMLElement | null>(null);
    // 拖拽状态
    let isDragging = false;
    let startX = 0;
    let scrollLeft = 0;

    const thumbSrc = computed(() => {
        if (!props.item.thumb) return null
        if (props.item.thumb.startsWith('data:image')) {
            return props.item.thumb
        }
        return `data:image/png;base64,${props.item.thumb}`
    })

    function parseDate(v: number | null) {
        if (!v) return null;
        const d = new Date(v);
        if (isNaN(d.getTime())) return null;
        return d;
    }

    function formatDate(v: number | null) {
        const d = parseDate(v);
        if (!d) return '';
        return new Intl.DateTimeFormat('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        }).format(d);
    }

    async function handleOpenExample(){
        const route = router.resolve({
            name: 'editor-example',
            params: { projectId: props.item.project_id }
        });
        window.open(route.href, '_blank');
    }

    function handleCopy(){
        // TODO: 实现复制功能
    }

    // 鼠标拖拽滚动逻辑
    function onMouseDown(e: MouseEvent) {
        if (!tagsScrollRef.value) return;
        isDragging = true;
        startX = e.pageX - tagsScrollRef.value.offsetLeft;
        scrollLeft = tagsScrollRef.value.scrollLeft;
        tagsScrollRef.value.style.cursor = 'grabbing';
        e.preventDefault();
    }

    function onMouseMove(e: MouseEvent) {
        if (!isDragging || !tagsScrollRef.value) return;
        const x = e.pageX - tagsScrollRef.value.offsetLeft;
        const walk = (x - startX) * 1.5;
        tagsScrollRef.value.scrollLeft = scrollLeft - walk;
        e.preventDefault();
    }

    function onMouseUp(e: MouseEvent) {
        if (!tagsScrollRef.value) return;
        isDragging = false;
        tagsScrollRef.value.style.cursor = 'grab';
    }

    function onWheel(e: WheelEvent) {
        if (!tagsScrollRef.value) return;
        if (e.deltaY !== 0) {
            e.preventDefault();
            tagsScrollRef.value.scrollLeft += e.deltaY;
        }
    }

    onMounted(() => {
        if (tagsScrollRef.value) {
            tagsScrollRef.value.addEventListener('mousedown', onMouseDown);
            window.addEventListener('mousemove', onMouseMove);
            window.addEventListener('mouseup', onMouseUp);
            tagsScrollRef.value.addEventListener('wheel', onWheel, { passive: false });
            tagsScrollRef.value.style.cursor = 'grab';
        }
    });

    onBeforeUnmount(() => {
        if (tagsScrollRef.value) {
            tagsScrollRef.value.removeEventListener('mousedown', onMouseDown);
            tagsScrollRef.value.removeEventListener('wheel', onWheel);
        }
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
    });
</script>
<template>
    <div class="project-card" @click="handleOpenExample">
        <div class="project-thumb">
            <div class="thumb-content">
                <template v-if="thumbSrc">
                    <img :src="thumbSrc" alt="thumb" class="thumb-img" />
                </template>
                <template v-else>
                    <div class="thumb-placeholder-large">{{ (props.item.project_name || '').charAt(0) || 'E' }}</div>
                </template>
            </div>
        </div>

        <div class="project-info">
            <div class="project-title">{{ item.project_name }}</div>

            <!-- 标签区域：横向滚动 + 隐藏滚动条 + 鼠标拖拽滚动 -->
            <div class="project-tags">
                <div
                    ref="tagsScrollRef"
                    class="tags-scroll"
                >
                    <div class="tags-wrapper">
                        <template v-if="item.tags && item.tags.length">
                            <Tag
                                v-for="tag in item.tags"
                                :key="tag"
                                :tag="{ content: tag }"
                                class="tag-item"
                            />
                        </template>
                        <span v-else class="tag-placeholder">暂无标签</span>
                    </div>
                </div>
            </div>

            <div class="project-meta">
                <div class="meta-item-row">
                    <span class="meta-item">修改: {{ formatDate(item.updated_at) }}</span>
                    <span class="meta-item">创建: {{ formatDate(item.created_at) }}</span>
                </div>
                <div class="meta-item-row">
                    <span class="meta-item">作者: {{ item.owner_name }}</span>
                </div>
            </div>
        </div>
    </div>
</template>
<style lang="scss" scoped>
.project-card{
    width: 100%;
    max-width: 420px;
    background: #ffffff;
    border-radius: 12px;
    color: #1f2d3d;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    cursor: pointer;
    box-shadow: 0 6px 25px rgba(31,45,61,0.08);
    transition: transform 140ms cubic-bezier(.2,.9,.3,1), box-shadow 140ms cubic-bezier(.2,.9,.3,1);
}
.project-card:focus{
    outline: 2px solid rgba(26,115,190,0.12);
    outline-offset: 2px;
}
.project-card:hover{
    transform: translateY(-4px) scale(1.015);
    box-shadow: 0 12px 28px rgba(31,45,61,0.12);
}
.project-thumb{
    position: relative;
    width: 100%;
    padding-top: 56.25%;
    display: block;
    background: #f6f9fb;
}
.thumb-content{
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}
.thumb-content > img.thumb-img{
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
}
.thumb-img{
    width:100%;
    height:100%;
    object-fit:cover;
}
.thumb-placeholder-large{
    width:100%;
    height:100%;
    display:flex;
    align-items:center;
    justify-content:center;
    color: #4b5d6a;
    font-size:48px;
    font-weight:700;
}
.project-info{
    padding: 14px 16px;
    display:flex;
    flex-direction:column;
    // gap:6px;
}
.project-title{
    font-weight:700;
    font-size:15px;
    color:#102335;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}
.project-meta{
    display:flex;
    flex-direction: column;
    gap:5px;
    font-size:12px;
    color:#6b7f8f;
}
.project-tags {
    margin: 4px 0;
    height: 32px;
    overflow: visible;
}
.tags-scroll {
    overflow-x: auto;
    overflow-y: hidden;
    white-space: nowrap;
    height: 100%;
    scrollbar-width: none;
    -ms-overflow-style: none;
    &::-webkit-scrollbar {
        display: none;
    }
    user-select: none;
    cursor: grab;
    &:active {
        cursor: grabbing;
    }
}
.tags-wrapper {
    display: inline-flex;
    gap: 8px;
    align-items: center;
    height: 100%;
    padding-right: 4px;
}
.tag-item {
    flex-shrink: 0;
}
.tag-placeholder {
    display: inline-block;
    font-size: 12px;
    color: #8a9aa8;
    line-height: 32px;
}
.meta-item{opacity:0.95}
.meta-item-row{
    display:flex;
    gap:10px;
}

@media (max-width: 480px){
    .project-card{ max-width: 100%; }
}
</style>