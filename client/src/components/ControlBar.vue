<script lang="ts" setup>
import { computed } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import { useGraphStore } from "@/stores/graphStore";
import { useProjectStore } from "@/stores/projectStore";
import { useLoginStore } from "@/stores/loginStore";
import { useModalStore } from "@/stores/modalStore";
import SvgIcon from "@jamescoyle/vue-icon";
import {
  mdiCompassOutline,
  mdiCompass,
  mdiHomeOutline,
  mdiHome,
  mdiFolderOutline,
  mdiFolder,
  mdiProjectorScreenOutline,
  mdiProjectorScreen,
  mdiAccountGroup,
  mdiAccountGroupOutline,
  mdiGithub,
  mdiAccountCog,
} from "@mdi/js";
import UserInfoMenu from "./FloatingMenu/UserInfoMenu.vue";
import AdminAccountInfo from '@/components/AdminAccountInfo.vue';

const graphStore = useGraphStore();
const projectStore = useProjectStore();
const loginStore = useLoginStore();
const modalStore = useModalStore();
const route = useRoute();
const router = useRouter();

function jumpToGithub() {
  window.open('https://github.com/LKLLLLLLLLLL/NodePy', '_blank');
}

// 迁移自 Footer：管理员入口逻辑（包含已登录时显示权限弹窗）
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

const explore_path_outline = mdiCompassOutline;
const explore_path_filled = mdiCompass;
const home_path_outline = mdiHomeOutline;
const home_path_filled = mdiHome;
const project_path_outline = mdiProjectorScreenOutline;
const project_path_filled = mdiProjectorScreen;
const square_path_outline = mdiAccountGroupOutline;
const square_path_filled = mdiAccountGroup;
const file_path_outline = mdiFolderOutline;
const file_path_filled = mdiFolder;

const showProjectName = computed(() => {
  if (route.params.projectId) return true;
  else return false;
});

const navItems = [
  { name: "Home", path: "/home", label: "首页", iconOutline: home_path_outline, iconFilled: home_path_filled, routeName: "home" },
  { name: "Explore", path: "/explore", label: "探索", iconOutline: explore_path_outline, iconFilled: explore_path_filled, routeName: "explore" },
  { name: "Example", path: "/example", label: "广场", iconOutline: square_path_outline, iconFilled: square_path_filled, routeName: "example" },
  { name: "Project", path: "/project", label: "工作台", iconOutline: project_path_outline, iconFilled: project_path_filled, routeName: "project" },
  { name: "File", path: "/file", label: "文件库", iconOutline: file_path_outline, iconFilled: file_path_filled, routeName: "file" },
];

const isActive = (item: typeof navItems[0]) => {
  if (item.routeName) return route.name === item.routeName;
  return route.path === item.path;
};

const isReadOnly = computed(() => {
  return graphStore.project.editable === false;
});
</script>

<template>
  <div class="control-bar" :class="{ 'readonly-mode': isReadOnly }">
    <div class="control-content">
      <!-- 左侧 Logo -->
      <div class="logo-area">
        <img src="../../public/logo-trans.png" alt="Logo" class="logo" />
      </div>

      <!-- 中间导航 / 项目名 -->
      <div class="middle-area">
        <nav class="nav-bar" v-if="!showProjectName">
          <RouterLink
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="nav-link"
            :class="{ active: isActive(item) }"
          >
            <span class="nav-inner">
              <SvgIcon
                v-if="item.iconOutline"
                type="mdi"
                :path="isActive(item) ? item.iconFilled : item.iconOutline"
                class="nav-icon"
              />
              <span class="nav-label">{{ item.label }}</span>
            </span>
          </RouterLink>
        </nav>
        <div v-else class="project-name">
          <h2>{{ graphStore.project.project_name }}</h2>
          <div v-if="isReadOnly" class="readonly-indicator">只读</div>
        </div>
      </div>

      <!-- 右侧操作区：GitHub 按钮 + 管理员按钮 + 用户头像 -->
      <div class="right-actions">
        <button class="action-btn github-btn" @click="jumpToGithub" title="GitHub 仓库">
          <SvgIcon type="mdi" :path="mdiGithub" class="action-icon" />
        </button>
        <button class="action-btn admin-btn" @click="jumpToAdmin" title="管理员入口">
          <SvgIcon type="mdi" :path="mdiAccountCog" class="action-icon" />
        </button>
        <div class="user-avatar">
          <UserInfoMenu />
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use "../common/global.scss" as *;

.control-bar {
  display: flex;
  flex-direction: row;
  height: 100%;
  width: 100%;
  color: black;
  box-shadow: 0 0px 15px rgba(128, 128, 128, 0.1);

  .control-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    height: 100%;
    padding: 0 20px;
    font-size: 14px;
    cursor: context-menu;
  }

  .logo-area {
    flex-shrink: 0;
    height: 90%;
    display: flex;
    align-items: center;

    .logo {
      height: 100%;
      width: auto;
    }
  }

  .middle-area {
    flex: 1;
    display: flex;
    justify-content: center;

    .nav-bar {
      display: flex;
      align-items: center;
      gap: 6px;

      .nav-link {
        color: #000000;
        text-decoration: none;
        font-size: 18px;
        font-weight: bold;
        padding: 9px 15px;
        margin: 0 6px;
        transition: all 0.18s ease;
        min-width: 120px;
        text-align: center;
        border-radius: 20px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: rgba(40, 40, 40, 0.76);

        &:hover {
          background-color: rgba(0, 0, 0, 0.06);
        }

        .nav-inner {
          display: inline-flex;
          align-items: center;
          gap: 8px;
        }

        .nav-icon {
          width: 22px;
          height: 22px;
          display: inline-block;
          fill: currentColor;
        }

        .nav-label {
          line-height: 1;
        }

        &.active {
          border-radius: 19px;
          color: $stress-color;
          background-color: white;
          box-shadow: 0px 3px 5px rgba(128, 128, 128, 0.1);
        }
      }
    }

    .project-name {
      display: flex;
      align-items: center;
      gap: 8px;

      h2 {
        margin: 0;
        font-size: 1.25rem;
      }

      .readonly-indicator {
        color: #9d9b9b;
        font-size: 14px;
        font-weight: bold;
      }
    }
  }

  .right-actions {
    display: flex;
    align-items: center;
    gap: 4px;
    flex-shrink: 0;

    // 通用按钮样式
    .action-btn {
      background: transparent;
      border: none;
      width: 36px;
      height: 36px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: background-color 0.2s;
      color: #5b5b5b;

      &:hover {
        background-color: rgba(0, 0, 0, 0.08);
      }

      .action-icon {
        width: 22px;
        height: 22px;
        fill: currentColor;
      }
    }

    .user-avatar {
      flex-shrink: 0;
      cursor: pointer;
    }
  }
}
</style>