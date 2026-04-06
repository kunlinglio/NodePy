<template>
  <div class="review-status-container">
    <!-- 统计卡片：教程总数 -->
    <div class="stats-grid">
      <div class="stat-card" style="--card-accent: #108efe">
        <div class="card-icon" style="background-color: #108efe10">
          <span class="icon-emoji">📚</span>
        </div>
        <div class="card-content">
          <div class="card-title">教程总数</div>
          <div class="card-value">{{ totalTutorials }}</div>
        </div>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="data-table-wrapper">
      <div class="table-header">
        <h3 class="section-title">👍 教程评价统计</h3>
        <span class="section-subtitle">各教程的点赞、点踩数据</span>
      </div>

      <div class="table-container" v-if="!loading && tutorialList.length > 0">
        <table class="data-table">
          <thead>
            <tr>
              <th>教程 ID</th>
              <th>点赞数</th>
              <th>点踩数</th>
              <th>总数</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in tutorialList" :key="item.tutorial_id">
              <td class="tutorial-id">{{ item.tutorial_id }}</td>
              <td class="likes">{{ item.likes }}</td>
              <td class="dislikes">{{ item.dislikes }}</td>
              <td class="total">{{ item.total }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!loading && tutorialList.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <div class="empty-text">暂无教程评价数据</div>
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
import { type TutorialReviewStats } from "@/utils/api";
import { useAdminStore } from "@/stores/adminStore";
import Loading from "@/components/Loading.vue";
import PageDivision from "./PageDivision.vue";

const adminStore = useAdminStore();

const tutorialList = ref<TutorialReviewStats[]>([]);
const totalTutorials = ref(0);
const loading = ref(true);
const currentPage = ref(1);
const pageSize = 20; // 每页20条

// 总页数
const totalPages = computed(() => Math.ceil(totalTutorials.value / pageSize));

// 获取教程总数
const fetchTotal = async () => {
  try {
    // 不传 tutorialId 获取所有教程的数量
    totalTutorials.value = await adminStore.getTutorialNum(null);
  } catch (error) {
    console.error("获取教程总数失败:", error);
    totalTutorials.value = 0;
  }
};

// 获取教程评价列表（分页）
const fetchList = async () => {
  try {
    const offset = (currentPage.value - 1) * pageSize;
    const list = await adminStore.getTutorialReview(null, pageSize, offset);
    tutorialList.value = list || [];
  } catch (error) {
    console.error("获取教程评价列表失败:", error);
    tutorialList.value = [];
  }
};

// 刷新所有数据
const refreshData = async () => {
  loading.value = true;
  await fetchTotal();
  await fetchList();
  loading.value = false;
};

// 跳转页面
const goToPage = async (page: number) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  await fetchList();
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

.review-status-container {
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
        box-sizing: border-box;
        padding: 12px 12px;
        text-align: left;
        border-bottom: 1px solid $border-light;
      }

      td {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
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
      th:nth-child(1), td:nth-child(1) { width: 25%; }  // 教程 ID
      th:nth-child(2), td:nth-child(2) { width: 25%; }  // 点赞数
      th:nth-child(3), td:nth-child(3) { width: 25%; }  // 点踩数
      th:nth-child(4), td:nth-child(4) { width: 25%; }  // 总数

      tbody tr {
        transition: background 0.2s ease;

        &:hover {
          background: rgba(16, 142, 254, 0.03);
        }
      }

      .tutorial-id,
      .likes,
      .dislikes,
      .total {
        font-weight: 500;
        color: $text-dark;
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