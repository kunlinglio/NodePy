<template>
  <div class="server-storage-container">
    <!-- 统计卡片：存储概览 -->
    <div class="stats-grid">
      <div class="stat-card" style="--card-accent: #108efe">
        <div class="card-icon" style="background-color: #108efe10">
          <span class="icon-emoji">💾</span>
        </div>
        <div class="card-content">
          <div class="card-title">总存储空间</div>
          <div class="card-value">{{ formatBytes(storageStats.total_storage_bytes) }}</div>
        </div>
      </div>
      <div class="stat-card" style="--card-accent: #10b981">
        <div class="card-icon" style="background-color: #10b98110">
          <span class="icon-emoji">👤</span>
        </div>
        <div class="card-content">
          <div class="card-title">用户存储</div>
          <div class="card-value">{{ formatBytes(storageStats.guest_storage_bytes) }}</div>
        </div>
      </div>
      <div class="stat-card" style="--card-accent: #f59e0b">
        <div class="card-icon" style="background-color: #f59e0b10">
          <span class="icon-emoji">📘</span>
        </div>
        <div class="card-content">
          <div class="card-title">示例存储</div>
          <div class="card-value">{{ formatBytes(storageStats.example_storage_bytes) }}</div>
        </div>
      </div>
    </div>

    <!-- 饼图区域 -->
    <div class="chart-container">
      <div class="chart-header">
        <h3 class="section-title">📊 存储分布</h3>
        <span class="section-subtitle">各类型存储占比</span>
      </div>
      <div ref="chartRef" class="pie-chart"></div>
    </div>

    <!-- 用户存储查询 -->
    <div class="user-storage-query">
      <div class="query-header">
        <h3 class="section-title">🔍 查询用户存储</h3>
        <span class="section-subtitle">输入用户 ID 查看配额使用情况</span>
      </div>
      <div class="query-bar">
        <div class="query-input-wrapper">
          <span class="query-icon">🆔</span>
          <input
            v-model.number="userIdQuery"
            type="number"
            placeholder="用户 ID..."
            @keyup.enter="handleQueryUserStorage"
            class="query-input"
          />
        </div>
        <button class="query-btn" @click="handleQueryUserStorage">查询</button>
        <button class="reset-btn"
          @click="handleResetUserStorage"
          v-if="
            (userIdQuery !== null
            && userIdQuery !== '')
            || queried
          ">
            清空
          </button>
      </div>
      <div v-if="userStorageInfo" class="user-storage-card">
        <div class="user-storage-row">
          <span class="label">用户ID：</span>
          <span class="value">{{ userStorageInfo.user_id }}</span>
        </div>
        <div class="user-storage-row">
          <span class="label">用户名：</span>
          <span class="value">{{ userStorageInfo.username }}</span>
        </div>
        <div class="user-storage-row">
          <span class="label">已用空间：</span>
          <span class="value">{{ formatBytes(userStorageInfo.used_bytes) }}</span>
        </div>
        <div class="user-storage-row">
          <span class="label">总配额：</span>
          <span class="value">{{ formatBytes(userStorageInfo.total_bytes) }}</span>
        </div>
        <div class="user-storage-row">
          <span class="label">使用率：</span>
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: `${userStorageInfo.used_percentage}%` }"
            ></div>
          </div>
          <span class="value">{{ userStorageInfo.used_percentage.toFixed(1) }}%</span>
        </div>
      </div>
      <div v-else-if="queried && !userStorageInfo" class="user-storage-card empty">
        <div class="empty-text">未找到该用户或查询出错</div>
      </div>
    </div>

    <!-- 文件列表 -->
    <div class="data-table-wrapper">
      <div class="table-header">
        <h3 class="section-title">📄 文件列表</h3>
        <span class="section-subtitle">服务器存储的所有文件</span>
      </div>

      <!-- 文件名搜索 -->
      <div class="search-bar file-search">
        <div class="search-input-wrapper">
          <span class="search-icon">🔍</span>
          <input
            v-model="searchFilename"
            type="text"
            placeholder="按文件名搜索..."
            @keyup.enter="handleFileSearch"
            class="search-input"
          />
        </div>
        <div class="search-actions">
          <button class="search-btn" @click="handleFileSearch">搜索</button>
          <button class="reset-btn" @click="handleResetFileSearch" v-if="searchFilename">清空</button>
        </div>
      </div>

      <div class="table-container" v-if="!fileLoading && fileList.length > 0">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>文件名</th>
              <th>格式</th>
              <th>用户ID</th>
              <th>项目ID</th>
              <th>文件大小</th>
              <th>最后修改</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="file in fileList" :key="file.id">
              <td class="file-id">{{ file.id }}</td>
              <td class="filename">{{ file.filename }}</td>
              <td class="format">{{ file.format || '-' }}</td>
              <td class="user-id">{{ file.user_id }}</td>
              <td class="project-id">{{ file.project_id || '-' }}</td>
              <td class="file-size">{{ formatBytes(file.file_size) }}</td>
              <td class="last-modify">{{ formatDate(file.last_modify_time) }}</td>
              <td class="status">
                <span :class="['status-badge', file.is_deleted ? 'deleted' : 'active']">
                  {{ file.is_deleted ? '已删除' : '正常' }}
                </span>
              </td>
              <td class="actions">
                <button
                  class="action-btn preview-btn"
                  @click="handlePreviewFile(file.key)"
                  title="预览文件"
                >
                  预览
                </button>
                <button
                  class="action-btn delete-btn"
                  @click="handleDeleteFile(file.id, file.filename)"
                  title="删除文件"
                >
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!fileLoading && fileList.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <div class="empty-text">暂无文件数据</div>
      </div>

      <!-- 加载状态 -->
      <div v-if="fileLoading" class="loading-wrapper">
        <Loading />
      </div>
    </div>

    <!-- 分页组件 -->
    <PageDivision
      :current-page="fileCurrentPage"
      :total-pages="fileTotalPages"
      @page-change="goToFilePage"
    />
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from "vue";
import * as echarts from "echarts";
import { useAdminStore } from "@/stores/adminStore";
import { type StorageStats, type UserStorageInfo, type FileInfo } from "@/utils/api";
import Loading from "@/components/Loading.vue";
import PageDivision from "./PageDivision.vue";

const adminStore = useAdminStore();

// 存储概览
const storageStats = ref<StorageStats>({
  total_storage_bytes: 0,
  guest_storage_bytes: 0,
  example_storage_bytes: 0,
});

// 饼图
const chartRef = ref<HTMLElement | null>(null);
let chartInstance: echarts.ECharts | null = null;

// 用户查询
const userIdQuery = ref<number | null | ''>(null);
const userStorageInfo = ref<UserStorageInfo | null>(null);
const queried = ref(false);

// 文件列表
const fileList = ref<FileInfo[]>([]);
const totalFiles = ref(0);
const fileLoading = ref(false);
const searchFilename = ref("");
const fileCurrentPage = ref(1);
const pageSize = 20;

// 总页数
const fileTotalPages = ref(1);

// 辅助函数
const formatBytes = (bytes: number): string => {
  if (bytes === undefined || bytes === null) return "0 B";
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
};

const formatDate = (dateStr: string): string => {
  if (!dateStr) return "未知";
  const date = new Date(dateStr);
  return date.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

// 获取存储概览
const fetchStorageOverview = async () => {
  try {
    storageStats.value = await adminStore.getStorageOverview();
    updateChart();
  } catch (error) {
    console.error("获取存储概览失败:", error);
  }
};

// 初始化/更新饼图
const updateChart = () => {
  if (!chartRef.value) return;
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value);
  }
  const otherStorage = storageStats.value.total_storage_bytes - storageStats.value.guest_storage_bytes - storageStats.value.example_storage_bytes;
  const data = [
    { name: "用户存储", value: storageStats.value.guest_storage_bytes, itemStyle: { color: "#10b981" } },
    { name: "示例存储", value: storageStats.value.example_storage_bytes, itemStyle: { color: "#f59e0b" } },
    { name: "其他存储", value: otherStorage, itemStyle: { color: "#108efe" } },
  ].filter(item => item.value > 0);
  chartInstance.setOption({
    tooltip: {
      trigger: "item",
      formatter: (params: any) => {
        return `${params.name}: ${formatBytes(params.value)} (${params.percent.toFixed(1)}%)`;
      }
    },
    series: [{
      type: "pie",
      radius: "55%",
      data: data,
      label: { show: true, formatter: "{b}" },
      emphasis: { scale: true },
    }],
  });
};

// 查询用户存储
const handleQueryUserStorage = async () => {
  const userId = userIdQuery.value;
  if (userId === null || userId === '' || isNaN(userId)) return;
  try {
    userStorageInfo.value = await adminStore.getUserStorage(userId);
    queried.value = true;
  } catch (error) {
    userStorageInfo.value = null;
    queried.value = true;
  }
};

const handleResetUserStorage = () => {
  userIdQuery.value = null;
  userStorageInfo.value = null;
  queried.value = false;
};

// 获取文件总数
const fetchFileTotal = async () => {
  try {
    const filename = searchFilename.value.trim() || null;
    totalFiles.value = await adminStore.getFileNum(filename);
    fileTotalPages.value = Math.ceil(totalFiles.value / pageSize);
  } catch (error) {
    console.error("获取文件总数失败:", error);
    totalFiles.value = 0;
    fileTotalPages.value = 1;
  }
};

// 获取文件列表
const fetchFileList = async () => {
  try {
    const filename = searchFilename.value.trim() || null;
    const offset = (fileCurrentPage.value - 1) * pageSize;
    const list = await adminStore.getFileList(filename, pageSize, offset);
    fileList.value = list || [];
  } catch (error) {
    console.error("获取文件列表失败:", error);
    fileList.value = [];
  }
};

// 刷新文件数据
const refreshFileData = async () => {
  fileLoading.value = true;
  await fetchFileTotal();
  await fetchFileList();
  fileLoading.value = false;
};

// 文件搜索
const handleFileSearch = async () => {
  if (fileCurrentPage.value !== 1) fileCurrentPage.value = 1;
  await refreshFileData();
};

const handleResetFileSearch = async () => {
  searchFilename.value = "";
  if (fileCurrentPage.value !== 1) fileCurrentPage.value = 1;
  await refreshFileData();
};

// 分页跳转
const goToFilePage = async (page: number) => {
  if (page < 1 || page > fileTotalPages.value) return;
  fileCurrentPage.value = page;
  await fetchFileList();
};

// 预览文件（接收 key，二进制流）
const handlePreviewFile = async (key: string) => {
  try {
    const blob = await adminStore.previewFile(key);
    const url = URL.createObjectURL(blob);
    window.open(url, "_blank");
    // 延迟释放，确保新窗口能够加载
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  } catch (error) {
    console.error("预览文件失败:", error);
  }
};

// 删除文件
const handleDeleteFile = async (fileId: number, filename: string) => {
  const confirmMsg = `确定要永久删除文件 “${filename}” 吗？\n此操作不可恢复！`;
  if (!window.confirm(confirmMsg)) return;
  await adminStore.deleteFile(fileId);
  // 如果当前页只有一条数据且不是第一页，则跳到上一页
  if (fileList.value.length === 1 && fileCurrentPage.value > 1) {
    fileCurrentPage.value--;
  }
  await refreshFileData();
};

// 窗口大小调整
const handleResize = () => {
  if (chartInstance) chartInstance.resize();
};

onMounted(async () => {
  await fetchStorageOverview();
  await refreshFileData();
  window.addEventListener("resize", handleResize);
});
</script>

<style scoped lang="scss">
@use "sass:color";
$primary-color: #108efe;
$bg-light: #f5f7fa;
$card-white: #ffffff;
$text-dark: #2c3e50;
$text-gray: #5b6e8c;
$border-light: #eef2f8;
$shadow-sm: 0 2px 8px rgba(16, 142, 254, 0.08);
$shadow-md: 0 8px 20px rgba(0, 0, 0, 0.05);

.server-storage-container {
  width: 100%;
  height: 100%;
  background: transparent;
  overflow-y: auto;
  padding: 4px;
}

/* 统计卡片 */
.stats-grid {
  display: flex;
  justify-content: flex-start;
  gap: 20px;
  margin-bottom: 24px;
  flex-wrap: wrap;

  .stat-card {
    width: 240px;
    background: $card-white;
    border-radius: 12px;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    border: 1px solid $border-light;
    box-shadow: $shadow-sm;
    position: relative;
    overflow: hidden;

    &::before {
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      width: 4px;
      height: 100%;
      background: var(--card-accent, $primary-color);
    }

    .card-icon {
      width: 52px;
      height: 52px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      .icon-emoji { font-size: 26px; }
    }

    .card-content {
      flex: 1;
      .card-title {
        font-size: 14px;
        font-weight: 500;
        color: $text-gray;
        margin-bottom: 6px;
      }
      .card-value {
        font-size: 28px;
        font-weight: 800;
        color: $text-dark;
        line-height: 1.2;
      }
    }
  }
}

/* 饼图区域 */
.chart-container {
  background: $card-white;
  border-radius: 12px;
  border: 1px solid $border-light;
  box-shadow: $shadow-sm;
  padding: 20px;
  margin-bottom: 24px;

  .chart-header {
    margin-bottom: 16px;
    .section-title {
      font-size: 18px;
      font-weight: 700;
      color: $text-dark;
      margin: 0 0 4px 0;
    }
    .section-subtitle {
      font-size: 13px;
      color: $text-gray;
    }
  }

  .pie-chart {
    width: 100%;
    height: 400px;
  }
}

/* 用户存储查询 */
.user-storage-query {
  background: $card-white;
  border-radius: 12px;
  border: 1px solid $border-light;
  box-shadow: $shadow-sm;
  padding: 20px;
  margin-bottom: 24px;

  .query-header {
    margin-bottom: 16px;
    .section-title {
      font-size: 18px;
      font-weight: 700;
      color: $text-dark;
      margin: 0 0 4px 0;
    }
    .section-subtitle {
      font-size: 13px;
      color: $text-gray;
    }
  }

  .query-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
    align-items: center;
    flex-wrap: wrap;

    .query-input-wrapper {
      flex: 1;
      min-width: 200px;
      position: relative;
      display: flex;
      align-items: center;
      .query-icon {
        position: absolute;
        left: 12px;
        font-size: 16px;
        color: $text-gray;
        pointer-events: none;
        line-height: 1;
      }
      .query-input {
        width: 100%;
        padding: 10px 12px 10px 36px;
        border-radius: 12px;
        border: 1px solid $border-light;
        background: $card-white;
        font-size: 14px;
        outline: none;
        /* 隐藏 number 输入框的上下箭头 */
        &::-webkit-inner-spin-button,
        &::-webkit-outer-spin-button {
          -webkit-appearance: none;
          margin: 0;
        }
        -moz-appearance: textfield;
        &:focus {
          border-color: $primary-color;
          box-shadow: 0 0 0 3px rgba(16, 142, 254, 0.1);
        }
      }
    }

    .query-btn {
      padding: 8px 16px;
      border-radius: 12px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      border: none;
      transition: all 0.2s ease;
      background: $primary-color;
      color: white;
      &:hover {
        background: color.scale($primary-color, $lightness: -8%);
        transform: translateY(-1px);
      }
    }
  }

  .user-storage-card {
    background: $bg-light;
    border-radius: 12px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;

    .user-storage-row {
      display: flex;
      align-items: center;
      gap: 12px;
      .label {
        width: 80px;
        font-weight: 600;
        color: $text-dark;
      }
      .value {
        color: $text-gray;
        font-family: monospace;
      }
      .progress-bar {
        flex: 1;
        height: 8px;
        background: #e2e8f0;
        border-radius: 4px;
        overflow: hidden;
        .progress-fill {
          height: 100%;
          background: $primary-color;
          border-radius: 4px;
          transition: width 0.3s ease;
        }
      }
    }
    &.empty {
      text-align: center;
      padding: 20px;
      .empty-text {
        color: $text-gray;
      }
    }
  }
}

/* 全局搜索和重置按钮样式 */
.search-btn, .reset-btn {
  padding: 8px 16px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}

.search-btn {
  background: $primary-color;
  color: white;
  &:hover {
    background: color.scale($primary-color, $lightness: -8%);
    transform: translateY(-1px);
  }
}

.reset-btn {
  background: rgba(239, 68, 68, 0.08);
  color: #e5484d;
  border: 1px solid rgba(239, 68, 68, 0.2);
  &:hover {
    background: #e5484d;
    color: white;
  }
}

/* 文件列表表格 */
.data-table-wrapper {
  background: $card-white;
  border-radius: 12px;
  border: 1px solid $border-light;
  overflow: hidden;
  transition: all 0.2s ease;

  .table-header {
    padding: 20px 24px 12px 24px;
    border-bottom: 1px solid $border-light;
    .section-title {
      font-size: 18px;
      font-weight: 700;
      color: $text-dark;
      margin: 0 0 4px 0;
    }
    .section-subtitle {
      font-size: 13px;
      color: $text-gray;
    }
  }

  .search-bar.file-search {
    margin: 16px 24px;
    display: flex;
    gap: 12px;
    .search-input-wrapper {
      flex: 2;
      min-width: 200px;
      position: relative;
      display: flex;
      align-items: center;
      .search-icon {
        position: absolute;
        left: 12px;
        font-size: 16px;
        color: $text-gray;
        pointer-events: none;
        line-height: 1;
      }
      .search-input {
        width: 100%;
        padding: 10px 12px 10px 36px;
        border-radius: 12px;
        border: 1px solid $border-light;
        background: $card-white;
        font-size: 14px;
        &:focus {
          border-color: $primary-color;
          box-shadow: 0 0 0 3px rgba(16, 142, 254, 0.1);
        }
      }
    }
    .search-actions {
      display: flex;
      gap: 8px;
    }
  }

  .table-container {
    overflow-x: auto;
    padding: 0 4px 4px 4px;

    .data-table {
      width: 100%;
      table-layout: fixed;
      border-collapse: collapse;
      font-size: 14px;

      th, td {
        box-sizing: border-box;
        padding: 12px 12px;
        text-align: left;
        border-bottom: 1px solid $border-light;
      }

      td:not(.actions) {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      td.actions {
        overflow-x: auto;
        white-space: nowrap;
      }

      th {
        background: $bg-light;
        font-weight: 600;
        color: $text-dark;
        font-size: 13px;
        letter-spacing: 0.3px;
        white-space: nowrap;
      }

      // 列宽分配
      th:nth-child(1), td:nth-child(1) { width: 5%; }
      th:nth-child(2), td:nth-child(2) { width: 20%; }
      th:nth-child(3), td:nth-child(3) { width: 6%; }
      th:nth-child(4), td:nth-child(4) { width: 6%; }
      th:nth-child(5), td:nth-child(5) { width: 6%; }
      th:nth-child(6), td:nth-child(6) { width: 8%; }
      th:nth-child(7), td:nth-child(7) { width: 15%; }
      th:nth-child(8), td:nth-child(8) { width: 8%; }
      th:nth-child(9), td:nth-child(9) { width: 10%; }

      tbody tr:hover {
        background: rgba(16, 142, 254, 0.03);
      }

      .status-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        white-space: nowrap;
        &.active {
          background: #d1fae5;
          color: #059669;
        }
        &.deleted {
          background: #fee2e2;
          color: #dc2626;
        }
      }

      .actions {
        display: flex;
        gap: 8px;
        flex-wrap: nowrap;
        width: fit-content;
        min-width: 100%;
        .action-btn {
          padding: 6px 12px;
          border-radius: 20px;
          font-size: 12px;
          font-weight: 500;
          cursor: pointer;
          border: none;
          white-space: nowrap;
          transition: all 0.2s ease;
          background: rgba(16, 142, 254, 0.1);
          color: $primary-color;
          &:hover {
            background: $primary-color;
            color: white;
          }
          &.delete-btn {
            background: rgba(239, 68, 68, 0.1);
            color: #e5484d;
            &:hover {
              background: #e5484d;
              color: white;
            }
          }
        }
      }
    }
  }

  .empty-state {
    padding: 60px 20px;
    text-align: center;
    .empty-icon { font-size: 48px; margin-bottom: 16px; opacity: 0.6; }
    .empty-text { font-size: 14px; color: $text-gray; }
  }

  .loading-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 300px;
  }
}

/* 滚动条 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: $border-light;
  border-radius: 8px;
}
::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 8px;
  &:hover { background: #94a3b8; }
}

/* 响应式 */
@media (max-width: 768px) {
  .stats-grid .stat-card {
    width: 100%;
  }
  .data-table th, .data-table td {
    padding: 10px 8px;
    font-size: 12px;
  }
}
</style>