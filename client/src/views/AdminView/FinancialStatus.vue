<script lang="ts" setup>
    import { ref } from "vue";
    import { type FinancialSymbolStats } from "@/utils/api";
    const props = defineProps<{
        financialStatus: Array<FinancialSymbolStats>
    }>();
</script>
<template>
    <div class="system-status-container">
        <pre>{{ props.financialStatus }}</pre>
    </div>
</template>
<style scoped lang="scss">

</style>