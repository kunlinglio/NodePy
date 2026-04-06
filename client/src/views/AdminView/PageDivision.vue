<template>
  <div class="pagination" v-if="totalPages > 1">
    <button
      class="page-btn"
      :disabled="currentPage === 1"
      @click="handlePageChange(currentPage - 1)"
    >
      上一页
    </button>
    <span class="page-info">第 {{ currentPage }} / {{ totalPages }} 页</span>
    <button
      class="page-btn"
      :disabled="currentPage === totalPages"
      @click="handlePageChange(currentPage + 1)"
    >
      下一页
    </button>

    <!-- 跳转控件 -->
    <div class="goto-container">
      <span class="goto-label">跳至</span>
      <input
        type="number"
        v-model.number="gotoPage"
        class="goto-input"
        :min="1"
        :max="totalPages"
        @keyup.enter="handleGoto"
      />
      <span class="goto-label">页</span>
      <button class="goto-btn" @click="handleGoto">GO</button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch } from 'vue';

const props = defineProps<{
  currentPage: number;
  totalPages: number;
}>();

const emit = defineEmits<{
  (e: 'pageChange', page: number): void;
}>();

const gotoPage = ref(props.currentPage);

// 同步输入框与当前页码
watch(() => props.currentPage, (newVal) => {
  gotoPage.value = newVal;
});

const handlePageChange = (page: number) => {
  if (page >= 1 && page <= props.totalPages) {
    emit('pageChange', page);
  }
};

const handleGoto = () => {
  let page = gotoPage.value;
  if (isNaN(page)) page = 1;
  page = Math.min(Math.max(page, 1), props.totalPages);
  if (page !== props.currentPage) {
    emit('pageChange', page);
  } else {
    gotoPage.value = props.currentPage;
  }
};
</script>

<style scoped lang="scss">
@use "sass:color";
$primary-color: #108efe;
$card-white: #ffffff;
$border-light: #eef2f8;
$text-gray: #5b6e8c;

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 24px;
  padding: 12px;
  flex-wrap: wrap;

  .page-btn {
    padding: 8px 16px;
    border-radius: 12px;
    background: $card-white;
    border: 1px solid $border-light;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s ease;

    &:hover:not(:disabled) {
      background: $primary-color;
      color: white;
      border-color: $primary-color;
      transform: translateY(-1px);
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }

  .page-info {
    font-size: 14px;
    color: $text-gray;
  }

  .goto-container {
    display: flex;
    align-items: center;
    gap: 8px;
    background: $card-white;
    padding: 4px 12px;
    border-radius: 20px;
    border: 1px solid $border-light;

    .goto-label {
      font-size: 13px;
      color: $text-gray;
    }

    .goto-input {
      width: 60px;
      padding: 6px 8px;
      border-radius: 8px;
      border: 1px solid $border-light;
      text-align: center;
      font-size: 14px;
      outline: none;
      transition: all 0.2s ease;

      /* 隐藏 number 输入框的上下箭头（Chrome/Safari/Edge） */
      &::-webkit-inner-spin-button,
      &::-webkit-outer-spin-button {
        -webkit-appearance: none;
        margin: 0;
      }
      /* Firefox */
      -moz-appearance: textfield;

      &:focus {
        border-color: $primary-color;
        box-shadow: 0 0 0 2px rgba(16, 142, 254, 0.1);
      }
    }

    .goto-btn {
      padding: 4px 12px;
      border-radius: 12px;
      background: $primary-color;
      color: white;
      border: none;
      cursor: pointer;
      font-size: 12px;
      font-weight: 500;
      transition: all 0.2s ease;

      &:hover {
        background: color.scale($primary-color, $lightness: -8%);
        transform: translateY(-1px);
      }
    }
  }
}

@media (max-width: 768px) {
  .pagination {
    gap: 12px;
    .goto-container {
      width: 100%;
      justify-content: center;
      margin-top: 8px;
    }
  }
}
</style>