import { defineStore } from 'pinia'
import { computed, watch } from 'vue'
import { useLoginStore } from './loginStore'
import { useAdminLoginStore } from './adminLoginStore'
import { DefaultService } from '@/utils/api/services/DefaultService'
import AuthenticatedServiceFactory from '@/utils/AuthenticatedServiceFactory'
import AdminAuthenticatedServiceFactory from '@/utils/AdminAuthenticatedServiceFactory'

// 刷新间隔（毫秒），可通过 VITE_TOKEN_REFRESH_MS 覆盖
const REFRESH_INTERVAL_MS = Number(import.meta.env.VITE_TOKEN_REFRESH_MS) || 9 * 60 * 1000

export const useAuthState = defineStore('authState', () => {
  const loginStore = useLoginStore()
  const adminLoginStore = useAdminLoginStore()

  // 管理员/用户互斥地被视为已登录
  const isUserAuthenticated = computed(() => !!loginStore.isAuthenticated && !adminLoginStore.isAuthenticated)
  const isAdminAuthenticated = computed(() => !!adminLoginStore.isAuthenticated && !loginStore.isAuthenticated)

  let userTimer: ReturnType<typeof setInterval> | null = null
  let adminTimer: ReturnType<typeof setInterval> | null = null

  async function refreshUserTokenOnce() {
    try {
      const resp = await DefaultService.refreshAccessTokenApiAuthRefreshPost()
      if (resp && (resp as any).access_token) {
        AuthenticatedServiceFactory.setToken((resp as any).access_token)
        // 同步更新 loginStore 状态
        loginStore.checkAuthStatus()
      }
    } catch (e) {
      // 刷新可能会因 refresh token 失效而失败，正常记录即可
      console.warn('User token refresh failed', e)
    }
  }

  async function refreshAdminTokenOnce() {
    try {
      const resp = await DefaultService.refreshAccessTokenApiAdminAuthRefreshPost()
      if (resp && (resp as any).access_token) {
        AdminAuthenticatedServiceFactory.setToken((resp as any).access_token)
        adminLoginStore.checkAuthStatus()
      }
    } catch (e) {
      console.warn('Admin token refresh failed', e)
    }
  }

  function startUserRefresh() {
    stopUserRefresh()
    if (isUserAuthenticated.value) {
      // 立即尝试刷新一次，然后开始定时
      refreshUserTokenOnce()
      userTimer = setInterval(refreshUserTokenOnce, REFRESH_INTERVAL_MS)
    }
  }

  function stopUserRefresh() {
    if (userTimer) {
      clearInterval(userTimer)
      userTimer = null
    }
  }

  function startAdminRefresh() {
    stopAdminRefresh()
    if (isAdminAuthenticated.value) {
      refreshAdminTokenOnce()
      adminTimer = setInterval(refreshAdminTokenOnce, REFRESH_INTERVAL_MS)
    }
  }

  function stopAdminRefresh() {
    if (adminTimer) {
      clearInterval(adminTimer)
      adminTimer = null
    }
  }

  // 根据登录状态自动启动/停止刷新
  watch(isUserAuthenticated, (val) => {
    if (val) startUserRefresh()
    else stopUserRefresh()
  }, { immediate: true })

  watch(isAdminAuthenticated, (val) => {
    if (val) startAdminRefresh()
    else stopAdminRefresh()
  }, { immediate: true })

  // 初始化（在 app 启动时调用）
  function init() {
    if (isUserAuthenticated.value) startUserRefresh()
    if (isAdminAuthenticated.value) startAdminRefresh()
  }

  return {
    isUserAuthenticated,
    isAdminAuthenticated,
    refreshUserTokenOnce,
    refreshAdminTokenOnce,
    startUserRefresh,
    stopUserRefresh,
    startAdminRefresh,
    stopAdminRefresh,
    init
  }
})
