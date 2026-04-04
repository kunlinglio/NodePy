<template>
  <div class="ecosystem-carousel">
    <div class="cylinder-carousel-wrapper"
         @mouseenter="pauseEcoAuto"
         @mouseleave="resumeEcoAuto">
      <button class="carousel-arrow left-arrow" @click="prevEco">
        <svg-icon :path="mdiChevronLeft" :size="32" />
      </button>
      <div class="cylinder-container">
        <div class="cylinder-stage">
          <div class="cylinder-carousel"
               :style="{ transform: `rotateY(${currentEcoAngle}deg)` }">
            <div v-for="(item, idx) in ecosystemItems"
                 :key="idx"
                 class="cylinder-card"
                 :style="{ transform: `rotateY(${idx * 60}deg) translateZ(420px)` }">
              <div class="card-inner">
                <div class="eco-icon">
                  <svg-icon :path="item.icon" :size="44" />
                </div>
                <h4>{{ item.title }}</h4>
                <p>{{ item.description }}</p>
                <div class="card-glow"></div>
              </div>
            </div>
          </div>
        </div>
        <div class="cylinder-mask mask-left"></div>
        <div class="cylinder-mask mask-right"></div>
      </div>
      <button class="carousel-arrow right-arrow" @click="nextEco">
        <svg-icon :path="mdiChevronRight" :size="32" />
      </button>
    </div>
    <div class="cylinder-indicators">
      <span v-for="(_, idx) in ecosystemItems"
            :key="idx"
            class="cylinder-dot"
            :class="{ active: currentEcoIndex === idx }"
            @click="rotateToEcoIndex(idx)"></span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
//@ts-ignore
import SvgIcon from '@jamescoyle/vue-icon';
import {
  mdiDatabase,
  mdiTune,
  mdiChartLine,
  mdiRobot,
  mdiVectorPolygon,
  mdiCellphoneLink,
  mdiChevronLeft,
  mdiChevronRight
} from '@mdi/js';

const ecosystemItems = [
  { icon: mdiDatabase, title: '数据接入', description: '支持股票、加密货币、宏观经济数据等实时/历史数据源' },
  { icon: mdiTune, title: '数据清洗', description: '缺失值处理、异常检测、数据标准化、去重聚合' },
  { icon: mdiChartLine, title: '技术指标', description: '内置MACD、RSI、布林带等50+种技术分析指标' },
  { icon: mdiRobot, title: '机器学习', description: '回归、分类、聚类算法，支持模型训练与评估' },
  { icon: mdiVectorPolygon, title: '策略回测', description: '事件驱动回测框架，精准评估策略表现' },
  { icon: mdiCellphoneLink, title: '实时监控', description: 'WebSocket实时行情接入，策略信号实时推送' }
];

const currentEcoAngle = ref(0);
let ecoAutoTimer: NodeJS.Timeout | null = null;
const isEcoHovering = ref(false);

const currentEcoIndex = computed(() => {
  const raw = Math.round(currentEcoAngle.value / 60);
  return ((raw % 6) + 6) % 6;
});

const rotateToEcoIndex = (targetIndex: number) => {
  const currentIndex = currentEcoIndex.value;
  let delta = targetIndex - currentIndex;
  if (delta > 3) delta -= 6;
  if (delta < -3) delta += 6;
  currentEcoAngle.value += delta * 60;
  resetEcoAutoTimer();
};

const nextEco = () => {
  currentEcoAngle.value += 60;
  resetEcoAutoTimer();
};

const prevEco = () => {
  currentEcoAngle.value -= 60;
  resetEcoAutoTimer();
};

const startEcoAutoTimer = () => {
  if (ecoAutoTimer) clearInterval(ecoAutoTimer);
  ecoAutoTimer = setInterval(() => {
    if (!isEcoHovering.value) {
      nextEco();
    }
  }, 3000);
};

const resetEcoAutoTimer = () => {
  if (ecoAutoTimer) {
    clearInterval(ecoAutoTimer);
    ecoAutoTimer = null;
  }
  startEcoAutoTimer();
};

const pauseEcoAuto = () => {
  isEcoHovering.value = true;
};

const resumeEcoAuto = () => {
  isEcoHovering.value = false;
  resetEcoAutoTimer();
};

onMounted(() => {
  startEcoAutoTimer();
});

onUnmounted(() => {
  if (ecoAutoTimer) clearInterval(ecoAutoTimer);
});
</script>

<style scoped lang="scss">
.cylinder-carousel-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 40px 0;
  padding: 20px 0;
}

.carousel-arrow {
  background: rgba(255,255,255,0.9);
  border: 1px solid rgba(37,99,235,0.2);
  border-radius: 50%;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.2, 0.9, 0.4, 1.1);
  color: #1e293b;
  backdrop-filter: blur(8px);
  z-index: 20;
  box-shadow: 0 8px 20px rgba(0,0,0,0.08);
  
  &:hover {
    background: white;
    transform: scale(1.08);
    box-shadow: 0 12px 24px rgba(37,99,235,0.2);
    color: #2563eb;
    border-color: #2563eb;
  }
  
  &.left-arrow { margin-right: 20px; }
  &.right-arrow { margin-left: 20px; }
  
  @media (max-width: 768px) {
    width: 36px;
    height: 36px;
    &.left-arrow { margin-right: 10px; }
    &.right-arrow { margin-left: 10px; }
  }
}

.cylinder-container {
  flex: 1;
  max-width: 1100px;
  perspective: 1600px;
  overflow: visible;
  position: relative;
}

.cylinder-stage {
  width: 100%;
  height: 380px;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.cylinder-carousel {
  position: relative;
  width: 300px;
  height: 340px;
  transform-style: preserve-3d;
  transition: transform 0.7s cubic-bezier(0.25, 0.85, 0.35, 1);
  will-change: transform;
}

.cylinder-card {
  position: absolute;
  top: 0;
  left: 0;
  width: 300px;
  height: 340px;
  border-radius: 28px;
  background: linear-gradient(145deg, rgba(255,255,255,0.95), rgba(249,250,255,0.98));
  backdrop-filter: blur(2px);
  box-shadow: 0 25px 40px -12px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.8);
  border: 1px solid rgba(255,255,255,0.6);
  transition: all 0.3s ease;
  cursor: default;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 28px;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #2563eb, #7c3aed, #06b6d4);
    border-radius: 28px 28px 0 0;
  }
  
  .card-inner {
    width: 100%;
    position: relative;
    z-index: 2;
  }
  
  .eco-icon {
    margin-bottom: 24px;
    color: #2563eb;
    background: linear-gradient(135deg, #eef2ff, #ffffff);
    width: 70px;
    height: 70px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 30px;
    margin-left: auto;
    margin-right: auto;
    box-shadow: 0 8px 16px -8px rgba(0,0,0,0.1);
    
    svg {
      width: 44px;
      height: 44px;
      filter: drop-shadow(0 2px 4px rgba(0,0,0,0.05));
    }
  }
  
  h4 {
    font-size: 1.4rem;
    font-weight: 800;
    margin-bottom: 14px;
    background: linear-gradient(135deg, #0f172a, #1e293b);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    letter-spacing: -0.01em;
  }
  
  p {
    font-size: 0.9rem;
    color: #475569;
    line-height: 1.5;
    font-weight: 500;
  }
  
  .card-glow {
    position: absolute;
    bottom: -20px;
    left: 10%;
    width: 80%;
    height: 40px;
    background: radial-gradient(ellipse, rgba(37,99,235,0.2), transparent);
    filter: blur(12px);
    z-index: 0;
    pointer-events: none;
  }
  
  &:hover {
    transform: translateY(-6px) rotateY(0deg) !important;
    box-shadow: 0 35px 50px -20px rgba(0,0,0,0.35);
    border-color: rgba(37,99,235,0.3);
    
    .card-glow {
      opacity: 0.7;
      transform: scale(1.1);
    }
  }
}

.cylinder-mask {
  position: absolute;
  top: 0;
  width: 120px;
  height: 100%;
  pointer-events: none;
  z-index: 15;
  
  &.mask-left {
    left: 0;
    background: linear-gradient(to right, rgba(248,250,255,0.95), rgba(248,250,255,0));
  }
  
  &.mask-right {
    right: 0;
    background: linear-gradient(to left, rgba(248,250,255,0.95), rgba(248,250,255,0));
  }
  
  @media (max-width: 768px) {
    width: 60px;
  }
}

.cylinder-indicators {
  display: flex;
  justify-content: center;
  gap: 14px;
  margin-top: 32px;
  
  .cylinder-dot {
    width: 10px;
    height: 10px;
    border-radius: 12px;
    background: #cbd5e1;
    transition: all 0.2s ease;
    cursor: pointer;
    
    &.active {
      width: 32px;
      background: linear-gradient(90deg, #2563eb, #7c3aed);
      box-shadow: 0 0 6px rgba(37,99,235,0.4);
    }
    
    &:hover {
      background: #94a3b8;
      transform: scale(1.1);
    }
  }
}
</style>