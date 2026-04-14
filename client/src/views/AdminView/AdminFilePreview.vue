<template>
  <div class="admin-file-preview-page">
    <FileView v-if="fileData" :value="fileData" />
    <Loading v-else-if="loading" />
    <div v-else class="error-state">
      <p>{{ error || '无法加载文件' }}</p>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useAdminStore } from '@/stores/adminStore';
import { useFileStore } from '@/stores/fileStore';
import FileView from '@/components/Result/FileView.vue'; // 根据实际路径调整
import Loading from '@/components/Loading.vue';
import type { FileItem } from '@/utils/api';

const route = useRoute();
const adminStore = useAdminStore();
const fileStore = useFileStore();

const fileKey = route.query.key as string;
const filename = route.query.filename as string;
const format = route.query.format as string;
const size = Number(route.query.size);
const modifiedAt = route.query.modified as string;

const loading = ref(true);
const error = ref('');
const fileData = ref<FileItem | null>(null);

onMounted(async () => {
  if (!fileKey || !filename) {
    error.value = '缺少文件参数';
    loading.value = false;
    return;
  }

  try {
    // 1. 使用管理员专用预览 API 获取 Blob
    const blob = await adminStore.previewFile(fileKey);

    // 2. 构造 FileItem 对象
    const item: FileItem = {
      key: fileKey,
      filename: filename,
      format: format as any,
      size: size,
      modified_at: modifiedAt ? new Date(modifiedAt).getTime() : Date.now(),
      project_name: '',
    };
    fileData.value = item;

    // 3. 将 Blob 存入 fileStore 缓存，以便 FileView 内部通过 fileStore.getCacheContent 获取
    fileStore.addCacheContent(fileKey, blob);
    
    // 4. 设置当前文件（部分组件可能依赖此状态）
    fileStore.changeCurrentFile(item);

    loading.value = false;
  } catch (err: any) {
    console.error('预览文件失败:', err);
    error.value = err.message || '加载文件失败，请稍后重试';
    loading.value = false;
  }
});
</script>

<style scoped lang="scss">
.admin-file-preview-page {
  width: 100%;
  height: 100vh;
  background: #f5f7fa;
  overflow: hidden;
}

.error-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
  font-size: 16px;
  padding: 20px;
  text-align: center;
}
</style>