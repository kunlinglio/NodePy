<template>
  <div class="features-media-grid">
    <div
      v-for="(feature, index) in features"
      :key="index"
      class="feature-media-card"
      :class="`type-${feature.nodeType}`"
      :style="{ backgroundColor: feature.bgColor }"
    >
      <div class="feature-info">
        <div class="feature-header">
          <div class="feature-icon">
            <svg-icon :path="feature.icon" :size="24" type="mdi"></svg-icon>
          </div>
          <h3>{{ feature.title }}</h3>
        </div>
        <p>{{ feature.description }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
//@ts-ignore
import SvgIcon from '@jamescoyle/vue-icon';
import {
  mdiGraph,
  mdiTableLarge,
  mdiChartScatterPlot,
  mdiFunctionVariant,
  mdiBrain,
  mdiTextSearch,
  mdiCalendarClock,
  mdiFileDocumentMultiple,
} from '@mdi/js';

interface Feature {
  icon: string;
  title: string;
  description: string;
  nodeType: string;
  bgColor: string;
}

const features: Feature[] = [
  {
    icon: mdiGraph,
    title: '严格类型系统',
    description: '  支持 Int、Float、Bool、String、Table、File、Datetime 七大类型，确保数据流转准确性。',
    nodeType: 'input',
    bgColor: '#2563eb'
  },
  {
    icon: mdiTableLarge,
    title: 'Pandas 表格处理',
    description: '  内置强大的表格处理能力，支持过滤、去重、缺失值处理、列运算等复杂操作。',
    nodeType: 'tableProcess',
    bgColor: '#3b82f6'
  },
  {
    icon: mdiChartScatterPlot,
    title: '专业可视化',
    description: '  支持散点图、折线图、柱状图、面积图、K线图等多种专业金融图表绘制。',
    nodeType: 'visualize',
    bgColor: '#8b5cf6'
  },
  {
    icon: mdiFunctionVariant,
    title: 'Python 驱动',
    description: '  底层完全由 Python 驱动，兼容 Python 生态，计算结果精准可靠。',
    nodeType: 'compute',
    bgColor: '#06b6d4'
  },
  {
    icon: mdiBrain,
    title: '机器学习支持',
    description: '  集成 scikit-learn，支持线性回归、逻辑回归等多种机器学习算法。',
    nodeType: 'machineLearning',
    bgColor: '#ec4899'
  },
  {
    icon: mdiTextSearch,
    title: '文本处理',
    description: '  内置分词、正则匹配、情感分析等强大的文本处理能力。',
    nodeType: 'stringProcess',
    bgColor: '#f59e0b'
  },
  {
    icon: mdiCalendarClock,
    title: '时间序列',
    description: '  完整的时间序列数据处理能力，支持日期计算、移动窗口等操作。',
    nodeType: 'datetimeProcess',
    bgColor: '#10b981'
  },
  {
    icon: mdiFileDocumentMultiple,
    title: '文件系统',
    description: '  支持 CSV、Excel、JSON 等多种文件格式的导入导出，配额管理更安全。',
    nodeType: 'file',
    bgColor: '#6b7280'
  }
];
</script>

<style scoped lang="scss">
.features-media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 28px;
}

.feature-media-card {
  border-radius: 24px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.2, 0, 0, 1);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border: none;
  color: white;
  height: 180px; // 固定高度，确保所有卡片大小一致
  display: flex;
  flex-direction: column;

  &:hover {
    transform: translateY(-6px);
    box-shadow: 0 20px 30px -12px rgba(0,0,0,0.25);
  }

  .feature-info {
    padding: 24px 20px 20px 20px;
    flex: 1;
    display: flex;
    flex-direction: column;

    .feature-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;
    }

    .feature-icon {
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.2);
      color: white;
      flex-shrink: 0;
    }

    h3 {
      font-size: 1.2rem;
      font-weight: 700;
      margin: 0;
      color: white;
    }

    p {
      color: rgba(255, 255, 255, 0.9);
      line-height: 1.5;
      font-size: 0.85rem;
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
      margin: 0;
    }
  }
}
</style>