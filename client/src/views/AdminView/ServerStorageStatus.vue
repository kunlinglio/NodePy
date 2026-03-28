<script lang="ts" setup>
import { computed, ref } from "vue";
import { type StorageStats } from "@/utils/api";

const props = defineProps<{
  serverStorageStatus: StorageStats;
}>();

// 分页配置
const currentPage = ref(1);
const pageSize = ref(10);

// 格式化存储字节为易读单位
const formatStorage = (bytes: number): string => {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  const value = bytes / Math.pow(k, i);
  return `${value.toFixed(1)} ${sizes[i]}`;
};

// 统计卡片数据
const storageCards = computed(() => [
  {
    title: "总存储空间",
    value: formatStorage(props.serverStorageStatus.total_storage_bytes),
    icon: "💾",
    color: "#108efe",
  },
  {
    title: "访客存储",
    value: formatStorage(props.serverStorageStatus.guest_storage_bytes),
    icon: "👤",
    color: "#10b981",
  },
  {
    title: "示例存储",
    value: formatStorage(props.serverStorageStatus.example_storage_bytes),
    icon: "📚",
    color: "#f59e0b",
  },
]);

// 原始用户列表
const allUsers = computed(() => props.serverStorageStatus.top_users || []);

// 分页后的用户列表
const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return allUsers.value.slice(start, end);
});

// 总页数
const totalPages = computed(() => Math.ceil(allUsers.value.length / pageSize.value));

// 页码切换
const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
};

// 上一页
const prevPage = () => goToPage(currentPage.value - 1);

// 下一页
const nextPage = () => goToPage(currentPage.value + 1);

// 生成页码数组（简单版，可扩展）
const pageNumbers = computed(() => {
  const total = totalPages.value;
  const current = currentPage.value;
  const delta = 2;
  const range: any[] = [];
  const rangeWithDots: any[] = [];
  let l;

  for (let i = 1; i <= total; i++) {
    if (i === 1 || i === total || (i >= current - delta && i <= current + delta)) {
      range.push(i);
    }
  }

  range.forEach((i) => {
    if (l) {
      if (i - l === 2) {
        rangeWithDots.push(l + 1);
      } else if (i - l !== 1) {
        rangeWithDots.push('...');
      }
    }
    rangeWithDots.push(i);
    l = i;
  });
  return rangeWithDots;
});
</script>

<template>
  <div class="server-storage-container">
    <!-- 存储概览卡片 -->
    <div class="stats-grid">
      <div
        v-for="(card, idx) in storageCards"
        :key="idx"
        class="stat-card"
        :style="{ '--card-accent': card.color }"
      >
        <div class="card-icon" :style="{ backgroundColor: card.color + '10' }">
          <span class="icon-emoji">{{ card.icon }}</span>
        </div>
        <div class="card-content">
          <div class="card-title">{{ card.title }}</div>
          <div class="card-value">{{ card.value }}</div>
        </div>
      </div>
    </div>

    <!-- Top 用户表格 -->
    <div class="users-section">
      <div class="section-header">
        <h3 class="section-title">📊 存储用量 Top 用户</h3>
        <span class="section-subtitle">按存储使用量排序</span>
      </div>

      <div class="table-wrapper" v-if="allUsers.length > 0">
        <table class="users-table">
          <thead>
            <tr>
              <th>排名</th>
              <th>用户 ID</th>
              <th>用户名</th>
              <th>存储用量</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(user, idx) in paginatedUsers" :key="user.user_id">
              <td class="rank">
                <span
                  class="rank-badge"
                  :class="{
                    'rank-1': (currentPage - 1) * pageSize + idx + 1 === 1,
                    'rank-2': (currentPage - 1) * pageSize + idx + 1 === 2,
                    'rank-3': (currentPage - 1) * pageSize + idx + 1 === 3,
                  }"
                >
                  {{ (currentPage - 1) * pageSize + idx + 1 }}
                </span>
              </td>
              <td class="user-id">{{ user.user_id }}</td>
              <td class="username">{{ user.username }}</td>
              <td class="storage">
                <span class="storage-value">{{ formatStorage(user.storage_used) }}</span>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- 分页组件 -->
        <div class="pagination" v-if="totalPages > 1">
          <button
            class="page-btn"
            :disabled="currentPage === 1"
            @click="prevPage"
            aria-label="上一页"
          >
            <span class="btn-icon">‹</span>
          </button>

          <template v-for="(page, index) in pageNumbers" :key="index">
            <button
              v-if="page === '...'"
              class="page-dots"
              disabled
            >
              ...
            </button>
            <button
              v-else
              class="page-btn"
              :class="{ active: currentPage === page }"
              @click="goToPage(Number(page))"
            >
              {{ page }}
            </button>
          </template>

          <button
            class="page-btn"
            :disabled="currentPage === totalPages"
            @click="nextPage"
            aria-label="下一页"
          >
            <span class="btn-icon">›</span>
          </button>
        </div>
      </div>
      <div v-else class="empty-state">
        <div class="empty-icon">📭</div>
        <div class="empty-text">暂无用户数据</div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
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
    background: rgba(16, 142, 254, 0.1);
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

.users-section {
  background: $card-white;
  border-radius: 12px;
  border: 1px solid $border-light;
  box-shadow: $shadow-sm;
  overflow: hidden;
  transition: all 0.2s ease;

  &:hover {
    box-shadow: $shadow-md;
  }

  .section-header {
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

  .table-wrapper {
    overflow-x: auto;
    padding: 0 4px 4px 4px;

    .users-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;

      th,
      td {
        padding: 14px 16px;
        text-align: left;
        border-bottom: 1px solid $border-light;
      }

      th {
        background: $bg-light;
        font-weight: 600;
        color: $text-dark;
        font-size: 13px;
        letter-spacing: 0.3px;
      }

      tbody tr {
        transition: background 0.2s ease;

        &:hover {
          background: rgba(16, 142, 254, 0.03);
        }
      }

      .rank {
        width: 70px;

        .rank-badge {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 28px;
          height: 28px;
          border-radius: 8px;
          background: $bg-light;
          color: $text-gray;
          font-weight: 600;
          font-size: 13px;

          &.rank-1 {
            background: #fef3c7;
            color: #d97706;
          }

          &.rank-2 {
            background: #e6f7e6;
            color: #10b981;
          }

          &.rank-3 {
            background: #e0f2fe;
            color: #0284c7;
          }
        }
      }

      .user-id {
        font-family: monospace;
        font-size: 13px;
        color: $text-gray;
      }

      .username {
        font-weight: 500;
        color: $text-dark;
      }

      .storage {
        .storage-value {
          font-weight: 600;
          color: $primary-color;
          background: rgba(16, 142, 254, 0.08);
          padding: 4px 10px;
          border-radius: 12px;
          font-size: 13px;
          display: inline-block;
        }
      }
    }

    .pagination {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 8px;
      padding: 16px 20px;
      border-top: 1px solid $border-light;
      flex-wrap: wrap;

      .page-btn {
        min-width: 36px;
        height: 36px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0 8px;
        border-radius: 6px;
        background: transparent;
        border: 1px solid $border-light;
        font-size: 14px;
        font-weight: 500;
        color: $text-gray;
        cursor: pointer;
        transition: all 0.2s ease;

        &:hover:not(:disabled) {
          background: rgba(16, 142, 254, 0.08);
          border-color: $primary-color;
          color: $primary-color;
          transform: translateY(-1px);
        }

        &:active:not(:disabled) {
          transform: translateY(0);
        }

        &:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }

        &.active {
          background: $primary-color;
          border-color: $primary-color;
          color: white;
          box-shadow: 0 2px 6px rgba(16, 142, 254, 0.2);
        }

        .btn-icon {
          font-size: 18px;
          line-height: 1;
        }
      }

      .page-dots {
        min-width: 36px;
        height: 36px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        color: $text-gray;
        cursor: default;
        background: transparent;
        border: none;
      }
    }
  }
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
  background: $card-white;

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

// 滚动条美化
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

// 响应式
@media (max-width: 768px) {
  .stats-grid {
    gap: 16px;
  }

  .stat-card {
    padding: 16px;

    .card-icon {
      width: 44px;
      height: 44px;

      .icon-emoji {
        font-size: 22px;
      }
    }

    .card-value {
      font-size: 24px;
    }
  }

  .users-table th,
  .users-table td {
    padding: 12px 12px;
  }

  .users-table .rank {
    width: 50px;
  }

  .pagination {
    gap: 4px;
    .page-btn {
      min-width: 32px;
      height: 32px;
      font-size: 13px;
    }
  }
}
</style>