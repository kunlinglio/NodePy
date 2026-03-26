<script lang="ts" setup>
    import { ref } from "vue";
    const props = defineProps<{
        serverStorageStatus: any
    }>();
</script>
<template>
    <div class="system-status-container">
        <pre>{{ props.serverStorageStatus }}</pre>
    </div>
</template>
<style scoped lang="scss">

</style>