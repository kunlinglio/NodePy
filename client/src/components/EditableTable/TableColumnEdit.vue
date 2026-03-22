<template>
  <div class="column-edit-modal">
    <div class="form-item">
      <label>列名</label>
      <input
        v-model="localColName"
        type="text"
        placeholder="请输入列名"
        class="name-input"
        @keyup.enter="confirm"
      />
    </div>
    <div class="form-item">
      <label>类型</label>
      <select v-model="localColType" class="type-select">
        <option v-for="type in typeOptions" :key="type" :value="type">
          {{ type }}
        </option>
      </select>
    </div>
    <div class="button-container">
      <button class="button confirm-button" @click="confirm">确定</button>
      <button class="button cancel-button" @click="cancel">取消</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
  initialName: string;
  initialType: string;
  onConfirm: (name: string, type: string) => void;
  onCancel: () => void;
}>();

const typeOptions = ['int', 'float', 'str', 'bool', 'Datetime'];
const localColName = ref(props.initialName);
const localColType = ref(props.initialType);

function confirm() {
  if (!localColName.value.trim()) {
    alert('列名不能为空');
    return;
  }
  props.onConfirm(localColName.value.trim(), localColType.value);
}

function cancel() {
  props.onCancel();
}
</script>

<style scoped lang="scss">
@use '@/common/global.scss' as *;

.column-edit-modal {
  padding: 20px;
  min-width: 300px;
}

.form-item {
  margin-bottom: 16px;

  label {
    display: block;
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 8px;
    color: #606266;
  }

  .name-input {
    @include input-style;
    width: 100%;
    &:focus {
      @include input-focus-style;
    }
  }

  .type-select {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s;
    &:focus {
      border-color: #409eff;
    }
  }
}

.button-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-top: 20px;
}

.button {
  width: 100%;
  &.confirm-button {
    @include confirm-button-style;
    &:hover {
      @include confirm-button-hover-style;
    }
  }
  &.cancel-button {
    margin-top: 10px;
    @include cancel-button-style;
    &:hover {
      @include cancel-button-hover-style;
    }
  }
}
</style>