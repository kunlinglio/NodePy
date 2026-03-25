<script setup lang="ts">
    import { useAdminStore } from "@/stores/adminStore";
    import { type SystemStatsResponse, type StorageStats, type FinancialSymbolStats, type ProjectStats, type SystemHealthResponse } from "@/utils/api";
    import { ref } from "vue";
    const adminStore = useAdminStore();
    const systemStatus = ref<SystemStatsResponse>();
    const serverStorageStatus = ref<StorageStats>();
    const financialStatus = ref<Array<FinancialSymbolStats>>();
    const projectStatus = ref<ProjectStats>();
    const systemHealthStatus = ref<SystemHealthResponse>();
    
    async function handleGetSystemStatus(){
        systemStatus.value = await adminStore.getSystemStatus();
    }

    async function handleGetServerStorageStatus(limit: number = 10){
        serverStorageStatus.value = await adminStore.getServerStorageStatus(limit);
    }

    async function handleGetFinancialStatus(){
        financialStatus.value = await adminStore.getFinancialStatus();
    }

    async function handleGetProjectStatus(){
        projectStatus.value = await adminStore.getProjectStatus();
    }

    async function handleToggleProjectAccessible(id: number, show: boolean){
        await adminStore.toggleProjectAccessible(id, show);
    }

    async function handleGetSystemHealthStatus(){
        systemHealthStatus.value = await adminStore.getSystemHealthStatus();
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
                bottombar
            </div>
        </div>
        <div class="right-container">
            <div class="topbar-container">
                topbar
            </div>
            <div class="demo-container">
                demo
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