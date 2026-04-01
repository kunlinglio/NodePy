<script lang="ts" setup>
import { useLoginStore } from '@/stores/loginStore';
import { useModalStore } from '@/stores/modalStore';
import { useUserStore } from '@/stores/userStore';
import { useRouter } from 'vue-router';
import notify from './Notification/notify';

const router = useRouter();
const modalStore = useModalStore();
const loginStore = useLoginStore();
const userStore = useUserStore();

function handleConfirm() {
  modalStore.deactivateModal('user-access');
  modalStore.destroyModal('user-access');
}
</script>

<template>
  <div class="admin-account-wrapper">
    <div class="warning-container">
      <div class="warning-text">
        当前用户退出登录后才能进入管理员登录界面。
      </div>
    </div>
    <div class="action-buttons-container">
      <button class="btn confirm-btn" @click="handleConfirm">我已知晓</button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use "../common/global.scss" as *;

.admin-account-wrapper {
  display: flex;
  flex-direction: column;
  width: 200px;
  padding-bottom: 5px;
}

.warning-container {
  display: flex;
  flex-direction: column;
  padding-top: 20px;
  margin-bottom: 20px;
  height: 80px;
  gap: 10px;
}

.warning-text {
  font-size: 16px;
  text-align: center;
}

.action-buttons-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.btn {
  width: 100%;
  font-size: 16px;
  font-weight: bold;
  border-radius: 10px;
  box-shadow: 5px 5px 50px rgba(128, 128, 128, 0.12);
  transition: transform 0.12s ease, box-shadow 0.12s ease,
    background-color 0.12s ease;
}

.confirm-btn {
  background-color: #1890ff; // 蓝色确认按钮，可根据需要调整
  color: white;
  border: none;
  @include confirm-button-style; // 复用原有的按钮样式 mixin，若希望完全一致可调整
}

.confirm-btn:hover {
  @include confirm-button-hover-style;
}
</style>