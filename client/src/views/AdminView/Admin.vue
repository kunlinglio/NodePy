<script setup lang="ts">
    import { useAdminStore } from "@/stores/adminStore";
    import { useAdminLoginStore } from "@/stores/adminLoginStore";
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
    import { ref } from "vue";
    const adminStore = useAdminStore();
    const adminLoginStore = useAdminLoginStore();
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
    const systemStatus = ref<SystemStatsResponse>(defaultSystemStatsResponse);
    const serverStorageStatus = ref<StorageStats>(defaultStorageStats);
    const financialStatus = ref<Array<FinancialSymbolStats>>([]);
    const projectStatus = ref<ProjectStats>(defaultProjectStats);
    const systemHealthStatus = ref<SystemHealthResponse>(defaultSystemHealthResponse);
    
    
    async function handleGetSystemStatus(){
        systemStatus.value = await adminStore.getSystemStatus();
        currentDemo.value = "systemStatus";
    }

    async function handleGetServerStorageStatus(limit: number = 10){
        serverStorageStatus.value = await adminStore.getServerStorageStatus(limit);
        currentDemo.value = "serverStorageStatus";
    }

    async function handleGetFinancialStatus(){
        financialStatus.value = await adminStore.getFinancialStatus();
        currentDemo.value = "financialStatus";
    }

    async function handleGetProjectStatus(){
        projectStatus.value = await adminStore.getProjectStatus();
        currentDemo.value = "projectStatus";
    }

    async function handleToggleProjectAccessible(id: number, show: boolean){
        await adminStore.toggleProjectAccessible(id, show);
        currentDemo.value = "projectManagement"
    }

    async function handleGetSystemHealthStatus(){
        systemHealthStatus.value = await adminStore.getSystemHealthStatus();
        currentDemo.value = "systemHealthStatus";
    }

    async function handleLogout(){
        await adminLoginStore.logout();
        router.replace("/home");
    }
</script>
<template>
    <div class="page-container">
        <div class="left-container">
            <div class="icon-container">
                Icon
            </div>
            <div class="buttonlist-container">
                <button @click="handleGetSystemStatus">SystemStatus</button>
                <button @click="handleGetServerStorageStatus(10)">ServerStorageStatus</button>
                <button @click="handleGetFinancialStatus">FinancialStatus</button>
                <button @click="handleGetProjectStatus">ProjectStatus</button>
                <button @click="handleGetSystemHealthStatus">SystemHealthStatus</button>
            </div>
            <div class="bottombar-container">
                <button @click="handleLogout">
                    Logout
                </button>
            </div>
        </div>
        <div class="right-container">
            <div class="topbar-container">
                topbar
            </div>
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
        </div>
    </div>
</template>
<style scoped lang="scss">
    .page-container{
        width: 100%;
        height: 100%;
        display: flex;
    }
    .left-container{
        width: 200px;
        height: 100%;
        display: flex;
        flex-direction: column;
        border: 1px solid black;
        .icon-container{
            height: 100px;
            width: 100%;
            background-color: #f0f0f0;
            border: 1px solid black;
        }
        .buttonlist-container{
            display: flex;
            flex-direction: column;
            flex: 1;
            height: 100%;
            background-color: #e0e0e0;
            border: 1px solid black;
        }
        .bottombar-container{
            height: 80px;
            width: 100%;
            background-color: #d0d0d0;
            border: 1px solid black;
        }
    }
    .right-container{
        flex: 1;
        height: 100%;
        display: flex;
        flex-direction: column;
        .topbar-container{
            height: 100px;
            width: 100%;
            background-color: #f0f0f0;
            border: 1px solid black;
        }
        .demo-container{
            display: flex;
            flex: 1;
            background-color: #e0e0e0;
            border: 1px solid black;
        }
    }
</style>