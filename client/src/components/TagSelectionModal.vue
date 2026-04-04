<!-- src/components/TagSelectionModal.vue -->
<script lang="ts" setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useProjectStore } from '@/stores/projectStore';
import { useModalStore } from '@/stores/modalStore';
import Tag from '@/components/Tag.vue';

const props = withDefaults(defineProps<{
  modalId?: string;
  initialTags?: string[];
  onConfirm?: (tags: string[]) => void;
}>(), {
  modalId: '',
  initialTags: () => [],
  onConfirm: (tags: string[]) => {}
});

const projectStore = useProjectStore();
const modalStore = useModalStore();

const selectedTags = ref<string[]>([...(props.initialTags || [])]);
const allTags = computed(() => projectStore.allProjectTags || []);
const searchQuery = ref<string>('');

const filteredTags = computed(() => {
  if (!searchQuery.value.trim()) return allTags.value;
  const keyword = searchQuery.value.trim().toLowerCase();
  return allTags.value.filter(tag => tag.toLowerCase().includes(keyword));
});

// 当前选中标签栏拖拽滚动相关
const selectedTagsScrollRef = ref<HTMLElement | null>(null);
let isDragging = false;
let startX = 0;
let scrollLeft = 0;

onMounted(() => {
  if (allTags.value.length === 0) {
    projectStore.getAllTags();
  }
  
  // 绑定拖拽滚动事件
  if (selectedTagsScrollRef.value) {
    selectedTagsScrollRef.value.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    selectedTagsScrollRef.value.addEventListener('wheel', onWheel, { passive: false });
    selectedTagsScrollRef.value.style.cursor = 'grab';
  }
});

onBeforeUnmount(() => {
  if (selectedTagsScrollRef.value) {
    selectedTagsScrollRef.value.removeEventListener('mousedown', onMouseDown);
    selectedTagsScrollRef.value.removeEventListener('wheel', onWheel);
  }
  window.removeEventListener('mousemove', onMouseMove);
  window.removeEventListener('mouseup', onMouseUp);
});

function onMouseDown(e: MouseEvent) {
  if (!selectedTagsScrollRef.value) return;
  // 避免在删除按钮上触发拖拽
  const target = e.target as HTMLElement;
  if (target.closest('.tag-remove')) return;
  
  isDragging = true;
  startX = e.pageX - selectedTagsScrollRef.value.offsetLeft;
  scrollLeft = selectedTagsScrollRef.value.scrollLeft;
  selectedTagsScrollRef.value.style.cursor = 'grabbing';
  selectedTagsScrollRef.value.style.userSelect = 'none';
  e.preventDefault();
}

function onMouseMove(e: MouseEvent) {
  if (!isDragging || !selectedTagsScrollRef.value) return;
  const x = e.pageX - selectedTagsScrollRef.value.offsetLeft;
  const walk = (x - startX) * 1.5;
  selectedTagsScrollRef.value.scrollLeft = scrollLeft - walk;
  e.preventDefault();
}

function onMouseUp() {
  if (!selectedTagsScrollRef.value) return;
  isDragging = false;
  selectedTagsScrollRef.value.style.cursor = 'grab';
  selectedTagsScrollRef.value.style.userSelect = '';
}

function onWheel(e: WheelEvent) {
  if (!selectedTagsScrollRef.value) return;
  if (e.deltaY !== 0) {
    e.preventDefault();
    selectedTagsScrollRef.value.scrollLeft += e.deltaY;
  }
}

function toggleTag(tag: string) {
  const index = selectedTags.value.indexOf(tag);
  if (index === -1) {
    selectedTags.value.push(tag);
  } else {
    selectedTags.value.splice(index, 1);
  }
}

function removeSelectedTag(tag: string) {
  const index = selectedTags.value.indexOf(tag);
  if (index !== -1) selectedTags.value.splice(index, 1);
}

function clearAllSelected() {
  selectedTags.value = [];
}

async function handleCreateTag() {
  const tagName = prompt('请输入新标签名称');
  if (!tagName?.trim()) return;
  const success = await projectStore.createTag(tagName.trim());
  if (success) {
    await projectStore.getAllTags();
    const newTag = tagName.trim();
    if (!selectedTags.value.includes(newTag)) {
      selectedTags.value.push(newTag);
    }
    searchQuery.value = '';
  }
}

function clearSearch() {
  searchQuery.value = '';
}

function confirmSelection() {
  props.onConfirm(selectedTags.value);
  modalStore.deactivateModal(props.modalId);
  modalStore.destroyModal(props.modalId);
}

function cancel() {
  modalStore.deactivateModal(props.modalId);
  modalStore.destroyModal(props.modalId);
}
</script>

<template>
  <div class="tag-selection-container">
    <!-- 搜索框 + 新建按钮行 -->
    <div class="search-and-new">
      <div class="search-wrapper">
        <i class="mdi mdi-magnify search-icon"></i>
        <input
          type="text"
          v-model="searchQuery"
          placeholder="搜索标签..."
          class="search-input"
        />
        <i
          v-if="searchQuery"
          class="mdi mdi-close clear-icon"
          @click="clearSearch"
          @keyup.enter="clearSearch"
          tabindex="0"
          role="button"
          aria-label="清除搜索"
        ></i>
      </div>
      <button class="create-tag-btn" @click="handleCreateTag">+ 新建标签</button>
    </div>

    <!-- 标签列表（可多选） -->
    <div class="tags-list">
      <div v-if="allTags.length === 0" class="empty-tips">暂无任何标签，请点击“+ 新建标签”创建</div>
      <template v-else>
        <Tag
          v-for="tag in filteredTags"
          :key="tag"
          :tag="{ content: tag }"
          :color="selectedTags.includes(tag) ? '#409eff' : undefined"
          class="tag-item"
          :class="{ 'tag-selected': selectedTags.includes(tag) }"
          @click="toggleTag(tag)"
          @keyup.enter="toggleTag(tag)"
          tabindex="0"
        />
        <div v-if="filteredTags.length === 0 && allTags.length > 0" class="empty-tips">未找到匹配的标签</div>
      </template>
    </div>

    <!-- 当前选中标签栏（支持拖拽滚动，无滚动条） -->
    <div class="selected-tags-section">
      <div class="section-header">
        <span class="section-title">当前选中标签</span>
        <button v-if="selectedTags.length" class="clear-all-btn" @click="clearAllSelected">
          <i class="mdi mdi-delete-outline"></i> 清空
        </button>
      </div>
      <div class="selected-tags-wrapper">
        <div ref="selectedTagsScrollRef" class="selected-tags-scroll">
          <Tag
            v-for="tag in selectedTags"
            :key="tag"
            :content="tag"
            :color="'#409eff'"
            class="selected-tag"
          >
            <template #action>
              <span class="tag-remove" @click.stop="removeSelectedTag(tag)">
                <i class="mdi mdi-close"></i>
              </span>
            </template>
          </Tag>
          <div v-if="selectedTags.length === 0" class="empty-selected">未选择任何标签</div>
        </div>
      </div>
    </div>

    <!-- 底部按钮：上下排列，风格与 CreateProject / UpdateProjectSetting 一致 -->
    <div class="button-container">
      <button class="button confirm-button" @click="confirmSelection">确定</button>
      <button class="button cancel" @click="cancel">取消</button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use "../common/global.scss" as *;

.tag-selection-container {
  width: 480px;
  max-width: 90vw;
  padding: 0 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 搜索框 + 新建按钮行 */
.search-and-new {
  display: flex;
  gap: 12px;
  align-items: center;

  .search-wrapper {
    flex: 1;
    position: relative;
    display: flex;
    align-items: center;

    .search-icon {
      position: absolute;
      left: 12px;
      font-size: 16px;
      color: #8c8f96;
      pointer-events: none;
    }

    .search-input {
      width: 100%;
      padding: 8px 30px 8px 32px;
      border: 1px solid #e2e6ea;
      border-radius: 24px;
      font-size: 13px;
      background-color: #ffffff;
      transition: all 0.2s;
      outline: none;

      &:focus {
        border-color: #409eff;
        box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
      }

      &::placeholder {
        color: #b4b8bf;
      }
    }

    .clear-icon {
      position: absolute;
      right: 12px;
      font-size: 16px;
      color: #8c8f96;
      cursor: pointer;
      padding: 4px;
      border-radius: 50%;
      transition: all 0.2s;

      &:hover {
        background-color: #f0f2f5;
        color: #5a5e66;
      }
    }
  }

  .create-tag-btn {
    background-color: #f0f2f5;
    border: none;
    padding: 6px 12px;
    border-radius: 24px;
    font-size: 12px;
    cursor: pointer;
    color: #2c3e50;
    transition: all 0.2s;
    white-space: nowrap;

    &:hover {
      background-color: #e4e7eb;
      transform: scale(1.02);
    }
  }
}

/* 标签列表区域 */
.tags-list {
  max-height: 260px;
  overflow-y: auto;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 4px 4px;
  border-top: 1px solid #eaeef2;
  border-bottom: 1px solid #eaeef2;
}

.tag-item {
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none;
  border-radius: 12px;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(2, 6, 23, 0.06);
  }

  &.tag-selected {
    box-shadow: 0 0 0 2px #409eff, 0 4px 12px rgba(64, 158, 255, 0.3);
    border-radius: 12px;
  }

  &:focus {
    box-shadow: 0 0 0 2px #66b1ff;
  }
}

.empty-tips {
  font-size: 13px;
  color: #909399;
  padding: 20px 0;
  text-align: center;
  width: 100%;
}

/* 当前选中标签栏 */
.selected-tags-section {
  margin-top: 4px;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;

    .section-title {
      font-size: 13px;
      font-weight: 500;
      color: #606266;
    }

    .clear-all-btn {
      background: none;
      border: none;
      font-size: 12px;
      color: #e74c3c;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 4px 8px;
      border-radius: 16px;
      transition: all 0.2s;

      &:hover {
        background-color: #fef0ef;
      }
    }
  }

  .selected-tags-wrapper {
    .selected-tags-scroll {
      display: flex;
      flex-wrap: nowrap;
      overflow-x: auto;
      gap: 8px;
      align-items: center;
      padding: 4px 0;
      cursor: grab;
      user-select: none;
      
      /* 隐藏滚动条 */
      scrollbar-width: none;
      -ms-overflow-style: none;
      &::-webkit-scrollbar {
        display: none;
      }
      
      &:active {
        cursor: grabbing;
      }

      .selected-tag {
        flex-shrink: 0;
        .tag-remove {
          margin-left: 6px;
          cursor: pointer;
          font-size: 14px;
          display: inline-flex;
          align-items: center;
          color: #e74c3c;
          opacity: 0.7;
          transition: opacity 0.2s;

          &:hover {
            opacity: 1;
          }
        }
      }

      .empty-selected {
        font-size: 12px;
        color: #c0c4cc;
        white-space: nowrap;
      }
    }
  }
}
.button-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
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
</style>