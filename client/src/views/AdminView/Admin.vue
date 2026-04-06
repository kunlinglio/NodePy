<script setup lang="ts">
import { useAdminLoginStore } from "@/stores/adminLoginStore";
import { useUserStore } from "@/stores/userStore";
import { useRouter } from "vue-router";
import ServerStorageStatus from "./ServerStorageStatus.vue";
import UserStatus from "./UserStatus.vue";
import FinancialStatus from "./FinancialStatus.vue";
import SystemHealthStatus from "./SystemHealthStatus.vue";
import ProjectStatus from "./ProjectStatus.vue";
import ReviewStatus from "./ReviewStatus.vue";
import Loading from "@/components/Loading.vue";
import notify from "@/components/Notification/notify";
import { ref, onMounted, computed } from "vue";

const adminLoginStore = useAdminLoginStore();
const userStore = useUserStore();
const router = useRouter();

const currentDemo = ref<string>("userStatus");
const currentAdmin = ref<string>(userStore.currentUserInfo.username || "DefaultAdmin");
const isClickable = ref(true); // 防抖标志

// 头像首字母缩写
const avatarInitials = computed(() => {
  const name = currentAdmin.value?.trim() || 'Admin';
  if (!name) return 'AD';
  const parts = name.split(/\s|[._-]+/).filter(part => part.length > 0);
  if (parts.length === 0) return name.slice(0, 2).toUpperCase();
  
  const firstPart = parts[0] ?? '';
  if (parts.length === 1) {
    return firstPart.slice(0, 2).toUpperCase();
  }
  
  const secondPart = parts[1] ?? '';
  const firstChar = firstPart[0] ?? '';
  const secondChar = secondPart[0] ?? '';
  const result = (firstChar + secondChar).toUpperCase();
  return result || name.slice(0, 2).toUpperCase();
});

onMounted(async () => {
  await userStore.getUserInfo();
  currentAdmin.value = userStore.currentUserInfo.username || "DefaultAdmin";
});

// 防抖包装函数（带提示）
function withDebounce(fn: () => void) {
  return () => {
    if (!isClickable.value) {
      notify({
        message: '操作过于频繁，请稍后再试',
        type: 'warning'
      });
      return;
    }
    isClickable.value = false;
    fn();
    setTimeout(() => {
      isClickable.value = true;
    }, 1000);
  };
}

function handleGetUserStatus() {
  currentDemo.value = "userStatus";
}

function handleGetServerStorageStatus() {
  currentDemo.value = "serverStorageStatus";
}

function handleGetFinancialStatus() {
  currentDemo.value = "financialStatus";
}

function handleGetProjectStatus() {
  currentDemo.value = "projectStatus";
}

function handleGetSystemHealthStatus() {
  currentDemo.value = "systemHealthStatus";
}

function handleGetReviewStatus() {
  currentDemo.value = "reviewStatus";
}

async function handleLogout() {
  await adminLoginStore.logout();
  router.replace("/home");
}

// 应用防抖
const debouncedGetUserStatus = withDebounce(handleGetUserStatus);
const debouncedGetServerStorageStatus = withDebounce(handleGetServerStorageStatus);
const debouncedGetFinancialStatus = withDebounce(handleGetFinancialStatus);
const debouncedGetProjectStatus = withDebounce(handleGetProjectStatus);
const debouncedGetSystemHealthStatus = withDebounce(handleGetSystemHealthStatus);
const debouncedGetReviewStatus = withDebounce(handleGetReviewStatus);
</script>

<template>
  <div class="page-container">
    <div class="left-container">
      <div class="icon-container">
        <img src="../../../public/favicon.ico" class="logo" />
        <div class="title-wrapper">
          <div class="main-title">NodePy</div>
          <div class="sub-title">后台管理系统</div>
        </div>
      </div>
      <div class="buttonlist-container">
        <button 
          @click="debouncedGetUserStatus" 
          :class="{ active: currentDemo === 'userStatus' }"
        >用户状态</button>
        <button 
          @click="debouncedGetServerStorageStatus" 
          :class="{ active: currentDemo === 'serverStorageStatus' }"
        >存储状态</button>
        <button 
          @click="debouncedGetFinancialStatus" 
          :class="{ active: currentDemo === 'financialStatus' }"
        >财务状态</button>
        <button 
          @click="debouncedGetProjectStatus" 
          :class="{ active: currentDemo === 'projectStatus' }"
        >项目状态</button>
        <button 
          @click="debouncedGetSystemHealthStatus" 
          :class="{ active: currentDemo === 'systemHealthStatus' }"
        >系统健康</button>
        <button 
          @click="debouncedGetReviewStatus" 
          :class="{ active: currentDemo === 'reviewStatus' }"
        >教程评价</button>
      </div>
      <div class="bottombar-container">
        <div class="user-info">
          <div class="avatar">{{ avatarInitials }}</div>
          <div class="user-meta">
            <div class="user-name">{{ currentAdmin }}</div>
            <div class="user-sub">管理员</div>
          </div>
        </div>
        <button class="logout-btn" @click="handleLogout" title="Logout">
          <span>Logout</span>
        </button>
      </div>
    </div>
    <div class="right-container">
      <div class="demo-container" v-if="currentDemo === 'userStatus'">
        <UserStatus/>
      </div>
      <div class="demo-container" v-else-if="currentDemo === 'serverStorageStatus'">
        <ServerStorageStatus/>
      </div>
      <div class="demo-container" v-else-if="currentDemo === 'financialStatus'">
        <FinancialStatus/>
      </div>
      <div class="demo-container" v-else-if="currentDemo === 'projectStatus'">
        <ProjectStatus/>
      </div>
      <div class="demo-container" v-else-if="currentDemo === 'systemHealthStatus'">
        <SystemHealthStatus/>
      </div>
      <div class="demo-container" v-else-if="currentDemo === 'reviewStatus'">
        <ReviewStatus/>
      </div>
      <div class="loading" v-else-if="currentDemo === 'loading'">
        <Loading />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
// 配色与 Explore 保持一致
$primary-color: #108efe;
$bg-light: #f5f7fa;
$card-white: #ffffff;
$text-dark: #2c3e50;
$text-gray: #5b6e8c;
$border-light: #eef2f8;
$shadow-sm: 0 2px 8px rgba(16, 142, 254, 0.08);
$shadow-md: 0 8px 20px rgba(0, 0, 0, 0.05);

.page-container {
  width: 100%;
  height: 100%;
  display: flex;
  background-color: $bg-light;
  position: relative;
}

.left-container {
  width: 280px;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: $card-white;
  border-right: 1px solid $border-light;
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.02);
  z-index: 2;

  .icon-container {
    height: 120px;
    width: 100%;
    background: linear-gradient(135deg, rgba(16, 142, 254, 0.02), rgba(16, 142, 254, 0.08));
    border-bottom: 1px solid $border-light;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 16px;
    padding-left: 24px;
    font-weight: 600;
    color: $primary-color;

    .logo {
      max-height: 56px;
      width: auto;
      object-fit: contain;
    }

    .title-wrapper {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: flex-start;
      line-height: 1.2;

      .main-title {
        font-size: 28px;
        font-weight: 700;
        color: black;
        letter-spacing: 0.5px;
      }

      .sub-title {
        font-size: 14px;
        font-weight: 500;
        color: $text-gray;
        letter-spacing: 0.5px;
        margin-top: 4px;
      }
    }
  }

  .buttonlist-container {
    display: flex;
    flex-direction: column;
    flex: 1;
    background: transparent;
    padding: 16px 12px;
    gap: 8px;

    button {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 24px;
      border-radius: 12px;
      background: transparent;
      border: none;
      font-size: 14px;
      font-weight: 500;
      color: $text-gray;
      cursor: pointer;
      transition: all 0.2s ease;
      width: 100%;
      text-align: left;

      &:hover {
        background: rgba(16, 142, 254, 0.08);
        color: $primary-color;
        transform: translateX(4px);
      }

      // 当前激活按钮样式
      &.active {
        background: rgba(16, 142, 254, 0.12);
        color: $primary-color;
        border-left: 3px solid $primary-color;
        transform: translateX(0);
      }
    }
  }

  .bottombar-container {
    height: auto;
    width: 100%;
    border-top: 1px solid $border-light;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    padding: 16px 12px;
    gap: 12px;
    background: transparent;

    .user-info {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 8px 0;

      .avatar {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(16, 142, 254, 0.15), rgba(16, 142, 254, 0.25));
        color: $primary-color;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 16px;
        box-shadow: $shadow-sm;
      }

      .user-meta {
        flex: 1;

        .user-name {
          font-size: 14px;
          font-weight: 700;
          color: $text-dark;
          line-height: 1.3;
        }

        .user-sub {
          font-size: 11px;
          color: $text-gray;
          margin-top: 2px;
        }
      }
    }

    .logout-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      width: 100%;
      padding: 8px 12px;
      border-radius: 12px;
      background: rgba(239, 68, 68, 0.05);
      border: 1px solid rgba(239, 68, 68, 0.2);
      font-size: 14px;
      font-weight: 500;
      color: #e5484d;
      cursor: pointer;
      transition: all 0.2s ease;

      &:hover {
        background: #e5484d;
        color: white;
        border-color: #e5484d;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(229, 72, 77, 0.2);
      }
    }
  }
}

.right-container {
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: $bg-light;
  overflow-y: auto;

  .demo-container {
    display: flex;
    flex: 1;
    background: $card-white;
    margin: 20px;
    border-radius: 24px;
    box-shadow: $shadow-md;
    padding: 20px;
    border: 1px solid $border-light;
    overflow: auto;

    &:hover {
      box-shadow: 0 12px 28px rgba(16, 142, 254, 0.12);
    }
  }

  .loading {
    flex: 1;
    background: $card-white;
    margin: 20px;
    border-radius: 24px;
    box-shadow: $shadow-md;
    border: 1px solid $border-light;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;

    &:hover {
      box-shadow: 0 12px 28px rgba(16, 142, 254, 0.12);
    }
  }
}

// 滚动条美化
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: $border-light;
  border-radius: 8px;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 8px;

  &:hover {
    background: #94a3b8;
  }
}
</style>