<script lang="ts" setup>
import { computed, ref } from "vue";
import { type FinancialSymbolStats } from "@/utils/api";

const props = defineProps<{
  financialStatus: Array<FinancialSymbolStats>;
}>();

// 分页配置
const currentPage = ref(1);
const pageSize = ref(10);

// 格式化时间戳（兼容 number | string | null）
const formatTimestamp = (timestamp: number | string | null): string => {
  if (timestamp === null || timestamp === undefined) return "暂无数据";
  const numTimestamp = typeof timestamp === "string" ? parseInt(timestamp, 10) : timestamp;
  if (isNaN(numTimestamp)) return "无效时间戳";
  const date = new Date(numTimestamp * 1000);
  return date.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

// 统计卡片数据
const stats = computed(() => {
  const total = props.financialStatus.length;
  const completedCount = props.financialStatus.filter(item => item.completed).length;
  const cryptoCount = props.financialStatus.filter(item => item.type === "crypto").length;
  const stockCount = props.financialStatus.filter(item => item.type === "stock").length;

  return [
    {
      title: "总数据条目",
      value: total,
      icon: "📋",
      color: "#108efe",
    },
    {
      title: "已完成同步",
      value: completedCount,
      suffix: `/${total}`,
      icon: "✅",
      color: "#10b981",
    },
    {
      title: "加密货币",
      value: cryptoCount,
      icon: "₿",
      color: "#f59e0b",
    },
    {
      title: "股票",
      value: stockCount,
      icon: "📈",
      color: "#8b5cf6",
    },
  ];
});

// 类型标签样式
const getTypeStyle = (type: string) => {
  if (type === "crypto") {
    return { backgroundColor: "#fef3c7", color: "#d97706", label: "加密货币" };
  }
  return { backgroundColor: "#e0f2fe", color: "#0284c7", label: "股票" };
};

// 状态标签样式
const getStatusStyle = (completed: boolean) => {
  if (completed) {
    return { backgroundColor: "#d1fae5", color: "#059669", label: "已完成" };
  }
  return { backgroundColor: "#fee2e2", color: "#dc2626", label: "未完成" };
};

// 原始数据
const allData = computed(() => props.financialStatus || []);

// 分页后的数据
const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return allData.value.slice(start, end);
});

// 总页数
const totalPages = computed(() => Math.ceil(allData.value.length / pageSize.value));

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

// 生成页码数组（带省略号）
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
  <div class="financial-container">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div
        v-for="(card, idx) in stats"
        :key="idx"
        class="stat-card"
        :style="{ '--card-accent': card.color }"
      >
        <div class="card-icon" :style="{ backgroundColor: card.color + '10' }">
          <span class="icon-emoji">{{ card.icon }}</span>
        </div>
        <div class="card-content">
          <div class="card-title">{{ card.title }}</div>
          <div class="card-value">
            {{ card.value }}
            <span v-if="card.suffix" class="card-suffix">{{ card.suffix }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="data-table-wrapper">
      <div class="table-header">
        <h3 class="section-title">📊 财务数据同步状态</h3>
        <span class="section-subtitle">各金融品种的历史数据同步情况</span>
      </div>

      <div class="table-container" v-if="allData.length > 0">
        <table class="data-table">
          <thead>
            <tr>
              <th>交易品种</th>
              <th>类型</th>
              <th>同步状态</th>
              <th>最早可用数据</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in paginatedData" :key="idx">
              <td class="symbol">{{ item.symbol }}</td>
              <td>
                <span
                  class="badge type-badge"
                  :style="{
                    backgroundColor: getTypeStyle(item.type).backgroundColor,
                    color: getTypeStyle(item.type).color,
                  }"
                >
                  {{ getTypeStyle(item.type).label }}
                </span>
              </td>
              <td>
                <span
                  class="badge status-badge"
                  :style="{
                    backgroundColor: getStatusStyle(item.completed).backgroundColor,
                    color: getStatusStyle(item.completed).color,
                  }"
                >
                  {{ getStatusStyle(item.completed).label }}
                </span>
              </td>
              <td class="timestamp">
                {{ formatTimestamp(item.oldest_data) }}
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

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <div class="empty-icon">📭</div>
        <div class="empty-text">暂无财务数据</div>
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

.financial-container {
  width: 100%;
  height: 100%;
  background: transparent;
  overflow-y: auto;
  padding: 4px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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

      .card-suffix {
        font-size: 16px;
        font-weight: 500;
        color: $text-gray;
        margin-left: 4px;
      }
    }
  }
}

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

      .symbol {
        font-weight: 600;
        color: $text-dark;
        font-family: monospace;
        font-size: 14px;
      }

      .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        line-height: 1.2;
      }

      .timestamp {
        font-size: 13px;
        color: $text-gray;
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

  .data-table th,
  .data-table td {
    padding: 12px 12px;
  }

  .badge {
    font-size: 11px;
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