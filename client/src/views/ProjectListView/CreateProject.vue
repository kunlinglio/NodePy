<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { useProjectStore } from '@/stores/projectStore';
import { useModalStore } from '@/stores/modalStore';
import { useUserStore } from '@/stores/userStore';
import { onUnmounted } from 'vue';

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

// 原有样式保持不变，新增标签相关样式
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
</style>

<script lang="ts">
// 辅助函数：根据标签内容生成一致的随机颜色（可自行改进）
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