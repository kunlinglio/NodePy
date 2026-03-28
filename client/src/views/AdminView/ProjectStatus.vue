<script lang="ts" setup>
import { computed } from "vue";
import { type ProjectStats } from "@/utils/api";

const props = defineProps<{
  projectStatus: ProjectStats;
}>();

// 统计卡片数据
const projectCards = computed(() => [
  {
    title: "总项目数",
    value: props.projectStatus.total_projects,
    icon: "📁",
    color: "#108efe",
    description: "所有创建的项目",
  },
  {
    title: "探索项目",
    value: props.projectStatus.explore_projects,
    icon: "🔍",
    color: "#10b981",
    description: "公开可探索的项目",
  },
  {
    title: "近期更新",
    value: props.projectStatus.recent_updates,
    icon: "🔄",
    color: "#f59e0b",
    description: "近7天有更新的项目",
  },
]);
</script>

<template>
  <div class="project-container">
    <!-- 统计卡片网格 -->
    <div class="stats-grid">
      <div
        v-for="(card, idx) in projectCards"
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
          <div class="card-description">{{ card.description }}</div>
        </div>
      </div>
    </div>

    <!-- 项目统计概览（可选） -->
    <div class="summary-section">
      <div class="summary-header">
        <h3 class="summary-title">📊 项目概览</h3>
        <p class="summary-subtitle">基于当前项目数据的统计摘要</p>
      </div>
      <div class="summary-stats">
        <div class="summary-item">
          <span class="summary-label">探索项目占比</span>
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{
                width: (props.projectStatus.explore_projects / props.projectStatus.total_projects * 100) + '%',
                backgroundColor: '#108efe'
              }"
            ></div>
          </div>
          <span class="summary-value">
            {{ ((props.projectStatus.explore_projects / props.projectStatus.total_projects) * 100).toFixed(1) }}%
          </span>
        </div>
        <div class="summary-item">
          <span class="summary-label">近期更新活跃度</span>
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{
                width: (props.projectStatus.recent_updates / props.projectStatus.total_projects * 100) + '%',
                backgroundColor: '#f59e0b'
              }"
            ></div>
          </div>
          <span class="summary-value">
            {{ ((props.projectStatus.recent_updates / props.projectStatus.total_projects) * 100).toFixed(1) }}%
          </span>
        </div>
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

.project-container {
  width: 100%;
  height: 100%;
  background: transparent;
  overflow-y: auto;
  padding: 4px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: $card-white;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: flex-start;
  gap: 20px;
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
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.2s ease;
    flex-shrink: 0;

    .icon-emoji {
      font-size: 28px;
    }
  }

  .card-content {
    flex: 1;

    .card-title {
      font-size: 14px;
      font-weight: 500;
      color: $text-gray;
      margin-bottom: 8px;
      letter-spacing: 0.3px;
    }

    .card-value {
      font-size: 36px;
      font-weight: 800;
      color: $text-dark;
      line-height: 1.2;
      margin-bottom: 6px;
    }

    .card-description {
      font-size: 12px;
      color: $text-gray;
    }
  }
}

.summary-section {
  background: $card-white;
  border-radius: 12px;
  border: 1px solid $border-light;
  box-shadow: $shadow-sm;
  padding: 24px;
  transition: all 0.2s ease;

  &:hover {
    box-shadow: $shadow-md;
  }

  .summary-header {
    margin-bottom: 20px;

    .summary-title {
      font-size: 18px;
      font-weight: 700;
      color: $text-dark;
      margin: 0 0 4px 0;
    }

    .summary-subtitle {
      font-size: 13px;
      color: $text-gray;
    }
  }

  .summary-stats {
    display: flex;
    flex-direction: column;
    gap: 20px;

    .summary-item {
      display: flex;
      align-items: center;
      gap: 16px;

      .summary-label {
        width: 120px;
        font-size: 14px;
        font-weight: 500;
        color: $text-dark;
      }

      .progress-bar {
        flex: 1;
        height: 8px;
        background: $bg-light;
        border-radius: 10px;
        overflow: hidden;

        .progress-fill {
          height: 100%;
          border-radius: 10px;
          transition: width 0.3s ease;
        }
      }

      .summary-value {
        width: 60px;
        font-size: 14px;
        font-weight: 600;
        color: $text-dark;
        text-align: right;
      }
    }
  }
}

// 响应式
@media (max-width: 768px) {
  .stats-grid {
    gap: 16px;
  }

  .stat-card {
    padding: 20px;

    .card-icon {
      width: 48px;
      height: 48px;

      .icon-emoji {
        font-size: 24px;
      }
    }

    .card-value {
      font-size: 28px;
    }
  }

  .summary-stats .summary-item {
    .summary-label {
      width: 100px;
    }
  }
}
</style>