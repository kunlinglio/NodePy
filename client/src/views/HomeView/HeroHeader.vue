// HeroHeader.vue
<template>
  <div class="hero-header">
    <h1 class="hero-title">
      NodePy
      <span class="gradient-text">基于节点的金融数据分析平台</span>
    </h1>
    <p class="hero-subtitle">
      无需编写复杂代码，通过拖拽节点即可完成从数据获取、清洗、计算到可视化的全过程。
    </p>

    <div class="quick-start-wrapper">
      <button @click="quickStart" class="quick-start-btn">
        快速开始
      </button>
      <button v-if="!isLoggedIn" @click="signUp" class="signup-btn">
        注册账号
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useLoginStore } from '@/stores/loginStore';
import { computed } from 'vue';

const router = useRouter();
const loginStore = useLoginStore();

const isLoggedIn = computed(() => loginStore.loggedIn);

function quickStart() {
  if (isLoggedIn.value) {
    router.push({ name: 'project' });
  } else {
    router.push({ name: 'visitor' });
  }
}

function signUp() {
    router.push({ name: 'login' });
}
</script>

<style scoped lang="scss">
.hero-header {
  text-align: center;
  max-width: 900px;
  margin: 0 auto;

  .hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    line-height: 1.2;
    letter-spacing: -0.02em;
    color: #0f172a;
    margin-bottom: 5px;      // 降低间距 (原 24px)
    display: flex;
    flex-direction: column;
    gap: 8px;

    .gradient-text {
      font-size: 2rem;
      background: linear-gradient(135deg, #2563eb, #7c3aed);
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent;
    }

    @media (max-width: 768px) {
      font-size: 2.5rem;
      .gradient-text {
        font-size: 1.5rem;
      }
    }
  }

  .hero-subtitle {
    font-size: 1.125rem;
    color: #475569;
    line-height: 1.6;
    margin-bottom: 20px;      // 降低间距 (原 32px)
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
  }

  .quick-start-wrapper {
    display: flex;
    gap: 16px;
    justify-content: center;
    margin-bottom: 24px;      // 降低间距 (原 48px)

    .quick-start-btn, .signup-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: none;
      padding: 12px 32px;
      border-radius: 40px;
      font-weight: 600;
      font-size: 1rem;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .quick-start-btn {
      background: linear-gradient(135deg, #2563eb, #7c3aed);
      color: white;
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
      }
    }

    .signup-btn {
      background: white;
      color: #2563eb;
      border: 1px solid #2563eb;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

      &:hover {
        transform: translateY(-2px);
        background: #f0f4ff;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
      }
    }
  }
}
</style>