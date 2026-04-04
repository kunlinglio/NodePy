<template>
  <div class="cta-card">
    <div class="cta-content">
      <h2 v-if="!isLoggedIn">准备好开始了吗？</h2>
      <h2 v-else>欢迎回来！</h2>
      <p v-if="!isLoggedIn">立即注册，开启您的可视化金融分析之旅</p>
      <p v-else>继续您的金融分析之旅</p>
      <div class="cta-buttons">
        <button @click="jumpToExample" class="cta-btn outline">
          {{ isLoggedIn ? '回顾教程' : '学习使用' }}
        </button>
        <button @click="quickStart" class="cta-btn solid">
          {{ isLoggedIn ? '进入工作台' : '免费注册' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useLoginStore } from '@/stores/loginStore';

const router = useRouter();
const loginStore = useLoginStore();
const isLoggedIn = computed(() => loginStore.loggedIn);

function jumpToExample() {
  router.push({ name: 'example' });
}

function quickStart() {
  if (isLoggedIn.value) {
    router.push({ name: 'project' });
  } else {
    router.push({ name: 'login' });
  }
}
</script>

<style scoped lang="scss">
.cta-card {
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(12px);
  border-radius: 48px;
  padding: 56px 48px;
  /* 明确设置宽度，使在父容器中可扩展 */
  box-sizing: border-box;
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  text-align: center;
  box-shadow: 0 20px 35px -12px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.5);
  transition: all 0.3s ease;

  h2 {
    font-size: 2rem;
    font-weight: 800;
    margin-bottom: 16px;
    background: linear-gradient(135deg, #1e293b, #2d3a5e);
    background-clip: text;
    -webkit-background-clip: text;
    color: transparent;
  }

  p {
    color: #334155;
    margin-bottom: 32px;
    font-size: 1.1rem;
  }

  .cta-buttons {
    display: flex;
    gap: 20px;
    justify-content: center;
    flex-wrap: wrap;

    .cta-btn {
      padding: 12px 32px;
      border-radius: 40px;
      font-weight: 600;
      font-size: 1rem;
      cursor: pointer;
      transition: all 0.25s ease;
      letter-spacing: 0.3px;

      &.solid {
        background: linear-gradient(105deg, #2563eb, #7c3aed);
        color: white;
        border: none;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
          background: linear-gradient(105deg, #1d4ed8, #6d28d9);
        }
      }

      &.outline {
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid #cbd5e1;
        color: #1e293b;
        backdrop-filter: blur(4px);

        &:hover {
          background: white;
          border-color: #94a3b8;
          transform: translateY(-1px);
        }
      }
    }
  }
}

@media (max-width: 640px) {
  .cta-card {
    padding: 40px 24px;
    h2 {
      font-size: 1.6rem;
    }
    .cta-btn {
      padding: 10px 24px;
    }
  }
}
</style>