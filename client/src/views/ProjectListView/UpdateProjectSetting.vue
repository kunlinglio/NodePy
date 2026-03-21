<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { useProjectStore } from '@/stores/projectStore';
import { useModalStore } from '@/stores/modalStore';
import { useUserStore } from '@/stores/userStore';

const projectStore = useProjectStore();
const modalStore = useModalStore();
const userStore = useUserStore();
const labelPosition = ref<string>('top');

// 临时标签列表（初始从 store.currentProjectTags 复制）
const selectedTags = ref<string[]>([]);

// 添加/删除标签（临时）
function addTagToTemp(tag: string) {
  if (!selectedTags.value.includes(tag)) {
    selectedTags.value.push(tag);
  }
}
function removeTagFromTemp(tag: string) {
  const index = selectedTags.value.indexOf(tag);
  if (index !== -1) {
    selectedTags.value.splice(index, 1);
  }
}

// 创建新标签
async function createNewTag() {
  const tagName = prompt('请输入新标签名称');
  if (tagName && tagName.trim()) {
    const success = await projectStore.createTag(tagName.trim());
    if (success) {
      // 自动添加到当前临时标签
      addTagToTemp(tagName.trim());
    }
  }
}

onMounted(async () => {
  await projectStore.getProjectSettings(projectStore.currentProjectId);
  // 初始化临时标签列表
  selectedTags.value = [...projectStore.currentProjectTags];
});

async function onConfirmUpdateProject() {
  // 同步临时标签到 store
  projectStore.currentProjectTags = selectedTags.value;
  console.log('selectedTags:', selectedTags.value,'currentProjectID', projectStore.currentProjectId, 'currentProjectName:', projectStore.currentProjectName, 'currentWhetherShow:', projectStore.currentWhetherShow);
  await projectStore.updateProjectSetting(projectStore.currentProjectId);
  await projectStore.initializeProjects();
  await projectStore.getAllTags();
  modalStore.deactivateModal('update-modal');
  modalStore.destroyModal('update-modal');
}

async function onCancelUpdateProject() {
  modalStore.deactivateModal('update-modal');
  modalStore.destroyModal('update-modal');
}
</script>

<template>
  <div class="update-project-container">
    <el-form :label-position="labelPosition">
      <el-form-item label="新项目名称">
        <input class="name-input" placeholder="请输入新的项目名称" v-model="projectStore.currentProjectName" />
      </el-form-item>

      <el-form-item label="公开项目">
        <label class="checkbox-container">
          <input type="checkbox" class="custom-checkbox" v-model="projectStore.currentWhetherShow" />
          <span class="checkmark"></span>
        </label>
      </el-form-item>

      <!-- 标签管理区域 -->
      <div class="tags-section">
        <div class="section-title">所有标签</div>
        <div class="tags-list">
          <div
            v-for="tag in projectStore.allProjectTags"
            :key="tag"
            class="tag-item"
            :style="{ backgroundColor: getRandomColor(tag) }"
          >
            {{ tag }}
            <span class="tag-action add" @click.stop="addTagToTemp(tag)">+</span>
          </div>
          <div class="tag-item add-new" @click="createNewTag">
            <span>+ 新建</span>
          </div>
        </div>

        <div class="section-title">当前项目标签</div>
        <div class="tags-list">
          <div
            v-for="tag in selectedTags"
            :key="tag"
            class="tag-item"
            :style="{ backgroundColor: getRandomColor(tag) }"
          >
            {{ tag }}
            <span class="tag-action remove" @click.stop="removeTagFromTemp(tag)">✕</span>
          </div>
          <div v-if="selectedTags.length === 0" class="empty-tips">暂无标签</div>
        </div>
      </div>
    </el-form>

    <div class="button-container">
      <button @click="onConfirmUpdateProject" class="confirm-button">修改</button>
      <button @click="onCancelUpdateProject" class="cancel-button">取消</button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use "../../common/global.scss" as *;

.update-project-container {
  display: flex;
  flex-direction: column;
  width: 300px;
  padding-bottom: 5px;
}

// 复用创建弹窗的标签样式
.tags-section {
  margin-top: 16px;
  .section-title {
    font-size: 14px;
    font-weight: 500;
    margin: 12px 0 8px;
    color: #606266;
  }
  .tags-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
  }
  .tag-item {
    display: inline-flex;
    align-items: center;
    padding: 4px 8px;
    border-radius: 16px;
    font-size: 12px;
    color: #2c3e50;
    background-color: #f0f2f5;
    cursor: default;
    .tag-action {
      margin-left: 6px;
      cursor: pointer;
      font-size: 14px;
      font-weight: bold;
      &.add {
        color: #27ae60;
      }
      &.remove {
        color: #e74c3c;
      }
    }
  }
  .add-new {
    background-color: #ecf5ff;
    color: #409eff;
    cursor: pointer;
    &:hover {
      background-color: #d9ecff;
    }
  }
  .empty-tips {
    font-size: 12px;
    color: #909399;
  }
}

.checkbox-container {
  display: flex;
  align-items: center;
  cursor: pointer;
  position: relative;
  user-select: none;
}
.custom-checkbox {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}
.checkmark {
  height: 20px;
  width: 20px;
  background-color: #fff;
  border: 2px solid #dcdfe6;
  border-radius: 4px;
  transition: all 0.3s ease;
  position: relative;
}
.checkbox-container:hover .checkmark {
  border-color: $stress-color;
}
.custom-checkbox:checked ~ .checkmark {
  background-color: $stress-color;
  border-color: $stress-color;
}
.checkmark:after {
  content: "";
  position: absolute;
  display: none;
}
.custom-checkbox:checked ~ .checkmark:after {
  display: block;
  left: 6px;
  top: 3px;
  width: 5px;
  height: 9px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.button-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 10px;
  margin-top: 16px;
}
.confirm-button {
  @include confirm-button-style;
}
.cancel-button {
  @include cancel-button-style;
}
.confirm-button:hover {
  @include confirm-button-hover-style;
}
.cancel-button:hover {
  @include cancel-button-hover-style;
}
.name-input {
  @include input-style;
}
.name-input:focus {
  @include input-focus-style;
}
</style>

<script lang="ts">
// 辅助颜色函数（同创建弹窗）
function getRandomColor(str: string): string {
  const colors = [
    '#FFE5B4', '#B4E0FF', '#C2F2E8', '#E6D3FF', '#FFD6E0',
    '#D4F7D4', '#FFFACD', '#F0FFF0', '#F5F5DC', '#E6F3FF',
    '#FFF0F5', '#FDFD96', '#E0FFFF', '#DDF8D8', '#FFE4E1',
    '#F0E68C', '#D8BFD8', '#AFEEEE', '#F5DEB3', '#DEB887'
  ];
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash |= 0;
  }
  return colors[Math.abs(hash) % colors.length]!;
}
</script>