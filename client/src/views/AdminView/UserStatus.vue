<template>
  <div class="user-status-container">
    <!-- 统计卡片：用户总数 -->
    <div class="stats-grid">
      <div class="stat-card" style="--card-accent: #108efe">
        <div class="card-icon" style="background-color: #108efe10">
          <span class="icon-emoji">👥</span>
        </div>
        <div class="card-content">
          <div class="card-title">用户总数</div>
          <div class="card-value">{{ totalUsers }}</div>
        </div>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <div class="search-input-wrapper">
        <span class="search-icon">🔍</span>
        <input
          v-model="searchUsername"
          type="text"
          placeholder="按用户名搜索..."
          @keyup.enter="handleSearch"
          class="search-input"
        />
      </div>
      <div class="search-actions">
        <button class="search-btn" @click="handleSearch">搜索</button>
        <button class="reset-btn" @click="handleResetSearch" v-if="searchUsername">清空</button>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="data-table-wrapper">
      <div class="table-header">
        <h3 class="section-title">👤 用户管理</h3>
        <span class="section-subtitle">所有注册用户的信息与操作</span>
      </div>

      <div class="table-container" v-if="!loading && userList.length > 0">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>用户名</th>
              <th>邮箱</th>
              <th>存储空间</th>
              <th>注册时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in userList" :key="user.id">
              <td class="user-id">{{ user.id }}</td>
              <td class="username">{{ user.username }}</td>
              <td class="email">{{ user.email || '未设置' }}</td>
              <td class="storage">{{ formatStorage(user.file_total_space) }}</td>
              <td class="created-at">{{ formatDate(user.created_at) }}</td>
              <td class="actions">
                <template v-if="!isBuiltInUser(user.username)">
                  <button
                    class="action-btn reset-btn"
                    @click="handleResetPassword(user.id, user.username)"
                    title="重置密码"
                  >
                    重置密码
                  </button>
                  <button
                    class="action-btn delete-btn"
                    @click="handleDeleteUser(user.id, user.username)"
                    title="删除用户"
                  >
                    删除用户
                  </button>
                </template>
                <span v-else class="builtin-tip">内置用户，不可操作</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!loading && userList.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <div class="empty-text">暂无用户数据</div>
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
import { type UserInfo } from "@/utils/api";
import { useAdminStore } from "@/stores/adminStore";
import Loading from "@/components/Loading.vue";
import PageDivision from "./PageDivision.vue";

const adminStore = useAdminStore();

const userList = ref<UserInfo[]>([]);
const totalUsers = ref(0);
const loading = ref(true);
const searchUsername = ref("");
const currentPage = ref(1);
const pageSize = 20;

const isBuiltInUser = (username: string): boolean => {
  const builtIn = ['NodePy-Learning', 'NodePy-Guest', 'admin'];
  return builtIn.includes(username);
};

const totalPages = computed(() => Math.ceil(totalUsers.value / pageSize));

const formatStorage = (bytes: number): string => {
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

const fetchTotalUsers = async () => {
  try {
    const username = searchUsername.value.trim() || null;
    totalUsers.value = await adminStore.getUserNum(username);
  } catch (error) {
    console.error("获取用户总数失败:", error);
    totalUsers.value = 0;
  }
};

const fetchUserList = async () => {
  try {
    const username = searchUsername.value.trim() || null;
    const offset = (currentPage.value - 1) * pageSize;
    const list = await adminStore.getUserList(username, pageSize, offset);
    userList.value = list || [];
  } catch (error) {
    console.error("获取用户列表失败:", error);
    userList.value = [];
  }
};

const refreshData = async () => {
  loading.value = true;
  await fetchTotalUsers();
  await fetchUserList();
  loading.value = false;
};

const handleSearch = async () => {
  if (currentPage.value !== 1) currentPage.value = 1;
  await refreshData();
};

const handleResetSearch = async () => {
  searchUsername.value = "";
  if (currentPage.value !== 1) currentPage.value = 1;
  await refreshData();
};

const goToPage = async (page: number) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  await fetchUserList();
};

const handleResetPassword = async (userId: number, username: string) => {
  if (isBuiltInUser(username)) return;
  const confirmMsg = `确定要重置用户 “${username}” 的密码吗？\n新密码将恢复为默认密码。`;
  if (!window.confirm(confirmMsg)) return;
  await adminStore.resetUserPassword(userId);
  await fetchUserList();
};

const handleDeleteUser = async (userId: number, username: string) => {
  if (isBuiltInUser(username)) return;
  const confirmMsg = `确定要永久删除用户 “${username}” 吗？\n此操作不可恢复！`;
  if (!window.confirm(confirmMsg)) return;
  await adminStore.deleteUserAccount(userId);
  if (userList.value.length === 1 && currentPage.value > 1) currentPage.value--;
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

.user-status-container {
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
}

.search-input-wrapper {
  flex: 2;
  min-width: 200px;
  position: relative;
  display: flex;
  align-items: center;
}

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

.search-actions {
  display: flex;
  gap: 8px;
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
        box-sizing: border-box;  // 关键：使百分比宽度包含 padding
        padding: 12px 12px;
        text-align: left;
        border-bottom: 1px solid $border-light;
      }

      // 非操作列不换行，超出省略号
      td:not(.actions) {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      // 操作列：允许横向滚动，但严格限制宽度
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

      // 列宽分配（总和100%）
      th:nth-child(1), td:nth-child(1) { width: 8%; }
      th:nth-child(2), td:nth-child(2) { width: 15%; }
      th:nth-child(3), td:nth-child(3) { width: 20%; }
      th:nth-child(4), td:nth-child(4) { width: 12%; }
      th:nth-child(5), td:nth-child(5) { width: 20%; }
      th:nth-child(6), td:nth-child(6) { width: 25%; }

      tbody tr {
        transition: background 0.2s ease;

        &:hover {
          background: rgba(16, 142, 254, 0.03);
        }
      }

      .user-id,
      .username,
      .email {
        font-weight: 500;
        color: $text-dark;
      }

      .storage,
      .created-at {
        color: $text-gray;
        font-size: 13px;
      }

      .actions {
        display: flex;
        gap: 8px;
        flex-wrap: nowrap;   // 强制一行
        width: fit-content;   // 内容宽度，用于滚动
        min-width: 100%;      // 确保至少占满列宽（滚动时左侧对齐）
      }

      .action-btn {
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        border: none;
        white-space: nowrap;

        &.reset-btn {
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

      .builtin-tip {
        font-size: 12px;
        background: #e6f0ff;
        color: #1e6fdf;
        padding: 4px 10px;
        border-radius: 20px;
        white-space: nowrap;
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

  .data-table th,
  .data-table td {
    padding: 10px 8px;
    font-size: 12px;
  }
}
</style>