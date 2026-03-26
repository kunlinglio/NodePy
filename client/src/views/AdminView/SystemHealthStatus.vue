<script lang="ts" setup>
    import { ref } from "vue";
    import { type SystemHealthResponse } from "@/utils/api"
    const props = defineProps<{
        systemHealthStatus: SystemHealthResponse
    }>();
</script>
<template>
    <div class="system-status-container">
        <pre>{{ props.systemHealthStatus }}</pre>
    </div>
</template>
<style scoped lang="scss">

</style>