<script lang="ts" setup>
    import type { TagInstance } from '@/types/tag';
    const props = defineProps<{
        tag: TagInstance
    }>()

    // 生成随机颜色
    function getRandomColor(): string {
        const colors = [
            '#FFE5B4', // 浅橙色
            '#B4E0FF', // 浅蓝色
            '#C2F2E8', // 浅青绿色
            '#E6D3FF', // 浅紫色
            '#FFD6E0', // 浅粉色
            '#D4F7D4', // 浅绿色
            '#FFFACD', // 柠檬 chiffon
            '#F0FFF0', // 蜂蜜露白
            '#F5F5DC', // 米白色
            '#E6F3FF', // 淡天蓝色
            '#FFF0F5', // 淡紫红色
            '#FDFD96', // 浅黄色
            '#E0FFFF', // 淡青色
            '#DDF8D8', // 浅薄荷绿
            '#FFE4E1', // 淡玫瑰红
            '#F0E68C', // 卡其色
            '#D8BFD8', // 蓟色
            '#AFEEEE', // 淡青绿
            '#F5DEB3', // 小麦色
            '#DEB887'  // 沙棕色
        ];
        
        const randomIndex = Math.floor(Math.random() * colors.length);
        return colors[randomIndex]!;
    }
    
    // 获取标签颜色
    const tagColor = getRandomColor();
    
</script>
<template>
    <div class="tag" 
        :style="{backgroundColor: tagColor}">
        {{ props.tag.content }}
    </div>
</template>
<style scoped lang="scss">
.tag{
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 2px 4px 2px 4px;
    max-width: 80px;
    color: grey;
    border-radius: 4px;
    // border: 1px solid black;
}
</style>