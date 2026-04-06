<template>
  <div class="project-status-container">
    <!-- 统计卡片：项目总数 -->
    <div class="stats-grid">
      <div class="stat-card" style="--card-accent: #108efe">
        <div class="card-icon" style="background-color: #108efe10">
          <span class="icon-emoji">📁</span>
        </div>
        <div class="card-content">
          <div class="card-title">项目总数</div>
          <div class="card-value">{{ totalProjects }}</div>
        </div>
      </div>
    </div>

    <!-- 搜索栏（用户名 + 项目名） -->
    <div class="search-bar">
      <div class="search-input-wrapper">
        <span class="search-icon">👤</span>
        <input
          v-model="searchOwner"
          type="text"
          placeholder="按用户名搜索..."
          @keyup.enter="handleSearch"
          class="search-input"
        />
      </div>
      <div class="search-input-wrapper">
        <span class="search-icon">📄</span>
        <input
          v-model="searchProjectName"
          type="text"
          placeholder="按项目名搜索..."
          @keyup.enter="handleSearch"
          class="search-input"
        />
      </div>
      <div class="search-actions">
        <button class="search-btn" @click="handleSearch">搜索</button>
        <button class="reset-btn" @click="handleResetSearch" v-if="searchOwner || searchProjectName">
          清空筛选
        </button>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="data-table-wrapper">
      <div class="table-header">
        <h3 class="section-title">📂 项目管理</h3>
        <span class="section-subtitle">所有项目的详细信息与操作</span>
      </div>

      <div class="table-container" v-if="!loading && projectList.length > 0">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>项目名</th>
              <th>所有者</th>
              <th>可见性</th>
              <th>创建时间</th>
              <th>更新时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="project in projectList" :key="project.id">
              <td class="project-id">{{ project.id }}</td>
              <td class="project-name">{{ project.name }}</td>
              <td class="owner">{{ project.owner_username || '未知' }}</td>
              <td class="visibility">
                <span
                  class="visibility-badge"
                  :class="{ public: project.show_in_explore, private: !project.show_in_explore }"
                >
                  {{ project.show_in_explore ? '公开' : '私有' }}
                </span>
              </td>
              <td class="created-at">{{ formatDate(project.created_at) }}</td>
              <td class="updated-at">{{ formatDate(project.updated_at) }}</td>
              <td class="actions">
                <template v-if="!isReservedProject(project.owner_username)">
                  <button
                    class="action-btn toggle-btn"
                    @click="handleToggleVisibility(project.id, project.show_in_explore, project.name)"
                    :title="project.show_in_explore ? '设为私有' : '设为公开'"
                  >
                    {{ project.show_in_explore ? '🔒 设为私有' : '🌍 设为公开' }}
                  </button>
                  <button
                    class="action-btn delete-btn"
                    @click="handleDeleteProject(project.id, project.name)"
                    title="删除项目"
                  >
                    🗑️ 删除项目
                  </button>
                </template>
                <span v-else class="reserved-tip">保留项目，不可操作</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!loading && projectList.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <div class="empty-text">暂无项目数据</div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-wrapper">
        <Loading />
      </div>
    </div>

    <!-- 分页组件 -->
    <PageDivision
      :current-page="currentPage"
      :total-pages="totalPages"
      @page-change="goToPage"
    />
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed } from "vue";
import { type ProjectInfo } from "@/utils/api";
import { useAdminStore } from "@/stores/adminStore";
import Loading from "@/components/Loading.vue";
import PageDivision from "./PageDivision.vue";

const adminStore = useAdminStore();

const projectList = ref<ProjectInfo[]>([]);
const totalProjects = ref(0);
const loading = ref(true);
const searchOwner = ref("");
const searchProjectName = ref("");
const currentPage = ref(1);
const pageSize = 20; // 每页20条，测试时可改为1

// 保留用户名列表（这些用户的项目不允许操作）
const reservedOwners = ['NodePy-Learning', 'NodePy-Guest'];

// 判断是否为保留项目（兼容 owner_username 为 null 的情况）
const isReservedProject = (ownerUsername: string | null | undefined): boolean => {
  if (!ownerUsername) return false;
  return reservedOwners.includes(ownerUsername);
};

// 总页数
const totalPages = computed(() => Math.ceil(totalProjects.value / pageSize));

// 格式化日期
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

// 获取项目总数
const fetchTotalProjects = async () => {
  try {
    const owner = searchOwner.value.trim() || null;
    const name = searchProjectName.value.trim() || null;
    totalProjects.value = await adminStore.getProjectNum(owner, name);
  } catch (error) {
    console.error("获取项目总数失败:", error);
    totalProjects.value = 0;
  }
};

// 获取项目列表（分页）
const fetchProjectList = async () => {
  try {
    const owner = searchOwner.value.trim() || null;
    const name = searchProjectName.value.trim() || null;
    const offset = (currentPage.value - 1) * pageSize;
    const list = await adminStore.getProjectList(owner, name, pageSize, offset);
    projectList.value = list || [];
  } catch (error) {
    console.error("获取项目列表失败:", error);
    projectList.value = [];
  }
};

// 刷新所有数据
const refreshData = async () => {
  loading.value = true;
  await fetchTotalProjects();
  await fetchProjectList();
  loading.value = false;
};

// 搜索处理
const handleSearch = async () => {
  if (currentPage.value !== 1) {
    currentPage.value = 1;
  }
  await refreshData();
};

// 清空筛选
const handleResetSearch = async () => {
  searchOwner.value = "";
  searchProjectName.value = "";
  if (currentPage.value !== 1) {
    currentPage.value = 1;
  }
  await refreshData();
};

// 跳转页面
const goToPage = async (page: number) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  await fetchProjectList();
};

// 切换可见性 - 无需弹窗确认
const handleToggleVisibility = async (projectId: number, currentVisible: boolean, projectName: string) => {
  const newVisibility = !currentVisible;
  await adminStore.setProjectVisibility(projectId, newVisibility);
  await fetchProjectList(); // 刷新当前页，无需重新获取总数（可见性不影响总数）
};

// 删除项目 - 需要弹窗确认
const handleDeleteProject = async (projectId: number, projectName: string) => {
  const confirmMsg = `确定要永久删除项目 “${projectName}” 吗？\n此操作不可恢复！`;
  if (!window.confirm(confirmMsg)) return;
  await adminStore.deleteProject(projectId);
  // 如果当前页只有一条数据且不是第一页，则跳到上一页
  if (projectList.value.length === 1 && currentPage.value > 1) {
    currentPage.value--;
  }
  await refreshData();
};

onMounted(async () => {
  await refreshData();
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

.project-status-container {
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
  margin-bottom: 24px;

  .stat-card {
    width: 240px;
    background: $card-white;
    border-radius: 12px;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    transition: all 0.3s ease;
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
      transition: width 0.2s ease;
    }

    &:hover {
      transform: translateY(-4px);
      box-shadow: $shadow-md;
      border-color: rgba(16, 142, 254, 0.2);

      &::before {
        width: 6px;
      }

      .card-icon {
        transform: scale(1.05);
      }
    }

    .card-icon {
      width: 52px;
      height: 52px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: transform 0.2s ease;

      .icon-emoji {
        font-size: 26px;
      }
    }

    .card-content {
      flex: 1;

      .card-title {
        font-size: 14px;
        font-weight: 500;
        color: $text-gray;
        margin-bottom: 6px;
        letter-spacing: 0.3px;
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

/* 搜索栏 */
.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  align-items: center;
  flex-wrap: wrap;

  .search-input-wrapper {
    flex: 1;
    min-width: 180px;
    position: relative;
    display: flex;
    align-items: center;

    .search-icon {
      position: absolute;
      left: 12px;
      font-size: 16px;
      color: $text-gray;
      pointer-events: none;
    }

    .search-input {
      width: 100%;
      padding: 10px 12px 10px 36px;
      border-radius: 12px;
      border: 1px solid $border-light;
      background: $card-white;
      font-size: 14px;
      transition: all 0.2s ease;
      outline: none;

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

.search-btn,
.reset-btn {
  padding: 8px 16px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.search-btn {
  background: $primary-color;
  color: white;
  box-shadow: $shadow-sm;

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
    transform: translateY(-1px);
  }
}

/* 表格区域 */
.data-table-wrapper {
  background: $card-white;
  border-radius: 12px;
  border: 1px solid $border-light;
  box-shadow: $shadow-sm;
  overflow: hidden;
  transition: all 0.2s ease;

  &:hover {
    box-shadow: $shadow-md;
  }

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

  .table-container {
    overflow-x: auto;
    padding: 0 4px 4px 4px;

    .data-table {
      width: 100%;
      table-layout: fixed;
      border-collapse: collapse;
      font-size: 14px;

      th,
      td {
        padding: 12px 12px;
        text-align: left;
        border-bottom: 1px solid $border-light;
        word-break: break-word;
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
      th:nth-child(1), td:nth-child(1) { width: 6%; }   // ID
      th:nth-child(2), td:nth-child(2) { width: 18%; }  // 项目名
      th:nth-child(3), td:nth-child(3) { width: 12%; }  // 所有者
      th:nth-child(4), td:nth-child(4) { width: 10%; }  // 可见性
      th:nth-child(5), td:nth-child(5) { width: 15%; }  // 创建时间
      th:nth-child(6), td:nth-child(6) { width: 15%; }  // 更新时间
      th:nth-child(7), td:nth-child(7) { width: 24%; }  // 操作

      tbody tr {
        transition: background 0.2s ease;

        &:hover {
          background: rgba(16, 142, 254, 0.03);
        }
      }

      .project-id,
      .project-name,
      .owner {
        font-weight: 500;
        color: $text-dark;
      }

      .visibility-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;

        &.public {
          background: #d1fae5;
          color: #059669;
        }

        &.private {
          background: #fee2e2;
          color: #dc2626;
        }
      }

      .created-at,
      .updated-at {
        color: $text-gray;
        font-size: 13px;
      }

      .actions {
        display: flex;
        gap: 8px;
        flex-wrap: nowrap;

        .action-btn {
          padding: 6px 12px;
          border-radius: 20px;
          font-size: 12px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
          border: none;
          display: inline-flex;
          align-items: center;
          gap: 4px;
          white-space: nowrap;

          &.toggle-btn {
            background: rgba(16, 142, 254, 0.1);
            color: $primary-color;

            &:hover {
              background: $primary-color;
              color: white;
            }
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

        .reserved-tip {
          font-size: 12px;
          background: #e6f0ff;
          color: #1e6fdf;
          padding: 4px 10px;
          border-radius: 20px;
          white-space: nowrap;
        }
      }
    }
  }

  .empty-state {
    padding: 60px 20px;
    text-align: center;

    .empty-icon {
      font-size: 48px;
      margin-bottom: 16px;
      opacity: 0.6;
    }

    .empty-text {
      font-size: 14px;
      color: $text-gray;
    }
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

  &:hover {
    background: #94a3b8;
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .stats-grid .stat-card {
    width: 100%;
  }

  .search-bar {
    flex-direction: column;
    align-items: stretch;

    .search-input-wrapper {
      width: 100%;
    }
  }

  .data-table th,
  .data-table td {
    padding: 10px 8px;
    font-size: 12px;
  }

  .actions {
    flex-wrap: wrap !important;
    gap: 4px;

    .action-btn {
      white-space: normal;
    }
  }
}
</style>