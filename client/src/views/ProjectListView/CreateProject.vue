<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { useProjectStore } from '@/stores/projectStore';
import { useModalStore } from '@/stores/modalStore';
import { useUserStore } from '@/stores/userStore';
import { onUnmounted } from 'vue';
import Tag from '@/components/Tag.vue'; 

const projectStore = useProjectStore();
const modalStore = useModalStore();
const userStore = useUserStore();

const inputRef = ref<HTMLInputElement | null>(null);

// 临时标签列表（创建时为空）
const selectedTags = ref<string[]>([]);

// 添加标签到临时列表
function addTagToTemp(tag: string) {
  if (!selectedTags.value.includes(tag)) {
    selectedTags.value.push(tag);
    console.log(selectedTags.value)
  }
}

// 从临时列表删除标签
function removeTagFromTemp(tag: string) {
  const index = selectedTags.value.indexOf(tag);
  if (index !== -1) {
    selectedTags.value.splice(index, 1);
    console.log(selectedTags.value)
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

onMounted(() => {
  if (inputRef.value) {
    inputRef.value.focus();
  }
});

async function onCreateProject() {
  // 将临时标签同步到 store
  projectStore.currentProjectTags = selectedTags.value;
  const success = await projectStore.createProject();
  console.log('创建项目:', projectStore.currentProjectName, '公开：', projectStore.currentWhetherShow, '标签:', projectStore.currentProjectTags, '结果:', success);
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

      <!-- 公开项目复选框（与修改弹窗保持一致） -->
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

    .create-project-form{
        margin-bottom: 20px;
    }

    .button-container{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        // gap: 5px;
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

    .button.cancel{
        margin-top: 10px;
        margin-left: 0;
        @include cancel-button-style;
    }

    .button.cancel:hover{
        @include cancel-button-hover-style;
    }

    .button.confirm-button{
        width: 100%;
        @include confirm-button-style;
    }

    .button.confirm-button:hover{
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

// 所有标签容器：三行，垂直滚动
.all-tags-wrapper {
  .tags-scroll-container.three-rows {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    max-height: 100px;       // 约三行高度（28px*3 + 8px*2 = 100px）
    overflow-y: auto;
    padding: 2px 0;
    
    // 自定义滚动条（可选）
    &::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    &::-webkit-scrollbar-thumb {
      background: #c1c1c1;
      border-radius: 3px;
    }
  }
}

// 当前项目标签容器：一行，横向滚动
.current-tags-wrapper {
  .tags-scroll-container.one-row {
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
}

// 新增按钮样式（与 Tag 组件风格一致）
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
</style>