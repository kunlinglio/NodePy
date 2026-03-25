// services/AdminAuthenticatedServiceDecorator.ts
import { CancelablePromise } from './api/core/CancelablePromise';
import { OpenAPI } from './api/core/OpenAPI';
import { DefaultService } from './api/services/DefaultService';

// 环境判断
const isDev = import.meta.env.DEV;

/**
 * Admin 认证错误类
 */
export class AdminAuthError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AdminAuthError';
  }
}

// 定义排除的方法类型（admin 认证相关）
type ExcludedAdminMethods =
  | 'loginApiAdminLoginPost'
  | 'refreshAccessTokenApiAdminRefreshPost'
  | 'logoutApiAdminLogoutPost'
  | 'spaFallbackFullPathGet'; // SPA 回退也排除

// 使用条件类型排除特定方法
type DefaultServiceMethodNames = {
  [K in keyof typeof DefaultService]:
    K extends ExcludedAdminMethods ? never :
    (typeof DefaultService)[K] extends (...args: any[]) => CancelablePromise<any> ? K : never
}[keyof typeof DefaultService];

/**
 * Admin 认证服务类型：包含 DefaultService 的所有需要认证的方法（admin 和普通）
 */
export type AdminAuthenticatedService = {
  [K in DefaultServiceMethodNames]: (typeof DefaultService)[K];
};

/**
 * 安全地获取 token 字符串
 */
const getTokenString = (token: any): string | null => {
  return typeof token === 'string' ? token : null;
};

/**
 * 获取当前 admin token（优先从内存获取，其次从 localStorage）
 */
const getCurrentAdminToken = (): string | undefined => {
  return getTokenString(OpenAPI.TOKEN) || localStorage.getItem('admin_access_token') || undefined;
};

/**
 * 保存 admin token 到内存和本地存储
 */
export const setAdminAuthToken = (token: string): void => {
  OpenAPI.TOKEN = token;
  localStorage.setItem('admin_access_token', token);
  isDev && console.log('✅ Admin Token 已保存');
};

/**
 * 清除 admin token
 */
export const clearAdminAuthToken = (): void => {
  OpenAPI.TOKEN = undefined;
  localStorage.removeItem('admin_access_token');
};

/**
 * 初始化 admin token（应用启动时调用）
 */
export const initAdminAuthToken = (): void => {
  const savedToken = localStorage.getItem('admin_access_token');
  if (savedToken) {
    OpenAPI.TOKEN = savedToken;
  }
};

/**
 * 为单个 API 方法添加 admin 认证功能的装饰器
 */
export function withAdminAuthMethod<T extends any[], R>(
  apiMethod: (...args: T) => CancelablePromise<R>
): (...args: T) => CancelablePromise<R> {

  return (...args: T): CancelablePromise<R> => {

    const executeWithAuth = async (retryCount = 0): Promise<R> => {
      try {
        // 确保请求前有最新的 admin token
        const currentToken = getCurrentAdminToken();
        if (currentToken && getTokenString(OpenAPI.TOKEN) !== currentToken) {
          OpenAPI.TOKEN = currentToken;
        }

        const result = await apiMethod(...args);
        return result;

      } catch (error: any) {
        console.error(`❌ Admin API 请求失败 (${apiMethod.name}):`, error);

        const isAuthError = error.status === 401;

        if (isAuthError && retryCount < 1) {
          try {
            // 使用 admin 刷新端点
            const tokenResponse = await DefaultService.refreshAccessTokenApiAdminRefreshPost();

            if (tokenResponse.access_token) {
              setAdminAuthToken(tokenResponse.access_token);
              return await executeWithAuth(retryCount + 1);
            }
          } catch (refreshError) {
            console.error('❌ Admin Token 刷新失败:', refreshError);
            clearAdminAuthToken();
            throw new AdminAuthError(`Admin Token 刷新失败: ${refreshError}`);
          }
        }
        throw error;
      }
    };

    return new CancelablePromise<R>((resolve, reject) => {
      executeWithAuth()
        .then(resolve)
        .catch(reject);
    });
  };
}

/**
 * 获取类的所有静态方法名
 */
const getStaticMethodNames = (cls: any): string[] => {
  return Object.getOwnPropertyNames(cls)
    .filter(prop =>
      prop !== 'constructor' &&
      prop !== 'name' &&
      prop !== 'length' &&
      prop !== 'prototype' &&
      typeof cls[prop] === 'function'
    );
};

/**
 * 为整个服务添加 admin 认证功能
 */
export function createAdminAuthenticatedService(): AdminAuthenticatedService {
  // 初始化 admin token
  initAdminAuthToken();

  const authenticatedService = {} as AdminAuthenticatedService;

  // 不需要添加认证的方法列表（admin 认证相关）
  const excludedMethods: ExcludedAdminMethods[] = [
    'loginApiAdminLoginPost',
    'refreshAccessTokenApiAdminRefreshPost',
    'logoutApiAdminLogoutPost',
    'spaFallbackFullPathGet'
  ];

  // 获取并过滤方法
  const methodNames = getStaticMethodNames(DefaultService)
    .filter(methodName => !excludedMethods.includes(methodName as ExcludedAdminMethods));

  // 包装方法
  methodNames.forEach(methodName => {
    try {
      (authenticatedService as any)[methodName] = withAdminAuthMethod(
        (DefaultService as any)[methodName]
      );
    } catch (error) {
      console.error(`❌ 为方法 ${methodName} 添加 admin 认证功能失败:`, error);
    }
  });

  return authenticatedService;
}

/**
 * 开发工具：检查 admin 服务状态
 */
export function getAdminServiceStatus(service: AdminAuthenticatedService) {
  const hasToken = !!getCurrentAdminToken();
  return {
    serviceAvailable: !!service,
    methodCount: Object.keys(service || {}).length,
    hasToken,
    tokenSource: hasToken ? (getTokenString(OpenAPI.TOKEN) ? 'memory' : 'localStorage') : 'none',
    methods: Object.keys(service || {}).filter(key => typeof service[key] === 'function')
  };
}