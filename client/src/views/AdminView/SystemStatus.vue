<script lang="ts" setup>
import { computed } from "vue";
import { type SystemStatsResponse } from "@/utils/api";

const props = defineProps<{
  systemStatus: SystemStatsResponse;
}>();

// 格式化存储字节为易读单位
const formatStorage = (bytes: number): string => {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  const value = bytes / Math.pow(k, i);
  return `${value.toFixed(1)} ${sizes[i]}`;
};

// 指标卡片配置
const statsCards = computed(() => [
  {
    title: "总用户数",
    value: props.systemStatus.total_users,
    unit: "人",
    icon: "👥",
    color: "#108efe",
  },
  {
    title: "总项目数",
    value: props.systemStatus.total_projects,
    unit: "个",
    icon: "📁",
    color: "#10b981",
  },
  {
    title: "总存储量",
    value: formatStorage(props.systemStatus.total_storage_bytes),
    unit: "",
    icon: "💾",
    color: "#f59e0b",
  },
  {
    title: "节点输出总数",
    value: props.systemStatus.total_nodes_output,
    unit: "条",
    icon: "📊",
    color: "#8b5cf6",
  },
]);
</script>

<template>
  <div class="system-status-container">
    <div class="stats-grid">
      <div
        v-for="(card, idx) in statsCards"
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
            <span v-if="card.unit" class="card-unit">{{ card.unit }}</span>
          </div>
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

.system-status-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  width: 100%;
  padding: 8px;
}

.stat-card {
  background: $card-white;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
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
    background: rgba(16, 142, 254, 0.1);
    transition: transform 0.2s ease;

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
      font-size: 32px;
      font-weight: 800;
      color: $text-dark;
      line-height: 1.2;
      display: flex;
      align-items: baseline;
      flex-wrap: wrap;
      gap: 4px;

      .card-unit {
        font-size: 14px;
        font-weight: 500;
        color: $text-gray;
        margin-left: 4px;
      }
    }
  }
}

// 响应式调整
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
}
</style>