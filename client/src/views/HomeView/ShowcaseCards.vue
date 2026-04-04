<template>
  <div class="gallery-container">
    <div class="gallery-wrapper">
      <div 
        ref="trackRef"
        class="gallery-track"
        :style="{ transform: `translateX(${offsetX}px)` }"
      >
        <!-- 原始卡片列表 -->
        <div
          v-for="(card, index) in cards"
          :key="`original-${index}`"
          class="gallery-card"
          @click="jumpToExample(card)"
        >
          <div :class="['card-img', card.gradientClass]"></div>
          <div class="card-info">
            <h3>{{ card.title }}</h3>
            <p>{{ card.description }}</p>
            <div class="card-tags">
              <span v-for="tag in card.tags" :key="tag">{{ tag }}</span>
            </div>
          </div>
        </div>
        <!-- 克隆卡片列表（用于实现无缝循环） -->
        <div
          v-for="(card, index) in cards"
          :key="`clone-${index}`"
          class="gallery-card"
          @click="jumpToExample(card)"
        >
          <div :class="['card-img', card.gradientClass]"></div>
          <div class="card-info">
            <h3>{{ card.title }}</h3>
            <p>{{ card.description }}</p>
            <div class="card-tags">
              <span v-for="tag in card.tags" :key="tag">{{ tag }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

interface Card {
  title: string;
  description: string;
  tags: string[];
  gradientClass: string;
}

const cards: Card[] = [
  {
    title: '量化选股策略',
    description: '多因子选股 + 回测分析，一键生成绩效报告',
    tags: ['机器学习', '回测'],
    gradientClass: 'gradient-1',
  },
  {
    title: '高频数据处理',
    description: 'Tick级数据清洗、聚合、特征工程流水线',
    tags: ['实时计算', '大数据'],
    gradientClass: 'gradient-2',
  },
  {
    title: '风险敞口分析',
    description: '投资组合风险度量，VaR/CVaR 计算可视化',
    tags: ['风险管理', '可视化'],
    gradientClass: 'gradient-3',
  },
  {
    title: '因子挖掘平台',
    description: '自动化因子挖掘 + IC分析，快速筛选有效因子',
    tags: ['因子分析', '自动化'],
    gradientClass: 'gradient-4',
  },
  {
    title: '舆情情绪分析',
    description: '新闻与社交媒体情绪评分，构建情绪因子',
    tags: ['NLP', '情绪指标'],
    gradientClass: 'gradient-5',
  },
  {
    title: '智能订单执行',
    description: 'TWAP/VWAP算法拆单，降低冲击成本',
    tags: ['算法交易', '执行优化'],
    gradientClass: 'gradient-6',
  },
];

const trackRef = ref<HTMLElement | null>(null);
const offsetX = ref(0);
const totalWidth = ref(0);
let animationId: number | null = null;
let lastTimestamp = 0;

// 降低滚动速度：原来150，现在80像素/秒（更平滑）
const scrollSpeed = 80;

// 更新原始卡片组总宽度
const updateTotalWidth = () => {
  if (!trackRef.value) return;
  
  const cardsElements = trackRef.value.querySelectorAll('.gallery-card');
  const originalCardsCount = cards.length;
  
  if (cardsElements.length >= originalCardsCount) {
    let total = 0;
    for (let i = 0; i < originalCardsCount; i++) {
      const card = cardsElements[i] as HTMLElement;
      total += card.offsetWidth;
      const gap = parseFloat(getComputedStyle(trackRef.value!).gap);
      if (i < originalCardsCount - 1) total += gap;
    }
    totalWidth.value = total;
    
    // 修正偏移量，保证在有效范围内（-totalWidth ~ 0）
    if (offsetX.value <= -totalWidth.value) {
      offsetX.value += totalWidth.value;
    } else if (offsetX.value > 0) {
      offsetX.value -= totalWidth.value;
    }
  }
};

// 基于时间差的自动滚动动画（永不暂停）
const scrollByTime = (timestamp: number) => {
  if (lastTimestamp === 0) {
    lastTimestamp = timestamp;
    animationId = requestAnimationFrame(scrollByTime);
    return;
  }
  
  const deltaTime = Math.min(timestamp - lastTimestamp, 100);
  if (deltaTime > 0 && totalWidth.value > 0) {
    const step = (scrollSpeed * deltaTime) / 1000; // 像素偏移
    let newOffset = offsetX.value - step; // 向左滚动
    
    // 无缝循环：当偏移超出左侧边界时，直接加上总宽度
    if (newOffset <= -totalWidth.value) {
      newOffset += totalWidth.value;
    } else if (newOffset > 0) {
      newOffset -= totalWidth.value;
    }
    offsetX.value = newOffset;
  }
  
  lastTimestamp = timestamp;
  animationId = requestAnimationFrame(scrollByTime);
};

// 启动自动滚动（挂载时启动，永不停止）
const startAutoScroll = () => {
  if (animationId !== null) return;
  lastTimestamp = 0;
  animationId = requestAnimationFrame(scrollByTime);
};

const jumpToExample = (card: Card) => {
  router.push({ name: 'example', query: { title: card.title } });
};

let resizeObserver: ResizeObserver | null = null;
onMounted(() => {
  startAutoScroll();
  updateTotalWidth();
  
  if (trackRef.value) {
    resizeObserver = new ResizeObserver(() => {
      updateTotalWidth();
    });
    resizeObserver.observe(trackRef.value);
  }
  
  window.addEventListener('resize', updateTotalWidth);
});

onBeforeUnmount(() => {
  if (animationId) {
    cancelAnimationFrame(animationId);
    animationId = null;
  }
  if (resizeObserver) {
    resizeObserver.disconnect();
  }
  window.removeEventListener('resize', updateTotalWidth);
});

watch(() => cards.length, () => {
  updateTotalWidth();
});
</script>

<style scoped lang="scss">
.gallery-container {
  position: relative;
  width: 100%;
  overflow: hidden;
}

.gallery-wrapper {
  width: 100%;
  overflow: hidden;
}

.gallery-track {
  display: flex;
  gap: 28px;
  will-change: transform;
}

.gallery-card {
  flex-shrink: 0;
  width: 300px;
  background: white;
  border-radius: 24px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
  
  &:hover {
    transform: translateY(-6px);
    box-shadow: 0 20px 25px -12px rgba(0, 0, 0, 0.1);
  }
  
  .card-img {
    height: 160px;
    background-size: cover;
    background-position: center;
  }
  
  .gradient-1 { background: linear-gradient(135deg, #3b82f6, #8b5cf6); }
  .gradient-2 { background: linear-gradient(135deg, #06b6d4, #3b82f6); }
  .gradient-3 { background: linear-gradient(135deg, #f59e0b, #ef4444); }
  .gradient-4 { background: linear-gradient(135deg, #10b981, #34d399); }
  .gradient-5 { background: linear-gradient(135deg, #ec489a, #f472b6); }
  .gradient-6 { background: linear-gradient(135deg, #6366f1, #818cf8); }
  
  .card-info {
    padding: 20px;
    
    h3 {
      font-weight: 700;
      margin-bottom: 8px;
      font-size: 1.2rem;
      color: #0f172a;
    }
    
    p {
      font-size: 0.85rem;
      color: #475569;
      margin-bottom: 12px;
      line-height: 1.4;
    }
    
    .card-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      
      span {
        background: #f1f5f9;
        padding: 4px 8px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 500;
        color: #1e293b;
      }
    }
  }
}

/* 响应式调整卡片宽度 */
@media (max-width: 768px) {
  .gallery-card {
    width: 260px;
  }
  .gallery-track {
    gap: 20px;
  }
}

@media (max-width: 480px) {
  .gallery-card {
    width: 240px;
  }
}
</style>