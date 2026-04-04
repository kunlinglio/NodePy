<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useLoginStore } from '@/stores/loginStore';
import { usePageStore } from '@/stores/pageStore';

import HeroHeader from '@/views/HomeView/HeroHeader.vue';
import ExampleCarousel from '@/views/HomeView/ExampleCarousel.vue';
import FeaturesGrid from '@/views/HomeView/FeaturesGrid.vue';
import ShowcaseCards from '@/views/HomeView/ShowcaseCards.vue';
import HybridDeployment from '@/views/HomeView/HybridDeployment.vue';
import CtaSection from '@/views/HomeView/CtaSection.vue';
import AppFooter from '@/views/HomeView/AppFooter.vue';
import TutorialDemo from './TutorialDemo.vue';
import FileBank from './FileBank.vue';

const pageStore = usePageStore();
const loginStore = useLoginStore();

// 当前激活的区块索引 - 7个区块（CTA和Footer合并）
const currentSection = ref(0);
const isAnimating = ref(false);
const totalSections = 7; // hero, features, tutorial, showcase, filebank, hybrid, cta+footer

// 是否已进入自由滚动模式（只在最后一个区块内允许自由滚动）
const isFreeScrollMode = ref(false);

// 拖拽相关状态（改进版）
const isDragging = ref(false);
const isDraggingActive = ref(false);
const dragStartY = ref(0);
const dragStartTranslate = ref(0);
const currentTranslate = ref(0);
const dragThreshold = 100;

// 计算当前偏移量
const translateY = computed(() => {
  if (isDragging.value && isDraggingActive.value) {
    return currentTranslate.value;
  }
  return -currentSection.value * 100;
});

// 切换到指定区块
const goToSection = (index: number) => {
  if (isAnimating.value || index < 0 || index >= totalSections) return;

  isAnimating.value = true;
  currentSection.value = index;

  // 只有在进入最后一个区块时才启用自由滚动模式
  if (index === totalSections - 1) {
    isFreeScrollMode.value = true;
  } else {
    isFreeScrollMode.value = false;
  }

  setTimeout(() => {
    isAnimating.value = false;
  }, 800);
};

// 滚轮事件处理
const handleWheel = (e: WheelEvent) => {
  // 如果不在最后一个区块，使用分页滚动
  if (currentSection.value < totalSections - 1) {
    e.preventDefault();
    if (isAnimating.value) return;

    if (e.deltaY > 0) {
      goToSection(currentSection.value + 1);
    } else {
      goToSection(currentSection.value - 1);
    }
    return;
  }

  // 在最后一个区块内（CTA+Footer区块）
  if (currentSection.value === totalSections - 1) {
    const ctaFooterSlide = document.querySelector('.cta-footer-slide');
    if (!ctaFooterSlide) return;

    const rect = ctaFooterSlide.getBoundingClientRect();
    const isAtTop = rect.top >= -10;

    // 如果在顶部且向上滚动，返回上一个区块
    if (e.deltaY < 0 && isAtTop) {
      e.preventDefault();
      isFreeScrollMode.value = false;
      goToSection(totalSections - 2);
      return;
    }

    // 在最后一个区块内，允许自由滚动，不阻止默认行为
    e.stopPropagation();
  }
};

// 鼠标事件（改进版：只有移动超过阈值才真正拖拽）
const handleMouseDown = (e: MouseEvent) => {
  // 如果在最后一个区块且启用了自由滚动，不处理拖拽
  if (currentSection.value === totalSections - 1 && isFreeScrollMode.value) {
    return;
  }
  // 如果点击的是可交互元素（按钮、圆点等），不启动拖拽
  const interactiveSelector = 'button, .indicator-dot, .tab-btn, [role="button"], a';
  if ((e.target as HTMLElement).closest(interactiveSelector)) {
    return;
  }
  e.preventDefault();
  isDragging.value = true;
  isDraggingActive.value = false;
  dragStartY.value = e.clientY;
  dragStartTranslate.value = -currentSection.value * window.innerHeight;
  currentTranslate.value = dragStartTranslate.value;
};

const handleMouseMove = (e: MouseEvent) => {
  if (!isDragging.value) return;
  const deltaY = e.clientY - dragStartY.value;
  if (!isDraggingActive.value && Math.abs(deltaY) > dragThreshold) {
    isDraggingActive.value = true;
  }
  if (isDraggingActive.value) {
    currentTranslate.value = dragStartTranslate.value + deltaY;
  }
};

const handleMouseUp = (e: MouseEvent) => {
  if (!isDragging.value) return;
  isDragging.value = false;
  if (isDraggingActive.value) {
    const deltaY = e.clientY - dragStartY.value;
    if (Math.abs(deltaY) > dragThreshold) {
      if (deltaY > 0) {
        goToSection(currentSection.value - 1);
      } else {
        goToSection(currentSection.value + 1);
      }
    } else {
      goToSection(currentSection.value);
    }
  }
  isDraggingActive.value = false;
};

// 触摸事件（改进版）
const handleTouchStart = (e: TouchEvent) => {
  if (currentSection.value === totalSections - 1 && isFreeScrollMode.value) {
    return;
  }
  const interactiveSelector = 'button, .indicator-dot, .tab-btn, [role="button"], a';
  if ((e.target as HTMLElement).closest(interactiveSelector)) {
    return;
  }
  e.preventDefault();
  isDragging.value = true;
  isDraggingActive.value = false;
  dragStartY.value = e.touches[0]!.clientY;
  dragStartTranslate.value = -currentSection.value * window.innerHeight;
  currentTranslate.value = dragStartTranslate.value;
};

const handleTouchMove = (e: TouchEvent) => {
  if (!isDragging.value) return;
  const deltaY = e.touches[0]!.clientY - dragStartY.value;
  if (!isDraggingActive.value && Math.abs(deltaY) > dragThreshold) {
    isDraggingActive.value = true;
  }
  if (isDraggingActive.value) {
    currentTranslate.value = dragStartTranslate.value + deltaY;
  }
};

const handleTouchEnd = (e: TouchEvent) => {
  if (!isDragging.value) return;
  isDragging.value = false;
  if (isDraggingActive.value) {
    const deltaY = e.changedTouches[0]!.clientY - dragStartY.value;
    if (Math.abs(deltaY) > dragThreshold) {
      if (deltaY > 0) {
        goToSection(currentSection.value - 1);
      } else {
        goToSection(currentSection.value + 1);
      }
    } else {
      goToSection(currentSection.value);
    }
  }
  isDraggingActive.value = false;
};

// 键盘导航
const handleKeyDown = (e: KeyboardEvent) => {
  if (isAnimating.value) return;

  if (currentSection.value === totalSections - 1) {
    if (e.key === 'ArrowUp' || e.key === 'PageUp') {
      const ctaFooterSlide = document.querySelector('.cta-footer-slide');
      if (ctaFooterSlide) {
        const rect = ctaFooterSlide.getBoundingClientRect();
        if (rect.top >= -10) {
          e.preventDefault();
          isFreeScrollMode.value = false;
          goToSection(totalSections - 2);
          return;
        }
      }
    }
    if (e.key === 'Home') {
      e.preventDefault();
      isFreeScrollMode.value = false;
      goToSection(0);
      return;
    }
    return;
  }

  switch(e.key) {
    case 'ArrowDown':
    case 'PageDown':
      e.preventDefault();
      goToSection(currentSection.value + 1);
      break;
    case 'ArrowUp':
    case 'PageUp':
      e.preventDefault();
      goToSection(currentSection.value - 1);
      break;
    case 'Home':
      e.preventDefault();
      goToSection(0);
      break;
    case 'End':
      e.preventDefault();
      goToSection(totalSections - 1);
      break;
  }
};

onMounted(() => {
  loginStore.checkAuthStatus();
  pageStore.setCurrentPage('Home');

  window.addEventListener('wheel', handleWheel, { passive: false });
  window.addEventListener('keydown', handleKeyDown);
  window.addEventListener('mouseup', handleMouseUp);
  window.addEventListener('mousemove', handleMouseMove);
  window.addEventListener('touchend', handleTouchEnd);
  window.addEventListener('touchmove', handleTouchMove, { passive: false });
});

onUnmounted(() => {
  window.removeEventListener('wheel', handleWheel);
  window.removeEventListener('keydown', handleKeyDown);
  window.removeEventListener('mouseup', handleMouseUp);
  window.removeEventListener('mousemove', handleMouseMove);
  window.removeEventListener('touchend', handleTouchEnd);
  window.removeEventListener('touchmove', handleTouchMove);
});
</script>

<template>
  <div class="home-container">
    <!-- 背景装饰 -->
    <div class="particle-bg"></div>
    <div class="gradient-orb orb-1"></div>
    <div class="gradient-orb orb-2"></div>
    <div class="gradient-orb orb-3"></div>

    <!-- 全屏滚动容器 -->
    <div 
      class="fullscreen-slider"
      :class="{ 'free-scroll-mode': isFreeScrollMode && currentSection === totalSections - 1 }"
      :style="{ 
        transform: isFreeScrollMode && currentSection === totalSections - 1 
          ? `translateY(-${(totalSections - 1) * 100}vh)` 
          : `translateY(${isDragging && isDraggingActive ? currentTranslate + 'px' : translateY + 'vh'})`,
        transition: isDragging ? 'none' : 'transform 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)'
      }"
      @mousedown="handleMouseDown"
      @touchstart="handleTouchStart"
    >
      <!-- Hero Section -->
      <div class="slide hero-slide" :class="{ active: currentSection === 0 }">
        <div class="slide-content hero-content">
          <HeroHeader />
          <div class="hero-visual">
            <ExampleCarousel />
          </div>
        </div>
      </div>

      <!-- 核心优势 -->
      <div class="slide features-slide" :class="{ active: currentSection === 1 }">
        <div class="section-wrapper">
          <div class="section-header">
            <h2 class="section-title">专为量化而生，<span class="gradient-text">开箱即用</span></h2>
            <p class="section-subtitle">从数据获取到策略回测，NodePy 提供一站式金融数据分析解决方案</p>
          </div>
          <FeaturesGrid />
        </div>
      </div>

      <!-- 教程 -->
      <div class="slide" :class="{ active: currentSection === 2 }">
        <div class="section-wrapper">
          <div class="section-header">
            <h2 class="section-title">手把手教会你的<span class="gradient-text">教程</span></h2>
            <p class="section-subtitle">新手小白也能快速上手</p>
          </div>
          <TutorialDemo />
        </div>
      </div>

      <!-- 工作流模板 -->
      <div class="slide showcase-slide" :class="{ active: currentSection === 3 }">
        <div class="section-wrapper">
          <div class="section-header">
            <h2 class="section-title">精选<span class="gradient-text">工作流模板</span></h2>
            <p class="section-subtitle">从经典策略到前沿应用，快速启动您的项目</p>
          </div>
        </div>
        <!-- 全屏画廊容器（突破 .section-wrapper 的 max-width 限制） -->
        <div class="showcase-fullwidth">
          <ShowcaseCards />
        </div>
      </div>

      <!-- 文件库 -->
      <div class="slide" :class="{ active: currentSection === 4 }">
        <div class="section-wrapper">
          <div class="section-header">
            <h2 class="section-title">随心管理<span class="gradient-text">文件库</span></h2>
            <p class="section-subtitle">随时随地访问、管理或下载您的文件</p>
          </div>
          <FileBank />
        </div>
      </div>

      <!-- 混合部署 -->
      <div class="slide hybrid-slide" :class="{ active: currentSection === 5 }">
        <!-- 将标题和内容放入全宽深色面板，使面板覆盖标题与说明 -->
        <div class="hybrid-fullwidth">
          <div class="hybrid-panel-full">
            <div class="section-header">
              <h2 class="section-title">
                开源 + 可自托管<br />
                <span class="gradient-text">企业级部署，兼顾数据隐私</span>
              </h2>
              <p class="section-subtitle">
                NodePy 完全开源，支持云端 SaaS 或自有服务器部署，数据不出域，保障企业核心隐私安全。
                满足金融级、GDPR 等合规要求，让您的业务在安全与弹性间完美平衡。
              </p>
            </div>
            <HybridDeployment />
          </div>
        </div>
      </div>

      <!-- CTA + Footer 合并区块 -->
      <div class="slide cta-footer-slide" :class="{ active: currentSection === 6 }">
        <div class="cta-footer-wrapper">
          <div class="cta-section-full">
            <CtaSection />
          </div>
          <div class="footer-section-full">
            <AppFooter />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss">
@use '@/common/global.scss' as *;
@use '@/common/node.scss' as *;
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600;14..32,700;14..32,800&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  scrollbar-width: none;
  -ms-overflow-style: none;
}

html::-webkit-scrollbar {
  display: none;
}

.home-container {
  font-family: 'Inter', sans-serif;
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: #f8faff;
  overflow: hidden;
  color: #1e293b;
  user-select: none;
  scrollbar-width: none;
  z-index: 0;
  -ms-overflow-style: none;
}

.home-container::-webkit-scrollbar {
  display: none;
}

/* 背景装饰 */
.particle-bg {
  position: absolute;
  width: 100%;
  height: 100%;
  background-image: radial-gradient(#3b82f6 0.5px, transparent 0.5px);
  background-size: 24px 24px;
  opacity: 0.3;
  pointer-events: none;
  z-index: -1;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  z-index: -1;
  pointer-events: none;
}

.orb-1 {
  width: 500px;
  height: 500px;
  background: #3b82f6;
  top: -200px;
  right: -150px;
}
.orb-2 {
  width: 400px;
  height: 400px;
  background: #8b5cf6;
  bottom: 100px;
  left: -100px;
}
.orb-3 {
  width: 300px;
  height: 300px;
  background: #06b6d4;
  top: 60%;
  left: 40%;
}

.fullscreen-slider {
  position: relative;
  width: 100%;
  height: 100%;
  will-change: transform;
  cursor: grab;
  scrollbar-width: none;
  -ms-overflow-style: none;

  &:active {
    cursor: grabbing;
  }

  &::-webkit-scrollbar {
    display: none;
  }

  &.free-scroll-mode {
    height: auto;
    overflow-y: auto;
    cursor: default;
    scrollbar-width: none;
    -ms-overflow-style: none;
    touch-action: auto; /* allow native touch scrolling in free mode */
    -webkit-overflow-scrolling: touch;

    &::-webkit-scrollbar {
      display: none;
    }

    .cta-footer-slide {
      min-height: 100vh;
      height: auto;
    }
  }
}

/* Ensure CTA + Footer 区块有背景色（提高优先级以防被覆盖） */
.fullscreen-slider .cta-footer-slide {
  background: linear-gradient(180deg, #f8faff 0%, #f1f5f9 100%);
}

.slide {
  width: 100vw;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  scrollbar-width: none;
  -ms-overflow-style: none;

  &::-webkit-scrollbar {
    display: none;
  }
}

.section-wrapper {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 40px 24px;
  position: relative;
  z-index: 2;
}

.hero-slide {
  .hero-content {
    width: 100%;
    max-width: 1280px;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    padding-top: 60px;
    position: relative;
    z-index: 2;
  }

  .hero-visual {
    width: 100%;
    max-width: 900px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.features-slide {
  .section-wrapper {
    width: 100%;
    max-width: 1280px;
    padding: 40px 24px;

    :deep(.features-media-grid) {
      width: 100%;
    }
  }
}

/* Showcase 全屏展示：使画廊突破 .section-wrapper 的 max-width 限制 */
.showcase-slide {
  .section-wrapper {
    z-index: 2;
  }
}

.showcase-fullwidth {
  width: 100vw;
  margin-left: calc(50% - 50vw);
  margin-right: calc(50% - 50vw);
  padding: 20px 0px;
  box-sizing: border-box;
  z-index: 1;

  .gallery-container {
    width: 100%;
    overflow: visible;
  }
}

/* Hybrid 全屏深色面板：包裹标题与组件 */
.hybrid-fullwidth {
  width: 100vw;
  margin-left: calc(50% - 50vw);
  margin-right: calc(50% - 50vw);
  padding: 28px 0px;
  box-sizing: border-box;
  z-index: 1;
}

.hybrid-panel-full {
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  padding: 28px;
  box-sizing: border-box;
  background: linear-gradient(180deg, #071025 0%, #0b1726 100%);
  border-radius: 20px;
  box-shadow: 0 18px 40px rgba(2, 6, 23, 0.45);
  .section-header{
    .section-title{
      color: white;
    }
    .section-subtitle{
      color: grey;
    }
  }
}

@media (max-width: 768px) {
  .showcase-fullwidth {
    padding: 16px 20px;
  }
}

.cta-footer-slide {
  min-height: 100vh;
  height: auto;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  background: linear-gradient(180deg, #f8faff 0%, #f1f5f9 100%);
  padding: 0;
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;

  &::-webkit-scrollbar {
    display: none;
  }

  .cta-footer-wrapper {
    width: 100%;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  .cta-section-full {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 60px 24px;
    width: 100%;

    :deep(.cta-card) {
      width: 100%;
      max-width: 1100px;
      min-height: 300px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      /* CTA 不使用独立背景，让父级（Home 的 cta 区块）背景透出 */
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
      padding: 0 !important;
      color: inherit;
    }

    :deep(.cta-card) h2 {
      background: none !important;
      -webkit-background-clip: unset !important;
      color: #0f172a !important; /* 与 Home 背景配合的深色文本 */
    }
    :deep(.cta-card) p {
      color: #475569 !important;
    }
    :deep(.cta-card) .cta-btn.outline {
      background: rgba(255,255,255,0.95) !important;
      border: 1px solid #cbd5e1 !important;
      color: #0f172a !important;
      backdrop-filter: blur(4px) !important;
    }
    :deep(.cta-card) .cta-btn.solid {
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15) !important;
    }

    /* 确保 Hybrid 的代码高亮在深色面板中透明并使用深色主题色 */
    .hybrid-panel-full :deep(.hljs),
    .hybrid-panel-full :deep(pre.hljs),
    .hybrid-panel-full :deep(code.hljs),
    .hybrid-panel-full .code-block pre,
    .hybrid-panel-full .code-block code {
      background: transparent !important;
      color: #e6eef8 !important;
    }
  }

  .footer-section-full {
    width: 100%;
    margin-top: auto;

    :deep(.footer-container) {
      width: 100%;
      margin: 0;
      border-radius: 0;
      margin-top: 0;
    }
  }
}

.section-header {
  text-align: center;
  margin-bottom: 32px;

  .section-title {
    font-size: 2.5rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #0f172a;
    margin-bottom: 16px;
  }

  .section-subtitle {
    font-size: 1.125rem;
    color: #475569;
    max-width: 700px;
    margin: 0 auto;
    line-height: 1.5;
  }
}

.gradient-text {
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

@media (max-width: 768px) {
  .section-wrapper {
    padding: 48px 20px;
  }

  .section-header {
    .section-title {
      font-size: 2rem;
    }
  }

  .cta-footer-slide {
    .cta-section-full {
      padding: 40px 20px;

      :deep(.cta-card) {
        min-height: 250px;
        padding: 40px 24px;
      }
    }
  }
}

.slide {
  .section-wrapper {
    opacity: 0;
    transform: translateY(30px);
    transition: all 0.6s ease-out;
  }

  &.active {
    .section-wrapper {
      opacity: 1;
      transform: translateY(0);
    }
  }
}

.cta-footer-slide {
  .cta-section-full,
  .footer-section-full {
    opacity: 0;
    transform: translateY(30px);
    transition: all 0.6s ease-out;
  }

  &.active {
    .cta-section-full,
    .footer-section-full {
      opacity: 1;
      transform: translateY(0);
    }
  }
}
</style>