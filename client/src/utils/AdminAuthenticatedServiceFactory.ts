// services/AdminAuthenticatedServiceFactory.ts
import {
  createAdminAuthenticatedService,
  type AdminAuthenticatedService,
  getAdminServiceStatus,
  setAdminAuthToken,
  clearAdminAuthToken,
  initAdminAuthToken
} from './AdminAuthenticatedServiceDecorator';

// 环境判断
const isDev = import.meta.env.DEV;

/**
 * Admin 认证服务工厂
 */
class AdminAuthenticatedServiceFactory {
  private static _authenticatedService: AdminAuthenticatedService;

  /**
   * 初始化工厂
   */
  static init() {
    initAdminAuthToken();
    this._authenticatedService = createAdminAuthenticatedService();
  }

  /**
   * 获取 admin 认证服务实例
   */
  static getService(): AdminAuthenticatedService {
    if (!this._authenticatedService) {
      this.init();
    }
    return this._authenticatedService;
  }

  /**
   * 刷新 admin 认证服务
   */
  static refreshService(): AdminAuthenticatedService {
    this._authenticatedService = createAdminAuthenticatedService();
    return this._authenticatedService;
  }

  /**
   * 设置 admin 认证 token
   */
  static setToken(token: string): void {
    setAdminAuthToken(token);
  }

  /**
   * 清除 admin 认证 token
   */
  static clearToken(): void {
    clearAdminAuthToken();
  }

  /**
   * 获取 admin 服务状态信息
   */
  static getServiceStatus() {
    const service = this.getService();
    return {
      environment: import.meta.env.MODE,
      ...getAdminServiceStatus(service)
    };
  }

  /**
   * 开发工具：手动刷新服务
   */
  static devRefresh() {
    if (isDev) {
      this.refreshService();
    }
  }

  /**
   * 检查 admin 服务是否包含特定方法
   */
  static hasMethod(methodName: string): boolean {
    const service = this.getService();
    return methodName in service && typeof service[methodName as keyof AdminAuthenticatedService] === 'function';
  }
}

// 在模块加载时自动初始化
AdminAuthenticatedServiceFactory.init();

// 在开发环境中将工厂挂载到 window，方便调试
if (isDev) {
  (window as any).AdminAuthenticatedServiceFactory = AdminAuthenticatedServiceFactory;
}

export default AdminAuthenticatedServiceFactory;