import { CancelablePromise } from './api/core/CancelablePromise';
import { DefaultService } from './api/services/DefaultService';
import { ADMIN_ACCESS_TOKEN_KEY, installApiTokenResolver } from './ApiTokenResolver';

const isDev = import.meta.env.DEV;

export class AdminAuthError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AdminAuthError';
  }
}

type ExcludedAdminMethods =
  | 'loginApiAdminAuthLoginPost'
  | 'refreshAccessTokenApiAdminAuthRefreshPost'
  | 'logoutApiAdminAuthLogoutPost'
  | 'spaFallbackFullPathGet';

type DefaultServiceMethodNames = {
  [K in keyof typeof DefaultService]:
    K extends ExcludedAdminMethods ? never :
    (typeof DefaultService)[K] extends (...args: any[]) => CancelablePromise<any> ? K : never
}[keyof typeof DefaultService];

export type AdminAuthenticatedService = {
  [K in DefaultServiceMethodNames]: (typeof DefaultService)[K];
};

const getCurrentAdminToken = (): string | undefined => {
  return localStorage.getItem(ADMIN_ACCESS_TOKEN_KEY) || undefined;
};

export const setAdminAuthToken = (token: string): void => {
  installApiTokenResolver();
  localStorage.setItem(ADMIN_ACCESS_TOKEN_KEY, token);
  if (isDev) {
    console.log('Admin token updated');
  }
};

export const clearAdminAuthToken = (): void => {
  installApiTokenResolver();
  localStorage.removeItem(ADMIN_ACCESS_TOKEN_KEY);
};

export const initAdminAuthToken = (): void => {
  installApiTokenResolver();
};

export function withAdminAuthMethod<T extends any[], R>(
  apiMethod: (...args: T) => CancelablePromise<R>
): (...args: T) => CancelablePromise<R> {
  return (...args: T): CancelablePromise<R> => {
    const executeWithAuth = async (retryCount = 0): Promise<R> => {
      try {
        return await apiMethod(...args);
      } catch (error: any) {
        console.error(`Admin API request failed (${apiMethod.name}):`, error);

        if (error.status === 401 && retryCount < 1) {
          try {
            const tokenResponse = await DefaultService.refreshAccessTokenApiAdminAuthRefreshPost();

            if (tokenResponse.access_token) {
              setAdminAuthToken(tokenResponse.access_token);
              return await executeWithAuth(retryCount + 1);
            }
          } catch (refreshError) {
            console.error('Admin token refresh failed:', refreshError);
            clearAdminAuthToken();
            throw new AdminAuthError(`Admin token refresh failed: ${refreshError}`);
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

export function createAdminAuthenticatedService(): AdminAuthenticatedService {
  initAdminAuthToken();

  const authenticatedService = {} as AdminAuthenticatedService;
  const excludedMethods: ExcludedAdminMethods[] = [
    'loginApiAdminAuthLoginPost',
    'refreshAccessTokenApiAdminAuthRefreshPost',
    'logoutApiAdminAuthLogoutPost',
    'spaFallbackFullPathGet',
  ];

  const methodNames = getStaticMethodNames(DefaultService)
    .filter(methodName => !excludedMethods.includes(methodName as ExcludedAdminMethods));

  methodNames.forEach(methodName => {
    try {
      (authenticatedService as any)[methodName] = withAdminAuthMethod(
        (DefaultService as any)[methodName]
      );
    } catch (error) {
      console.error(`Failed to wrap admin authenticated method ${methodName}:`, error);
    }
  });

  return authenticatedService;
}

export function getAdminServiceStatus(service: AdminAuthenticatedService) {
  const hasToken = !!getCurrentAdminToken();
  return {
    serviceAvailable: !!service,
    methodCount: Object.keys(service || {}).length,
    hasToken,
    tokenSource: hasToken ? 'localStorage' : 'none',
    methods: Object.keys(service || {}).filter(key => typeof service[key] === 'function'),
  };
}
