<template>
  <div class="footer-container">
    <div class="footer-main">
      <div class="footer-brand">
        <h3>NodePy</h3>
        <p>下一代可视化金融数据分析平台</p>
        <!-- <div class="admin-entrance" @click="jumpToAdmin">管理员入口</div> -->
      </div>
      <div class="footer-links">
        <div class="link-group">
          <h4>产品</h4>
          <a @click="jumpToProject">工作台</a>
        </div>
        <div class="link-group">
          <h4>支持</h4>
          <a @click="jumpToTutorial">教程</a>
          <a @click="jumpToCommunity">广场</a>
        </div>
        <div class="link-group">
          <h4>关于</h4>
          <a @click="jumpToGithub">GitHub</a>
        </div>
      </div>
    </div>
    <div class="footer-copyright">
      <p>© 2026 NodePy Team. 数据驱动未来，节点构建智能。</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useLoginStore } from '@/stores/loginStore';
import { useModalStore } from '@/stores/modalStore';
import AdminAccountInfo from '@/components/AdminAccountInfo.vue';

const router = useRouter();
const loginStore = useLoginStore();
const modalStore = useModalStore();

function jumpToCommunity() {
  router.push({ name: 'example' });
}
function jumpToProject() {
  router.push({ name: 'project' });
}
function jumpToGithub() {
  window.open('https://github.com/LKLLLLLLLLLL/NodePy', '_blank');
}
function jumpToTutorial() {
  router.push({ name: 'explore' });
}

function jumpToAdmin() {
  if (loginStore.loggedIn) {
    const UserAccessWidth = 300;
    const UserAccessHeight = 240;
    modalStore.createModal({
      component: AdminAccountInfo,
      title: '用户权限',
      isActive: true,
      isResizable: false,
      isDraggable: true,
      isModal: true,
      position: {
        x: window.innerWidth / 2 - UserAccessWidth / 2,
        y: window.innerHeight / 2 - UserAccessHeight / 2
      },
      size: {
        width: UserAccessWidth,
        height: UserAccessHeight
      },
      id: 'user-access',
    });
    return;
  }
  router.push({ name: 'adminlogin' });
}
</script>

<style scoped lang="scss">
.footer-container {
  background-color: #0b1120;
//   border-radius: 24px 24px 0 0;
  padding: 28px 32px 20px;
  margin-top: 24px;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.05);
}

.footer-main {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 28px;
  margin-bottom: 20px;

  .footer-brand {
    h3 {
      font-size: 1.3rem;
      font-weight: 700;
      color: #f1f5f9;
      letter-spacing: -0.3px;
      margin-bottom: 6px;
    }
    p {
      font-size: 0.75rem;
      color: #94a3b8;
      margin: 0;
    }
    .admin-entrance {
      font-size: 0.65rem;
      color: #64748b;
      margin-top: 8px;
      cursor: pointer;
      transition: color 0.2s;
      &:hover {
        color: #60a5fa;
      }
    }
  }

  .footer-links {
    display: flex;
    gap: 40px;

    .link-group {
      h4 {
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 8px;
        color: #e2e8f0;
      }
      a {
        display: block;
        font-size: 0.8rem;
        color: #94a3b8;
        margin-bottom: 5px;
        cursor: pointer;
        transition: color 0.2s;
        &:hover {
          color: #ffffff;
        }
      }
    }
  }
}

.footer-copyright {
  text-align: center;
  font-size: 0.7rem;
  color: #5b6e8c;
  padding-top: 16px;
  border-top: 1px solid #1e293b;
  margin-top: 4px;

  p {
    margin: 0;
  }
}

@media (max-width: 640px) {
  .footer-container {
    padding: 20px 20px 16px;
  }
  .footer-main {
    gap: 20px;
    .footer-links {
      gap: 24px;
    }
  }
}
</style>