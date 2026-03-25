// utils/api/services/adminAuthHelper.ts
import { DefaultService } from './api/services/DefaultService';
import AdminAuthenticatedServiceFactory from './AdminAuthenticatedServiceFactory';
import type { LoginRequest } from './api/models/LoginRequest';
import type { TokenResponse } from './api/models/TokenResponse';

// 环境判断
const isDev = import.meta.env.DEV;

/**
 * Admin 登录函数
 */
export const adminLogin = async (credentials: LoginRequest): Promise<TokenResponse> => {
  try {
    const response = await DefaultService.loginApiAdminLoginPost(credentials);

    if (response.access_token) {
      AdminAuthenticatedServiceFactory.setToken(response.access_token);
      isDev && console.log('✅ Admin 登录成功');
    }

    return response;
  } catch (error) {
    console.error('❌ Admin 登录失败:', error);
    throw error;
  }
};

/**
 * Admin 登出函数
 */
export const adminLogout = async (): Promise<void> => {
  try {
    await DefaultService.logoutApiAdminLogoutPost();
  } catch (error) {
    console.error('Admin 登出 API 调用失败:', error);
  } finally {
    AdminAuthenticatedServiceFactory.clearToken();
    isDev && console.log('✅ Admin 已登出');
  }
};

/**
 * 获取 admin 认证服务（用于 API 调用）
 */
export const getAdminService = () => {
  return AdminAuthenticatedServiceFactory.getService();
};

/**
 * 检查是否已登录为 admin
 * （实际检查是否有有效的 admin token）
 */
export const isAdminLoggedIn = (): boolean => {
  return AdminAuthenticatedServiceFactory.getServiceStatus().hasToken;
};

/**
 * 获取当前 admin token
 */
export const getCurrentAdminToken = (): string | null => {
  return localStorage.getItem('admin_access_token');
};