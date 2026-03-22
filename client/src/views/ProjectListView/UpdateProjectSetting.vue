<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { useProjectStore } from '@/stores/projectStore';
import { useModalStore } from '@/stores/modalStore';
import { useUserStore } from '@/stores/userStore';
import Tag from '@/components/Tag.vue';

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
      await projectStore.getAllTags();
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
        <div class="all-tags-wrapper">
          <div class="tags-scroll-container three-rows">
            <div class="tag-item add-new" @click="createNewTag">
              <span>+ 新建</span>
            </div>
            <Tag
              v-for="tag in projectStore.allProjectTags"
              :key="tag"
              :content="tag"
            >
              <template #action>
                <span class="tag-action add" @click.stop="addTagToTemp(tag)">+</span>
              </template>
            </Tag>
          </div>
        </div>

        <div class="section-title">当前项目标签</div>
        <div class="current-tags-wrapper">
          <div class="tags-scroll-container one-row">
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

.tags-section {
  margin-top: 16px;
  .section-title {
    font-size: 14px;
    font-weight: 500;
    margin: 12px 0 8px;
    color: #606266;
  }
}

.all-tags-wrapper .tags-scroll-container.three-rows {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  max-height: 100px;
  overflow-y: auto;
  padding: 2px 0;
  
  &::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
  }
}

.current-tags-wrapper .tags-scroll-container.one-row {
  display: flex;
  flex-wrap: nowrap;
  gap: 8px;
  overflow-x: auto;
  padding: 2px 0;
  
  &::-webkit-scrollbar {
    height: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
  }
}

.tag-item.add-new {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 16px;
  font-size: 12px;
  background-color: #ecf5ff;
  color: #409eff;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
  
  &:hover {
    background-color: #d9ecff;
  }
}

.tag-action {
  margin-left: 4px;
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

.empty-tips {
  font-size: 12px;
  color: #909399;
  padding: 4px 0;
  white-space: nowrap;
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