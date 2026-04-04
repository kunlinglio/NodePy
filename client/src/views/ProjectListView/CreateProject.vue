<!-- CreateProject.vue -->
<script lang="ts" setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useProjectStore } from '@/stores/projectStore';
import { useModalStore } from '@/stores/modalStore';
import { useUserStore } from '@/stores/userStore';
import { onUnmounted } from 'vue';
import Tag from '@/components/Tag.vue';
import TagSelectionModal from '@/components/TagSelectionModal.vue';

const projectStore = useProjectStore();
const modalStore = useModalStore();
const userStore = useUserStore();

const inputRef = ref<HTMLInputElement | null>(null);
const tagsScrollRef = ref<HTMLElement | null>(null);

// 拖拽状态
let isDragging = false;
let startX = 0;
let scrollLeft = 0;

// 临时标签列表（创建时为空）
const selectedTags = ref<string[]>([]);

// 添加标签到临时列表
function addTagToTemp(tag: string) {
  if (!selectedTags.value.includes(tag)) {
    selectedTags.value.push(tag);
    console.log(selectedTags.value);
  }
}

// 从临时列表删除标签
function removeTagFromTemp(tag: string) {
  const index = selectedTags.value.indexOf(tag);
  if (index !== -1) {
    selectedTags.value.splice(index, 1);
    console.log(selectedTags.value);
  }
}

// 打开标签选择弹窗
function openTagSelectionModal() {
  const modalId = 'create-tag-selection';
  // 避免重复打开
  if (modalStore.findModal(modalId)) return;

  modalStore.createModal({
    id: modalId,
    title: '选择标签',
    isActive: true,
    isDraggable: true,
    isResizable: false,
    isModal: true,
    position: {
      x: (window.innerWidth - 500) / 2,
      y: (window.innerHeight - 500) / 2,
    },
    size: { width: 500, height: 500 },
    component: TagSelectionModal,
    props: {
      modalId: modalId,
      initialTags: selectedTags.value,
      onConfirm: (newTags: string[]) => {
        selectedTags.value = newTags;
      },
    },
  });
}

// 鼠标拖拽滚动逻辑
function onMouseDown(e: MouseEvent) {
  if (!tagsScrollRef.value) return;
  // 避免在交互元素（如删除按钮）上触发拖拽
  const target = e.target as HTMLElement;
  if (target.closest('.tag-action') || target.closest('.add-tag-btn')) return;
  
  isDragging = true;
  startX = e.pageX - tagsScrollRef.value.offsetLeft;
  scrollLeft = tagsScrollRef.value.scrollLeft;
  tagsScrollRef.value.style.cursor = 'grabbing';
  tagsScrollRef.value.style.userSelect = 'none';
  e.preventDefault();
}

function onMouseMove(e: MouseEvent) {
  if (!isDragging || !tagsScrollRef.value) return;
  const x = e.pageX - tagsScrollRef.value.offsetLeft;
  const walk = (x - startX) * 1.5;
  tagsScrollRef.value.scrollLeft = scrollLeft - walk;
  e.preventDefault();
}

function onMouseUp() {
  if (!tagsScrollRef.value) return;
  isDragging = false;
  tagsScrollRef.value.style.cursor = 'grab';
  tagsScrollRef.value.style.userSelect = '';
}

function onWheel(e: WheelEvent) {
  if (!tagsScrollRef.value) return;
  if (e.deltaY !== 0) {
    e.preventDefault();
    tagsScrollRef.value.scrollLeft += e.deltaY;
  }
}

onMounted(() => {
  if (inputRef.value) {
    inputRef.value.focus();
  }
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

async function onCreateProject() {
  projectStore.currentProjectTags = selectedTags.value;
  const success = await projectStore.createProject();
  console.log(
    '创建项目:',
    projectStore.currentProjectName,
    '公开：',
    projectStore.currentWhetherShow,
    '标签:',
    projectStore.currentProjectTags,
    '结果:',
    success
  );
  if (success) {
    await projectStore.initializeProjects();
    await userStore.initializeUserInfo();
  }
  modalStore.deactivateModal('create-project');
  modalStore.destroyModal('create-project');
}

function onCancel() {
  modalStore.deactivateModal('create-project');
  modalStore.destroyModal('create-project');
}

onUnmounted(async () => {
  await projectStore.initializeProjects();
  await projectStore.getAllTags();
});
</script>

<template>
  <div class="create-project-container">
    <el-form class="create-project-form" label-position="top" @submit.prevent="onCreateProject">
      <el-form-item label="项目名称">
        <input
          ref="inputRef"
          class="name-input"
          placeholder="请输入项目名称"
          v-model="projectStore.currentProjectName"
          @keyup.enter="onCreateProject"
        />
      </el-form-item>

      <el-form-item label="公开项目">
        <label class="checkbox-container">
          <input type="checkbox" class="custom-checkbox" v-model="projectStore.currentWhetherShow" />
          <span class="checkmark"></span>
        </label>
      </el-form-item>

      <!-- 标签管理区域：加号固定在左侧，标签列表可滚动 -->
      <div class="tags-section">
        <div class="section-title">当前项目标签</div>
        <div class="current-tags-wrapper">
          <div class="tags-row">
            <div class="add-tag-btn" @click="openTagSelectionModal">
              <span>+</span>
            </div>
            <div ref="tagsScrollRef" class="tags-scroll-container">
              <Tag
                v-for="tag in selectedTags"
                :key="tag"
                :content="tag"
              >
                <template #action>
                  <span class="tag-action remove" @click.stop="removeTagFromTemp(tag)">✕</span>
                </template>
              </Tag>
              <div v-if="selectedTags.length === 0" class="empty-tips">暂无标签</div>
            </div>
          </div>
        </div>
      </div>
    </el-form>

    <div class="button-container">
      <button class="button confirm-button" @click="onCreateProject">创建</button>
      <button class="button cancel" @click="onCancel">取消</button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use "../../common/global.scss" as *;

.create-project-container {
  display: flex;
  flex-direction: column;
  width: 300px;
  padding-bottom: 5px;
}

.create-project-form {
  margin-bottom: 20px;
}

.button-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.name-input {
  @include input-style;
}
.name-input:focus {
  @include input-focus-style;
}

.button {
  width: 100%;
}
.button.cancel {
  margin-top: 10px;
  margin-left: 0;
  @include cancel-button-style;
}
.button.cancel:hover {
  @include cancel-button-hover-style;
}
.button.confirm-button {
  width: 100%;
  @include confirm-button-style;
}
.button.confirm-button:hover {
  @include confirm-button-hover-style;
}

.tags-section {
  margin-top: 16px;
  .section-title {
    font-size: 14px;
    font-weight: 500;
    margin: 12px 0 8px;
    color: #606266;
  }
}

.current-tags-wrapper {
  .tags-row {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .add-tag-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background-color: #ecf5ff;
    color: #409eff;
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
    flex-shrink: 0;
    transition: all 0.2s;
    &:hover {
      background-color: #d9ecff;
      transform: scale(1.05);
    }
  }

  .tags-scroll-container {
    flex: 1;
    overflow-x: auto;
    overflow-y: hidden;
    white-space: nowrap;
    scrollbar-width: none;
    -ms-overflow-style: none;
    &::-webkit-scrollbar {
      display: none;
    }
    display: flex;
    gap: 8px;
    align-items: center;
    cursor: grab;
    &:active {
      cursor: grabbing;
    }
    user-select: none;
    
    > * {
      flex-shrink: 0;
    }
  }
}

.tag-action {
  margin-left: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  &.remove {
    color: #e74c3c;
  }
}

.empty-tips {
  font-size: 12px;
  color: #909399;
  padding: 4px 0;
  white-space: nowrap;
}
</style>