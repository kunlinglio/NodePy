<!-- src/components/TagSelectionModal.vue -->
<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue';
import { useProjectStore } from '@/stores/projectStore';
import { useModalStore } from '@/stores/modalStore';
import Tag from '@/components/Tag.vue';

const props = withDefaults(defineProps<{
  modalId?: string;                // 由父组件传入当前模态框的ID
  initialTags?: string[];         // 当前项目已有的标签
  onConfirm?: (tags: string[]) => void;  // 确认回调
}>(), {
  modalId: '',
  initialTags: () => [],
  onConfirm: (tags: string[]) => {}
});

const projectStore = useProjectStore();
const modalStore = useModalStore();

const selectedTags = ref<string[]>([...(props.initialTags || [])]);
const allTags = computed(() => projectStore.allProjectTags || []);

// 若标签列表为空，尝试加载
onMounted(() => {
  if (allTags.value.length === 0) {
    projectStore.getAllTags();
  }
});

function toggleTag(tag: string) {
  const index = selectedTags.value.indexOf(tag);
  if (index === -1) {
    selectedTags.value.push(tag);
  } else {
    selectedTags.value.splice(index, 1);
  }
}

function selectAll() {
  selectedTags.value = [...allTags.value];
}

function clearAll() {
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
  }
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
    <!-- <div class="header">
      <h3>管理项目标签</h3>
      <div class="batch-actions">
        <button class="batch-btn" @click="selectAll">全选</button>
        <button class="batch-btn" @click="clearAll">清空</button>
      </div>
    </div> -->

    <!-- 新建标签按钮行 -->
    <div class="new-tag-bar">
      <button class="create-tag-btn" @click="handleCreateTag">+ 新建标签</button>
    </div>

    <!-- 标签列表：使用 Tag 组件展示，通过 action 插槽显示选中标记 -->
    <div class="tags-list">
        <Tag
          v-for="tag in allTags"
          :key="tag"
          :tag="{ content: tag }"
          class="tag-item"
          :class="{ selected: selectedTags.includes(tag) }"
          @click="toggleTag(tag)"
          @keyup.enter="toggleTag(tag)"
          tabindex="0"
        >
          <template #action>
            <span v-if="selectedTags.includes(tag)" class="check-mark">✓</span>
          </template>
        </Tag>
      <div v-if="allTags.length === 0" class="empty-tips">暂无任何标签，请点击“+ 新建标签”创建</div>
    </div>

    <!-- 底部按钮：模仿 CreateProject 的确认/取消布局，上下排列 -->
    <div class="action-buttons">
      <button class="confirm-btn" @click="confirmSelection">确定</button>
      <button class="cancel-btn" @click="cancel">取消</button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.tag-selection-container {
  width: 480px;
  max-width: 90vw;
  padding: 0 20px;           /* 左右内边距 */
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: #1f2d3d;
  }
  .batch-actions {
    display: flex;
    gap: 12px;
    .batch-btn {
      background: none;
      border: none;
      color: #409eff;
      cursor: pointer;
      font-size: 13px;
      &:hover {
        text-decoration: underline;
      }
    }
  }
}

.new-tag-bar {
  display: flex;
  justify-content: flex-start;
  .create-tag-btn {
    background-color: #f0f2f5;
    border: none;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    cursor: pointer;
    color: #2c3e50;
    transition: all 0.2s;
    &:hover {
      background-color: #e4e7eb;
      transform: scale(1.02);
    }
  }
}

.tags-list {
  max-height: 320px;
  overflow-y: auto;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 4px 0;
  border-top: 1px solid #eaeef2;
  border-bottom: 1px solid #eaeef2;
}

.tag-item {
  cursor: pointer;
  transition: transform 0.12s ease, box-shadow 0.12s ease;
  outline: none;
  display: inline-flex;
  align-items: center;
  border-radius: 12px;
  padding: 2px;
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(2,6,23,0.06);
  }
  &.selected {
    box-shadow: 0 6px 20px rgba(37,99,235,0.12);
    border: 1px solid rgba(37,99,235,0.12);
  }
  &:focus {
    box-shadow: 0 0 0 4px rgba(37,99,235,0.06);
  }
  .check-mark {
    font-size: 13px;
    font-weight: 700;
    color: #1e9b6e;
    margin-left: 6px;
    display: inline-flex;
    align-items: center;
  }
}

.empty-tips {
  font-size: 13px;
  color: #909399;
  padding: 20px 0;
  text-align: center;
  width: 100%;
}

/* 底部按钮区域 —— 上下排列，宽度 100%，模仿 CreateProject 风格 */
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 4px;
  margin-bottom: 12px;

  button {
    width: 100%;
    padding: 8px 0;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    border: none;
    transition: all 0.2s;
  }

  .confirm-btn {
    background-color: #409eff;
    color: white;
    &:hover {
      background-color: #66b1ff;
    }
  }

  .cancel-btn {
    background-color: #fff;
    border: 1px solid #dcdfe6;
    color: #606266;
    &:hover {
      background-color: #f5f7fa;
    }
  }
}
</style>