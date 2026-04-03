<!-- Tag.vue -->
<script lang="ts" setup>
import type { TagInstance } from '@/types/tag';
import { computed } from 'vue';

const props = defineProps<{
    tag?: TagInstance;      // 原有的 tag 对象（兼容旧用法）
    content?: string;       // 直接传入标签文本（优先使用）
    color?: string;         // 可选固定颜色，若不传则根据文本计算
}>();

// 最终显示的文本
const displayContent = computed(() => {
    if (props.content) return props.content;
    if (props.tag) return props.tag.content;
    return '';
});

// 随机颜色（每个标签实例独立随机）
const tagColor = computed(() => {
    const colors = [
        '#FFE5B4', '#B4E0FF', '#C2F2E8', '#E6D3FF', '#FFD6E0',
        '#D4F7D4', '#FFFACD', '#F0FFF0', '#F5F5DC', '#E6F3FF',
        '#FFF0F5', '#FDFD96', '#E0FFFF', '#DDF8D8', '#FFE4E1',
        '#F0E68C', '#D8BFD8', '#AFEEEE', '#F5DEB3', '#DEB887'
    ];
    const randomIndex = Math.floor(Math.random() * colors.length);
    return colors[randomIndex]!;
});
</script>

<template>
    <div class="tag" :style="{ backgroundColor: tagColor }">
        {{ displayContent }}
        <span v-if="$slots.action" class="action-slot">
            <slot name="action" />
        </span>
    </div>
</template>

<style scoped lang="scss">
.tag {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    color: #2c3e50;
    background-color: #f0f2f5;
    white-space: nowrap;
    flex-shrink: 0;

    .action-slot {
        margin-left: 6px;
        display: inline-flex;
        align-items: center;
    }
}
</style>