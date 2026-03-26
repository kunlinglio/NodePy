<script lang="ts" setup>
    import { ref } from "vue";
    import { type SystemStatsResponse } from "@/utils/api"
    const props = defineProps<{
        systemStatus: SystemStatsResponse
    }>();
</script>
<template>
    <div class="system-status-container">
        <pre>{{ props.systemStatus }}</pre>
    </div>
</template>
<style scoped lang="scss">

</style>