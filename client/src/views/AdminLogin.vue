<template>
  <div class="admin-auth">
    <!-- 左侧 Hero 区域 -->
    <section class="hero">
      <div class="logo-container">
        <img src="../../public/logo-trans.png" alt="Logo" class="logo" />
      </div>
    </section>

    <!-- 右侧卡片区域 -->
    <section class="card">
      <div class="auth-box">
        <div class="login-container">
          <div class="login-head">
            <h2 class="nodepy-title title-container">管理员登录</h2>
          </div>
          <div class="login-form">
            <!-- 登录方式切换胶囊 -->
            <div class="login-type-row">
              <div class="login-type-capsule" role="tablist">
                <button
                  type="button"
                  class="capsule"
                  :class="{ active: loginType === 'email' }"
                  @click="loginType = 'email'"
                >邮箱</button>
                <button
                  type="button"
                  class="capsule"
                  :class="{ active: loginType === 'username' }"
                  @click="loginType = 'username'"
                >用户名</button>
              </div>
            </div>

            <form class="my-form" @submit.prevent="handleSubmit">
              <div class="form-item">
                <label class="form-label">{{ loginType === 'email' ? '邮箱' : '用户名' }}</label>
                <input
                  class="my-input"
                  :placeholder="loginType === 'email' ? '请输入管理员邮箱' : '请输入管理员用户名'"
                  v-model="identifier"
                />
              </div>

              <div class="form-item">
                <label class="form-label">密码</label>
                <input class="my-input" placeholder="请输入密码" v-model="password" type="password" />
              </div>

              <div class="login-control">
                <button type="submit" class="confirm-button" :disabled="pending">
                  {{ pending ? '登录中...' : '登录' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAdminLoginStore } from '@/stores/adminLoginStore';
import { LoginRequest } from '@/utils/api/models/LoginRequest';
import { notify } from '@/components/Notification/notify';
import { isAdminLoggedIn } from '@/utils/AdminAuthHelper';

const router = useRouter();
const adminLoginStore = useAdminLoginStore();

const loginType = ref<'email' | 'username'>('username');
const identifier = ref('');
const password = ref('');
const pending = ref(false);

const handleSubmit = async () => {
  // 前端验证
  if (!identifier.value.trim()) {
    notify({
      message: loginType.value === 'email' ? '请输入邮箱地址' : '请输入用户名',
      type: 'error'
    });
    return;
  }
  if (!password.value.trim()) {
    notify({ message: '请输入密码', type: 'error' });
    return;
  }

  if (loginType.value === 'email') {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(identifier.value)) {
      notify({ message: '请输入有效的邮箱地址', type: 'error' });
      return;
    }
  }

  pending.value = true;

  try {
    await adminLoginStore.login({
      type: loginType.value === 'email' ? LoginRequest.type.EMAIL : LoginRequest.type.USERNAME,
      identifier: identifier.value,
      password: password.value,
    });

    notify({ message: '登录成功，正在跳转...', type: 'success' });
    setTimeout(() => {
      router.push('/admin');
    }, 800);
  } catch (error) {
    // 错误已由 store 内部通过 notify 处理，此处无需重复处理
    console.error('Admin login error:', error);
  } finally {
    pending.value = false;
  }
};

onMounted(() => {
  if (isAdminLoggedIn()) {
    router.replace('/admin');
  }
});
</script>

<style lang="scss" scoped>
@use '../common/global.scss' as *;

/* 左右布局容器 */
.admin-auth {
  width: 100%;
  min-height: 100vh;
  display: flex;
  background: $background-color;
}

/* 左侧 Hero 区域 */
.hero {
  width: 500px;
  background-color: white;
  color: #fff;
  padding: 64px 48px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 32px;
}

/* Logo 容器 */
.logo-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  width: 100%;
  box-sizing: border-box;
  padding: 0 20px;
}

/* Logo 图片 */
.logo {
  max-width: 100%;
  max-height: 280px;
  width: auto;
  height: auto;
  object-fit: contain;
}

/* 右侧卡片区域 */
.card {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

/* ===== 右侧卡片样式 ===== */
.auth-box {
  width: 100%;
  max-width: 420px;
  padding: 24px;
  box-sizing: border-box;
  margin: 0 auto;
  @include controller-style;
  background: $stress-background-color;
  overflow: visible;
  max-height: none;
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
}

.login-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  background-color: transparent;
  padding: 0;
  position: relative;
  overflow: visible;
  min-height: auto;
}

.login-head {
  display: flex;
  flex-direction: column;
  height: auto;
  position: relative;
  z-index: 1;
  padding-bottom: 6px;
}

.title-container {
  height: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding-bottom: 6px;
}

.nodepy-title {
  font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  font-weight: 600;
  letter-spacing: 1px;
  margin: 0;
  color: #333;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  font-size: 24px;
}

.login-form {
  margin-top: 8px;
  position: relative;
  z-index: 1;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.login-type-row {
  display: flex;
  justify-content: center;
}

.login-type-capsule {
  display: inline-flex;
  gap: 8px;
  align-items: center;
  padding: 4px;
  background: transparent;
  border-radius: 999px;
  margin: 12px auto;
  justify-content: center;
}

.login-type-capsule .capsule {
  height: 34px;
  font-size: 13px;
  font-weight: 600;
  color: rgba(20, 20, 20, 0.85);
  padding: 6px 14px;
  border-radius: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-width: 70px;
  cursor: pointer;
  border: none;
  background-color: rgba(0, 0, 0, 0.03);
  box-shadow: none;
  transition: all 0.18s ease;
}

.login-type-capsule .capsule:hover {
  background-color: rgba(0, 0, 0, 0.06);
}

.login-type-capsule .capsule:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.12);
}

.login-type-capsule .capsule.active {
  color: #ffffff;
  background-color: $stress-color;
  box-shadow: 0px 3px 5px rgba(128, 128, 128, 0.15);
}

.my-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 13px;
  color: #5b6b74;
}

.my-input {
  border-radius: 10px;
  padding: 10px 12px;
  border: 1px solid #e6eef9;
  background: #fbfdff;
  font-size: 14px;
  color: #12212b;
  transition: all 0.2s;
}

.my-input:focus {
  outline: none;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
  border-color: $stress-color;
}

.login-control {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.confirm-button {
  @include confirm-button-style;
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.3px;
  border-radius: 10px;
  background-color: $stress-color;
  color: #fff;
  border: none;
  transition: transform 0.12s ease, box-shadow 0.12s ease, background-color 0.12s ease;
  cursor: pointer;
}

.confirm-button:hover:not(:disabled) {
  @include confirm-button-hover-style;
}

.confirm-button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

/* 响应式：窄屏幕下垂直排列 */
@media (max-width: 860px) {
  .admin-auth {
    grid-template-columns: 1fr;
  }
  .hero {
    padding: 40px 32px;
    border-radius: 0 0 24px 24px;
  }
  .card {
    padding: 32px 24px;
  }
}
</style>