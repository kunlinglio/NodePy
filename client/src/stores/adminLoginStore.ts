// stores/adminLoginStore.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
    adminLogin,
    adminLogout,
    isAdminLoggedIn,
    getCurrentAdminToken
} from '@/utils/AdminAuthHelper'
import type { LoginRequest } from '@/utils/api'
import type { TokenResponse } from '@/utils/api'
import { ApiError } from '@/utils/api'
import { handleNetworkError } from '@/utils/networkError'
import notify from "@/components/Notification/notify"

export const useAdminLoginStore = defineStore('adminLogin', () => {
    // 状态 - 直接从 AdminAuthHelper 获取当前状态
    const loggedIn = ref<boolean>(isAdminLoggedIn())
    const token = ref<string | null>(getCurrentAdminToken())

    // 计算属性
    const isAuthenticated = computed(() => loggedIn.value)
    const currentToken = computed(() => token.value)

    // 检查认证状态（同步更新 store 状态）
    const checkAuthStatus = (): boolean => {
        const newStatus = isAdminLoggedIn()
        const newToken = getCurrentAdminToken()

        loggedIn.value = newStatus
        token.value = newToken

        return newStatus
    }

    // 登录
    const login = async (credentials: LoginRequest): Promise<TokenResponse> => {
        try {
            const response = await adminLogin(credentials)
            checkAuthStatus() // 更新 store 状态
            return response
        } catch (error) {
            // 网络错误
            if (error instanceof TypeError && error.message &&
                (error.message.includes('Network Error') || error.message.includes('Failed to fetch'))) {
                notify({
                    message: '无法连接到服务器，请检查网络连接',
                    type: 'error'
                })
            } else if (error instanceof ApiError) {
                // 处理 ApiError
                switch (error.status) {
                    case 401:
                        notify({
                            message: '用户名或密码错误',
                            type: 'error'
                        })
                        break
                    case 422:
                        notify({
                            message: '验证错误',
                            type: 'error'
                        })
                        break
                    case 500:
                        notify({
                            message: '服务器内部错误',
                            type: 'error'
                        })
                        break
                    default:
                        const errMsg = handleNetworkError(error)
                        notify({
                            message: errMsg,
                            type: 'error'
                        })
                        break
                }
            } else {
                const errMsg = handleNetworkError(error)
                notify({
                    message: errMsg,
                    type: 'error'
                })
            }
            throw error
        }
    }

    // 退出登录
    const logout = async (): Promise<void> => {
        try {
            await adminLogout()
            checkAuthStatus() // 更新 store 状态
        } catch (error) {
            // 网络错误
            if (error instanceof TypeError && error.message &&
                (error.message.includes('Network Error') || error.message.includes('Failed to fetch'))) {
                notify({
                    message: '无法连接到服务器，您可能仍处于登录状态',
                    type: 'error'
                })
            } else if (error instanceof ApiError) {
                switch (error.status) {
                    case 401:
                        // Token 已失效，但仍清除本地状态
                        checkAuthStatus()
                        notify({
                            message: '会话已过期',
                            type: 'warning'
                        })
                        return
                    case 500:
                        notify({
                            message: '服务器内部错误',
                            type: 'error'
                        })
                        break
                    default:
                        const errMsg = handleNetworkError(error)
                        notify({
                            message: errMsg,
                            type: 'error'
                        })
                        break
                }
            } else if (error instanceof Error) {
                notify({
                    message: '登出失败: ' + error.message,
                    type: 'error'
                })
            } else {
                const errMsg = handleNetworkError(error)
                notify({
                    message: errMsg,
                    type: 'error'
                })
            }
            throw error
        }
    }

    return {
        // 状态
        loggedIn,
        token,

        // 计算属性
        isAuthenticated,
        currentToken,

        // 方法
        checkAuthStatus,
        login,
        logout
    }
})