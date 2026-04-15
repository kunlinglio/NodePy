<script lang="ts" setup>
</script>
<template>
    <div class="filebank">
        <img src="/public/filebank.png" alt="File Bank" style="width: auto; height: 100%; object-fit: contain;">
    </div>
</template>
<style lang="scss" scoped>
.filebank{
  width: fit-content;    /* 宽度随内容（图片） */
  margin: 0 auto;        /* 居中 */
  height: 500px;         /* 固定高度 */
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 4px 4px 20px rgba(0, 0, 0, 0.1);
}

.filebank__img{
  display: block;
  height: 500px; /* 图片高度固定为 500px */
  width: auto;   /* 宽度按比例自适应（保持原始宽高比） */
  object-fit: contain;
}
</style>
