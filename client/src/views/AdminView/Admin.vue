<script setup lang="ts">
    import { useAdminStore } from "@/stores/adminStore";
    import { useAdminLoginStore } from "@/stores/adminLoginStore";
    import { useUserStore } from "@/stores/userStore";
    import { useRouter } from "vue-router";
    import { type SystemStatsResponse, type StorageStats, type FinancialSymbolStats, type ProjectStats, type SystemHealthResponse } from "@/utils/api";
    import { PostgresMetrics } from "@/utils/api";
    import { RedisMetrics } from "@/utils/api";
    import { CeleryMetrics } from "@/utils/api";
    import { MinioMetrics } from "@/utils/api";
    import SystemStatus from "./SystemStatus.vue";
    import ServerStorageStatus from "./ServerStorageStatus.vue";
    import FinancialStatus from "./FinancialStatus.vue";
    import SystemHealthStatus from "./SystemHealthStatus.vue";
    import ProjectStatus from "./ProjectStatus.vue";
    import Loading from "@/components/Loading.vue";
    import { ref, onMounted, computed } from "vue";

    const adminStore = useAdminStore();
    const adminLoginStore = useAdminLoginStore();
    const userStore = useUserStore();
    const router = useRouter();

    const defaultSystemStatsResponse: SystemStatsResponse = {
        total_users: 0,
        total_projects: 0,
        total_storage_bytes: 0,
        total_nodes_output: 0,
    };
    const defaultStorageStats: StorageStats = {
        total_storage_bytes: 0,
        guest_storage_bytes: 0,
        example_storage_bytes: 0,
        top_users: [],
    };
    const defaultProjectStats: ProjectStats = {
        total_projects: 0,
        explore_projects: 0,
        recent_updates: 0,
    };
    const defaultSystemHealthResponse: SystemHealthResponse = {
        fastapi_latency_ms: 0,
        postgres: {
            latency_ms: 0,
            status: PostgresMetrics.status.HEALTHY,
            total_connections: 0,
            active_connections: 0,
            idle_connections: 0,
        },
        redis: {
            status: RedisMetrics.status.HEALTHY,
        },
        celery: {
            status: CeleryMetrics.status.HEALTHY,
            active_tasks: 0,
            waiting_tasks: 0,
            revoked_tasks: 0,
            worker_count: 0,
            worker_names: []
        },
        minio: {
            status: MinioMetrics.status.HEALTHY,
            bucket_count: 0,
            buckets: []
        },
    };

    const currentDemo = ref<string>("");
    const currentAdmin = ref<string>(userStore.currentUserInfo.username || "DefaultAdmin");
    const systemStatus = ref<SystemStatsResponse>(defaultSystemStatsResponse);
    const serverStorageStatus = ref<StorageStats>(defaultStorageStats);
    const financialStatus = ref<Array<FinancialSymbolStats>>([]);
    const projectStatus = ref<ProjectStats>(defaultProjectStats);
    const systemHealthStatus = ref<SystemHealthResponse>(defaultSystemHealthResponse);

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

    async function handleGetSystemStatus() {
        currentDemo.value = "loading";
        systemStatus.value = await adminStore.getSystemStatus();
        currentDemo.value = "systemStatus";
    }

    async function handleGetServerStorageStatus(limit: number = 10) {
        currentDemo.value = "loading";
        serverStorageStatus.value = await adminStore.getServerStorageStatus(limit);
        currentDemo.value = "serverStorageStatus";
    }

    async function handleGetFinancialStatus() {
        currentDemo.value = "loading";
        financialStatus.value = await adminStore.getFinancialStatus();
        currentDemo.value = "financialStatus";
    }

    async function handleGetProjectStatus() {
        currentDemo.value = "loading";
        projectStatus.value = await adminStore.getProjectStatus();
        currentDemo.value = "projectStatus";
    }

    async function handleToggleProjectAccessible(id: number, show: boolean) {
        currentDemo.value = "loading";
        await adminStore.toggleProjectAccessible(id, show);
        currentDemo.value = "projectManagement"
    }

    async function handleGetSystemHealthStatus() {
        currentDemo.value = "loading";
        systemHealthStatus.value = await adminStore.getSystemHealthStatus();
        currentDemo.value = "systemHealthStatus";
    }

    async function handleLogout() {
        await adminLoginStore.logout();
        router.replace("/home");
    }
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
                <button @click="handleGetSystemStatus">系统状态</button>
                <button @click="handleGetServerStorageStatus(10)">服务器存储状态</button>
                <button @click="handleGetFinancialStatus">财务状态</button>
                <button @click="handleGetProjectStatus">项目状态</button>
                <button @click="handleGetSystemHealthStatus">系统健康状态</button>
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
            <div class="demo-container" v-if="currentDemo === 'systemStatus'">
                <SystemStatus :systemStatus="systemStatus" />
            </div>
            <div class="demo-container" v-else-if="currentDemo === 'serverStorageStatus'">
                <ServerStorageStatus :serverStorageStatus="serverStorageStatus" />
            </div>
            <div class="demo-container" v-else-if="currentDemo === 'financialStatus'">
                <FinancialStatus :financialStatus="financialStatus" />
            </div>
            <div class="demo-container" v-else-if="currentDemo === 'projectStatus'">
                <ProjectStatus :projectStatus="projectStatus" />
            </div>
            <div class="demo-container" v-else-if="currentDemo === 'systemHealthStatus'">
                <SystemHealthStatus :systemHealthStatus="systemHealthStatus" />
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