<script lang="ts" setup>
import {computed, ref, nextTick, onMounted, onBeforeUnmount} from 'vue';
import { Plus, Edit, Delete } from '@element-plus/icons-vue';
import { useProjectStore } from '@/stores/projectStore';
import { useModalStore } from '@/stores/modalStore';
import DeleteProject from './DeleteProject.vue';
import UpdateProjectSetting from './UpdateProjectSetting.vue';
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiPencil, mdiDelete } from '@mdi/js';

import { type TagInstance } from '@/types/tag';
import Tag from '@/components/Tag.vue';

const edit_path = mdiPencil;
const delete_path = mdiDelete;

const props = defineProps<{
    id: number,
    title?: string,
    thumb?: string | null,
    created_at?: number | string | null,
    updated_at?: number | string | null,
    tags?: string[],
    isCreate?: boolean,
    handleOpenExistingProject?: (id: number) => void,
    handleCreateNewProject?: () => void,
}>();

const thumbSrc = computed(() => {
    if (!props.thumb) return null
    if (props.thumb.startsWith('data:image')) {
        return props.thumb
    }
    return `data:image/png;base64,${props.thumb}`
})

const projectStore = useProjectStore();
const modalStore = useModalStore();
const cardRef = ref<HTMLDivElement | null>(null);

// 标签滚动容器引用
const tagsScrollRef = ref<HTMLElement | null>(null);
// 拖拽状态
let isDragging = false;
let startX = 0;
let scrollLeft = 0;

function parseDate(v: number | string | null | undefined) {
    if (!v) return null;
    const d = typeof v === 'number' ? new Date(v) : new Date(String(v));
    if (isNaN(d.getTime())) return null;
    return d;
}

function formatDate(v: number | string | null | undefined) {
    const d = parseDate(v);
    if (!d) return '';
    return new Intl.DateTimeFormat('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }).format(d);
}

function onCardClick() {
    if (props.id != null && props.id !== 0 && props.handleOpenExistingProject) {
        props.handleOpenExistingProject(props.id);
    } else if (props.handleCreateNewProject) {
        props.handleCreateNewProject();
    }
    nextTick(() => {
        cardRef.value?.blur();
    });
}

async function handleClickDelete(){
    cardRef.value?.blur();
    projectStore.toBeDeleted.id = props.id
    const modalWidth = 350;
    const modalHeight = 270;
    modalStore.createModal({
        id: 'delete-modal',
        title: "删除项目",
        isActive: true,
        isDraggable: false,
        isResizable: false,
        isModal: true,
        position: {
                x: (window.innerWidth - modalWidth) / 2,
                y: (window.innerHeight - modalHeight) / 2
        },
        size:{
            height: modalHeight,
            width: modalWidth
        },
        component: DeleteProject
    })
}

async function handleClickUpdate(){
    cardRef.value?.blur();
    await projectStore.getProjectSettings(props.id)
    projectStore.currentProjectId = props.id
    const modalWidth = 400;
    const modalHeight = 450;
    modalStore.createModal({
        id: 'update-modal',
        title: "更新项目",
        isActive: true,
        isDraggable: false,
        isResizable: false,
        isModal: true,
        position: {
                x: (window.innerWidth - modalWidth) / 2,
                y: (window.innerHeight - modalHeight) / 2
        },
        size:{
            height: modalHeight,
            width: modalWidth
        },
        component: UpdateProjectSetting
    })
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
    <div
        ref="cardRef"
        :class="['project-card', { 'new-card': props.id === 0 && props.handleCreateNewProject, 'placeholder-large': !props.thumb && !(props.id === 0 && props.handleCreateNewProject) } ]"
        role="button"
        :aria-label="props.title ?? (props.id ? `Project ${props.id}` : 'Create Project')"
        tabindex="0"
        @click="onCardClick"
        @keyup.enter="onCardClick"
    >
        <div class="project-thumb">
            <slot name="picture">
                <div class="thumb-content">
                    <template v-if="thumbSrc">
                        <img :src="thumbSrc" alt="thumb" class="thumb-img" />
                    </template>
                    <template v-else>
                        <div v-if="props.id === 0 && props.handleCreateNewProject" class="thumb-new">
                            <el-icon :size="40" color="#2c98da"><Plus/></el-icon>
                        </div>
                        <div v-else class="thumb-placeholder-large">{{ (props.title || '').charAt(0) || 'P' }}</div>
                    </template>
                </div>
            </slot>
            <div v-if="props.id !== 0" class="card-actions">
                <div @click.stop="handleClickUpdate" title="编辑" class="project-edit-btn project-action-btn">
                    <svg-icon type="mdi" :path="edit_path"></svg-icon>
                </div>
                <div @click.stop="handleClickDelete" title="删除" class="project-delete-btn project-action-btn">
                    <svg-icon type="mdi" :path="delete_path"></svg-icon>
                </div>
            </div>
        </div>

        <div class="project-info">
            <div class="project-title">{{ props.title ?? (props.id ? `Project ${props.id}` : 'New') }}</div>

            <!-- 标签区域：横向滚动 + 隐藏滚动条 + 鼠标拖拽滚动 -->
            <div class="project-tags">
                <div
                    ref="tagsScrollRef"
                    class="tags-scroll"
                >
                    <div class="tags-wrapper">
                        <!-- 正常卡片（非创建）有标签时显示标签列表 -->
                        <template v-if="props.tags?.length && !props.isCreate">
                            <Tag
                                v-for="tag in props.tags"
                                :key="tag"
                                :tag="{ content: tag }"
                                class="tag-item"
                            />
                        </template>
                        <!-- 正常卡片无标签时显示占位符 -->
                        <template v-else-if="!props.isCreate">
                            <span class="tag-placeholder">暂无标签</span>
                        </template>
                        <!-- 创建卡片时：显示不可见占位符，保持高度一致 -->
                        <template v-else>
                            <span class="tag-placeholder-invisible"></span>
                        </template>
                    </div>
                </div>
            </div>

            <!-- 统一元数据区域：正常卡片显示真实数据，创建卡片显示隐藏占位符（保持高度） -->
            <div class="project-meta" :class="{ 'invisible-meta': props.id === 0 && props.handleCreateNewProject }">
                <span class="meta-item">修改: {{ formatDate(props.updated_at) }}</span>
                <span class="meta-item">创建: {{ formatDate(props.created_at) }}</span>
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
    padding-top: 56.25%; /* 16:9 */
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
.card-actions{
    position: absolute;
    right: 8px;
    top: 8px;
    display: flex;
    gap: 4px;
    z-index: 5;
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
.thumb-new{
    width:100%;
    height:100%;
    display:flex;
    align-items:center;
    justify-content:center;
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
    gap:10px;
    font-size:12px;
    color:#6b7f8f;
}
.invisible-meta {
    visibility: hidden;
}
.project-tags {
    // margin: 4px 0;
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
.tag-placeholder-invisible {
    display: inline-block;
    width: 1px;
    height: 24px;
    visibility: hidden;
}
.project-action-btn{
    cursor: pointer;
    padding: 6px;
    border-radius: 6px;
    height: 100%;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    svg{
        width: 18px;
        height: 18px;
        color: rgba(0, 0, 0, 0.60);
    }
    &:hover {
        background-color: rgba(0, 0, 0, 0.05);
    }
}
.new-card{ border: 1px solid rgba(28,128,199,0.06); }
.meta-item{opacity:0.95}
@media (max-width: 480px){
    .project-card{ max-width: 100%; }
}
</style>