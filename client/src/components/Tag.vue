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

// 现代化配色数组（莫兰迪/柔和色系）
const modernColors = [
    '#FEF3C7', // 琥珀浅色
    '#DBEAFE', // 蓝浅色
    '#D1FAE5', // 翠绿浅色
    '#E0E7FF', // 靛蓝浅色
    '#FCE7F3', // 粉红浅色
    '#E0F2FE', // 天蓝浅色
    '#CCFBF1', //  teal 浅色
    '#FED7AA', // 橙浅色
    '#ECFCCB', //  lime 浅色
    '#FFE4E6', // 玫瑰浅色
    '#F3E8FF', // 紫罗兰浅色
    '#FEF08A', // 黄浅色
    '#FFEDD5', // 暖橙浅色
    '#E6E6FA', // 薰衣草
    '#CFFAFE', // 浅青
    '#F1F5F9', // 石板灰
    '#FFF1F0', // 珊瑚浅色
    '#E5E7EB', // 冷灰
    '#FDF4FF', // 浅粉紫
    '#F0FDF4'  // 薄荷浅色
];

// 根据文本内容生成确定性的颜色（哈希取模）
const tagColor = computed(() => {
    // 优先使用外部传入的固定颜色
    if (props.color) return props.color;
    
    const content = displayContent.value;
    if (!content) return modernColors[0];
    
    // 简单哈希函数，保证相同内容得到相同颜色
    let hash = 0;
    for (let i = 0; i < content.length; i++) {
        hash = ((hash << 5) - hash) + content.charCodeAt(i);
        hash |= 0; // 转32位整数
    }
    const index = Math.abs(hash) % modernColors.length;
    return modernColors[index];
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
    font-weight: 500;       // 字体略微加粗
    color: #2c3e50;
    background-color: #f0f2f5;
    white-space: nowrap;
    flex-shrink: 0;
    transition: all 0.2s ease;

    .action-slot {
        margin-left: 6px;
        display: inline-flex;
        align-items: center;
    }
}

/* 支持外部传入的状态类，用于在不同上下文下呈现选中效果 */
.tag.tag-item {
    padding: 6px 12px;
    border-radius: 16px;
    font-size: 13px;
}

.tag.tag-selected {
    color: #ffffff;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.16);
}
</style>