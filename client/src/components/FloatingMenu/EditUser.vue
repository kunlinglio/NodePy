<script lang="ts" setup>
    const labelPosition = 'top';
</script>

<template>
    <div class="edit-user-container">
        <el-form :label-position="labelPosition">
            <el-form-item label="用户名">
                <input class="name-input" placeholder="请输入用户名" ></input>
            </el-form-item>
            <el-form-item label="邮箱">
                <input class="name-input" placeholder="请输入邮箱" ></input>
            </el-form-item>
            <el-form-item label="新密码">
                <input type="password" class="name-input" placeholder="留空则不修改密码" ></input>
            </el-form-item>
            <el-form-item label="确认新密码">
                <input type="password" class="name-input" placeholder="请再次输入新密码" ></input>
            </el-form-item>
        </el-form>
        <div class="button-container">
            <button @click="" class="confirm-button">修改</button>
            <button @click="" class="cancel-button">取消</button>
        </div>
    </div>
</template>

<style lang="scss" scoped>
    @use "../../common/global.scss" as *;
    .edit-user-container {
        display: flex;
        flex-direction: column;
        width: 300px;
        padding-bottom: 5px;
    }
    
    .button-container {
        display: flex;
        flex-direction: column;
        width: 100%;
        gap: 10px;
    }

    .confirm-button{
        @include confirm-button-style;
    }

    .cancel-button{
        @include cancel-button-style;
    }

    .confirm-button:hover{
        @include confirm-button-hover-style;
    }

    .cancel-button:hover{
        @include cancel-button-hover-style;
    }

    .name-input{
        @include input-style;
    }

    .name-input:focus{
        @include input-focus-style;
    }
</style>