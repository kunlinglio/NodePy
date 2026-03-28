<script lang="ts" setup>
import { computed } from "vue";
import { type SystemHealthResponse } from "@/utils/api";

const props = defineProps<{
  systemHealthStatus: SystemHealthResponse;
}>();

// 获取状态样式
const getStatusStyle = (status: string | undefined) => {
  if (!status) return { color: "#6b7280", bg: "#f3f4f6", icon: "⚪", text: "未知" };
  const s = status.toLowerCase();
  if (s === "healthy") {
    return { color: "#10b981", bg: "#d1fae5", icon: "✅", text: "健康" };
  }
  if (s === "unhealthy") {
    return { color: "#ef4444", bg: "#fee2e2", icon: "❌", text: "异常" };
  }
  return { color: "#f59e0b", bg: "#fed7aa", icon: "⚠️", text: "降级" };
};

// 格式化延迟（毫秒）
const formatLatency = (ms: number | null | undefined): string => {
  if (ms === undefined || ms === null) return "N/A";
  if (ms < 1) return `${(ms * 1000).toFixed(1)} μs`;
  return `${ms.toFixed(2)} ms`;
};

// 格式化百分比
const formatPercent = (value: number | null | undefined): string => {
  if (value === undefined || value === null) return "N/A";
  return `${value.toFixed(1)}%`;
};
</script>

<template>
  <div class="health-container">
    <!-- 整体概览卡片（FastAPI 延迟） -->
    <div class="overview-card">
      <div class="overview-icon">🚀</div>
      <div class="overview-content">
        <div class="overview-title">FastAPI 服务</div>
        <div class="overview-latency">
          {{ formatLatency(systemHealthStatus.fastapi_latency_ms) }}
        </div>
        <div class="overview-label">请求延迟</div>
      </div>
    </div>

    <!-- 各服务卡片网格 -->
    <div class="services-grid">
      <!-- PostgreSQL -->
      <div class="service-card">
        <div class="card-header">
          <div class="service-icon">🐘</div>
          <div class="service-title">PostgreSQL</div>
          <div
            class="status-badge"
            :style="{
              backgroundColor: getStatusStyle(systemHealthStatus.postgres?.status).bg,
              color: getStatusStyle(systemHealthStatus.postgres?.status).color,
            }"
          >
            {{ getStatusStyle(systemHealthStatus.postgres?.status).icon }}
            {{ getStatusStyle(systemHealthStatus.postgres?.status).text }}
          </div>
        </div>
        <div class="card-body">
          <div class="metric-row">
            <span class="metric-label">延迟</span>
            <span class="metric-value">{{ formatLatency(systemHealthStatus.postgres?.latency_ms) }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">活跃连接</span>
            <span class="metric-value">{{ systemHealthStatus.postgres?.active_connections ?? 0 }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">空闲连接</span>
            <span class="metric-value">{{ systemHealthStatus.postgres?.idle_connections ?? 0 }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">总连接数</span>
            <span class="metric-value">{{ systemHealthStatus.postgres?.total_connections ?? 0 }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">数据库大小</span>
            <span class="metric-value">{{ systemHealthStatus.postgres?.database_size ?? "N/A" }}</span>
          </div>
          <div v-if="systemHealthStatus.postgres?.error" class="error-message">
            ⚠️ {{ systemHealthStatus.postgres.error }}
          </div>
        </div>
      </div>

      <!-- Redis -->
      <div class="service-card">
        <div class="card-header">
          <div class="service-icon">⚡</div>
          <div class="service-title">Redis</div>
          <div
            class="status-badge"
            :style="{
              backgroundColor: getStatusStyle(systemHealthStatus.redis?.status).bg,
              color: getStatusStyle(systemHealthStatus.redis?.status).color,
            }"
          >
            {{ getStatusStyle(systemHealthStatus.redis?.status).icon }}
            {{ getStatusStyle(systemHealthStatus.redis?.status).text }}
          </div>
        </div>
        <div class="card-body">
          <div class="metric-row">
            <span class="metric-label">延迟</span>
            <span class="metric-value">{{ formatLatency(systemHealthStatus.redis?.latency_ms) }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">内存使用</span>
            <span class="metric-value">{{ systemHealthStatus.redis?.used_memory_human ?? "N/A" }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">峰值内存</span>
            <span class="metric-value">{{ systemHealthStatus.redis?.peak_memory_human ?? "N/A" }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">命中率</span>
            <span class="metric-value">{{ formatPercent(systemHealthStatus.redis?.hit_rate) }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">客户端连接</span>
            <span class="metric-value">{{ systemHealthStatus.redis?.connected_clients ?? 0 }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">版本</span>
            <span class="metric-value">{{ systemHealthStatus.redis?.version ?? "N/A" }}</span>
          </div>
          <div v-if="systemHealthStatus.redis?.error" class="error-message">
            ⚠️ {{ systemHealthStatus.redis.error }}
          </div>
        </div>
      </div>

      <!-- Celery -->
      <div class="service-card">
        <div class="card-header">
          <div class="service-icon">🍃</div>
          <div class="service-title">Celery</div>
          <div
            class="status-badge"
            :style="{
              backgroundColor: getStatusStyle(systemHealthStatus.celery?.status).bg,
              color: getStatusStyle(systemHealthStatus.celery?.status).color,
            }"
          >
            {{ getStatusStyle(systemHealthStatus.celery?.status).icon }}
            {{ getStatusStyle(systemHealthStatus.celery?.status).text }}
          </div>
        </div>
        <div class="card-body">
          <div class="metric-row">
            <span class="metric-label">延迟</span>
            <span class="metric-value">{{ formatLatency(systemHealthStatus.celery?.latency_ms) }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">活跃任务</span>
            <span class="metric-value">{{ systemHealthStatus.celery?.active_tasks ?? 0 }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">等待任务</span>
            <span class="metric-value">{{ systemHealthStatus.celery?.waiting_tasks ?? 0 }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">撤销任务</span>
            <span class="metric-value">{{ systemHealthStatus.celery?.revoked_tasks ?? 0 }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">工作节点数</span>
            <span class="metric-value">{{ systemHealthStatus.celery?.worker_count ?? 0 }}</span>
          </div>
          <div v-if="systemHealthStatus.celery?.error" class="error-message">
            ⚠️ {{ systemHealthStatus.celery.error }}
          </div>
        </div>
      </div>

      <!-- MinIO -->
      <div class="service-card">
        <div class="card-header">
          <div class="service-icon">📦</div>
          <div class="service-title">MinIO</div>
          <div
            class="status-badge"
            :style="{
              backgroundColor: getStatusStyle(systemHealthStatus.minio?.status).bg,
              color: getStatusStyle(systemHealthStatus.minio?.status).color,
            }"
          >
            {{ getStatusStyle(systemHealthStatus.minio?.status).icon }}
            {{ getStatusStyle(systemHealthStatus.minio?.status).text }}
          </div>
        </div>
        <div class="card-body">
          <div class="metric-row">
            <span class="metric-label">延迟</span>
            <span class="metric-value">{{ formatLatency(systemHealthStatus.minio?.latency_ms) }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">桶数量</span>
            <span class="metric-value">{{ systemHealthStatus.minio?.bucket_count ?? 0 }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">桶列表</span>
            <span class="metric-value metric-list">
              {{ (systemHealthStatus.minio?.buckets || []).join(", ") || "无" }}
            </span>
          </div>
          <div v-if="systemHealthStatus.minio?.error" class="error-message">
            ⚠️ {{ systemHealthStatus.minio.error }}
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

.health-container {
  width: 100%;
  height: 100%;
  background: transparent;
  overflow-y: auto;
  padding: 4px;
}

.overview-card {
  background: $card-white;
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  border: 1px solid $border-light;
  box-shadow: $shadow-sm;
  transition: all 0.2s ease;

  &:hover {
    box-shadow: $shadow-md;
    border-color: rgba(16, 142, 254, 0.2);
  }

  .overview-icon {
    font-size: 48px;
  }

  .overview-content {
    flex: 1;

    .overview-title {
      font-size: 18px;
      font-weight: 600;
      color: $text-dark;
      margin-bottom: 6px;
    }

    .overview-latency {
      font-size: 32px;
      font-weight: 800;
      color: $primary-color;
      line-height: 1.2;
      margin-bottom: 4px;
    }

    .overview-label {
      font-size: 13px;
      color: $text-gray;
    }
  }
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
}

.service-card {
  background: $card-white;
  border-radius: 12px;
  border: 1px solid $border-light;
  box-shadow: $shadow-sm;
  transition: all 0.2s ease;
  overflow: hidden;

  &:hover {
    box-shadow: $shadow-md;
    border-color: rgba(16, 142, 254, 0.2);
    transform: translateY(-2px);
  }

  .card-header {
    padding: 16px 20px;
    background: $bg-light;
    border-bottom: 1px solid $border-light;
    display: flex;
    align-items: center;
    gap: 12px;

    .service-icon {
      font-size: 24px;
    }

    .service-title {
      font-size: 18px;
      font-weight: 700;
      color: $text-dark;
      flex: 1;
    }

    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 500;
      line-height: 1;
    }
  }

  .card-body {
    padding: 16px 20px;
    display: flex;
    flex-direction: column;
    gap: 12px;

    .metric-row {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      font-size: 14px;
      border-bottom: 1px dashed $border-light;
      padding-bottom: 6px;

      .metric-label {
        color: $text-gray;
        font-weight: 500;
      }

      .metric-value {
        color: $text-dark;
        font-weight: 600;
        font-family: monospace;
        text-align: right;
      }

      .metric-list {
        font-family: inherit;
        max-width: 60%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }

    .error-message {
      margin-top: 8px;
      padding: 8px 12px;
      background: #fee2e2;
      border-radius: 8px;
      color: #dc2626;
      font-size: 12px;
      font-weight: 500;
      word-break: break-word;
    }
  }
}

// 响应式
@media (max-width: 768px) {
  .services-grid {
    gap: 16px;
    grid-template-columns: 1fr;
  }

  .overview-card .overview-latency {
    font-size: 28px;
  }

  .service-card .card-body .metric-row .metric-list {
    max-width: 50%;
  }
}
</style>