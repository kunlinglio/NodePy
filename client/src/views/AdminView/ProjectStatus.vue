<script lang="ts" setup>
    import { ref } from "vue";
    const props = defineProps<{
        projectStatus: any
    }>();
</script>
<template>
    <div class="system-status-container">
        <pre>{{ props.projectStatus }}</pre>
    </div>
</template>
<style scoped lang="scss">

</style>