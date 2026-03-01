<script lang="ts" setup>
    import type { TagInstance } from '@/types/tag';
    const props = defineProps<{
        tag: TagInstance
    }>()
</script>
<template>
    <div class="tag" 
        :style="{backgroundColor: props.tag.color}">
        {{ props.tag.content }}
    </div>
</template>
<style scoped lang="scss">
.tag{
    display: flex;
    justify-content: center;
    align-items: center;
    max-width: 80px;
    color: white;
    border-radius: 4px;
    border: 1px solid black;
}
</style>