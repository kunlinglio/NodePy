<template>
  <div class="tutorial-demo">
    <!-- 标签按钮区：无圆角，竖线分割，选中亮色边框 -->
    <div class="tab-bar-container">
      <div class="tab-buttons">
        <button
          v-for="(tutorial, index) in tutorials"
          :key="tutorial.id"
          :class="['tab-btn', { active: activeIndex === index }]"
          @click="setActiveTutorial(index)"
          @mousedown.stop
          @touchstart.stop
        >
          {{ tutorial.title }}
        </button>
      </div>
    </div>

    <!-- 下方大显示框：无圆角，仅展示当前教程图片 -->
    <div class="carousel-wrapper">
      <div class="carousel-viewport">
        <div class="single-image">
          <transition name="fade" mode="out-in">
            <img
              v-if="currentImage"
              :key="currentImage"
              :src="currentImage"
              :alt="currentTutorialTitle"
              class="carousel-image"
            />
            <div v-else class="placeholder-image" :key="'placeholder'">
              <span>图片加载失败</span>
            </div>
          </transition>
        </div>
      </div>

      <!-- 进度条 -->
      <div class="carousel-progress">
        <div class="progress-bar" :style="{ width: progressPercent + '%' }"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';

const tutorials = [
  { id: 1, title: '快速上手', category: 'Quickstart', pages: 9, playgroundProjectId: 588 },
  { id: 2, title: '核心概念', category: 'Concepts', pages: 5, playgroundProjectId: 589 },
  { id: 3, title: '数据流程', category: 'Workflow', pages: 7, playgroundProjectId: 590 },
  { id: 4, title: '逻辑控制', category: 'Automation', pages: 8, playgroundProjectId: 591 },
  { id: 5, title: '机器学习', category: 'Machine Learning', pages: 8, playgroundProjectId: 11 },
];

function getImageByTutorialId(id: number): string {
  const imageMap: Record<number, string> = {
    1: '/guides/1_quick_start_picture.png',
    2: '/guides/2_core_concept_picture.png',
    3: '/guides/3_common_data_flow_picture.png',
    4: '/guides/4_logical_control_and_automation_picture.png',
    5: '/guides/5_machine_learning_picture.png',
  };
  return imageMap[id] || '';
}

const activeIndex = ref(0);
const currentImage = computed(() => getImageByTutorialId(tutorials[activeIndex.value]!.id));
const currentTutorialTitle = computed(() => tutorials[activeIndex.value]!.title);

// 自动轮播相关变量
let carouselTimer: ReturnType<typeof setInterval> | null = null;
let progressInterval: ReturnType<typeof setInterval> | null = null;
const progressPercent = ref(0);
const AUTO_PLAY_INTERVAL = 3000; // 3秒切换一次

// 进度条更新（每60ms增加2%，3秒刚好100%）
const startProgress = () => {
  if (progressInterval) clearInterval(progressInterval);
  progressPercent.value = 0;
  progressInterval = setInterval(() => {
    if (progressPercent.value < 100) {
      progressPercent.value = Math.min(progressPercent.value + 2, 100);
    }
  }, AUTO_PLAY_INTERVAL / 50); // 3000/50 = 60ms
};

const resetProgress = () => {
  if (progressInterval) clearInterval(progressInterval);
  progressPercent.value = 0;
  startProgress();
};

const startAutoPlay = () => {
  if (carouselTimer) clearInterval(carouselTimer);
  carouselTimer = setInterval(() => {
    nextTutorial();
  }, AUTO_PLAY_INTERVAL);
};

const stopAutoPlay = () => {
  if (carouselTimer) {
    clearInterval(carouselTimer);
    carouselTimer = null;
  }
  if (progressInterval) {
    clearInterval(progressInterval);
    progressInterval = null;
  }
};

const resetAutoPlay = () => {
  stopAutoPlay();
  resetProgress();
  startAutoPlay();
};

const nextTutorial = () => {
  const nextIndex = (activeIndex.value + 1) % tutorials.length;
  activeIndex.value = nextIndex;
};

const setActiveTutorial = (index: number) => {
  if (activeIndex.value === index) return;
  activeIndex.value = index;
};

// 监听当前教程索引变化，重置自动播放计时和进度条
watch(activeIndex, () => {
  resetAutoPlay();
});

onMounted(() => {
  startAutoPlay();
  startProgress();
});

onUnmounted(() => {
  stopAutoPlay();
});
</script>

<style lang="scss" scoped>
.tutorial-demo {
  width: 100%;
  margin: 0 auto;
}

/* 按钮容器：无圆角，竖线分隔 */
.tab-bar-container {
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
  position: relative;
  z-index: 5;

  .tab-buttons {
    display: inline-flex;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
    overflow: hidden;

    .tab-btn {
      padding: 12px 28px;
      font-size: 1rem;
      font-weight: 600;
      color: #334155;
      background: transparent;
      border: none;
      cursor: pointer;
      transition: all 0.2s ease;
      white-space: nowrap;
      font-family: 'Inter', sans-serif;
      position: relative;

      &:not(:first-child) {
        border-left: 1px solid #e2e8f0;
      }

      &:hover {
        color: #2563eb;
        background-color: #f8fafc;
      }

      &.active {
        color: #2563eb;
        background: linear-gradient(to bottom, #eff6ff, #ffffff);
        box-shadow: inset 0 0 0 2px #3b82f6;
        z-index: 2;
      }
    }
  }
}

/* 下方大显示框 */
.carousel-wrapper {
  border: 1px solid #e2e8f0;
  background: white;
  max-width: 1000px;
  margin: 0 auto;
}

.carousel-viewport {
  width: 100%;
  overflow: hidden;
  background: #f8fafc;
  aspect-ratio: 16 / 9;
  display: flex;
  align-items: center;
  justify-content: center;
}

.single-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.carousel-image {
  height: 100%;
  background: #f1f5f9;
}

.placeholder-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  color: #94a3b8;
  font-size: 1rem;
  span {
    background: white;
    padding: 8px 16px;
    border-radius: 40px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }
}

/* 进度条 */
.carousel-progress {
  height: 3px;
  background: #e2e8f0;
  width: 100%;
  overflow: hidden;

  .progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    width: 0%;
    transition: width 60ms linear;
  }
}

/* 图片切换淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .tab-bar-container .tab-buttons .tab-btn {
    padding: 8px 16px;
    font-size: 0.85rem;
  }
}
</style>