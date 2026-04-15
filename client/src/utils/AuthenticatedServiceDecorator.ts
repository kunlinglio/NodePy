import { CancelablePromise } from './api/core/CancelablePromise';
import { DefaultService } from './api/services/DefaultService';
import { USER_ACCESS_TOKEN_KEY, installApiTokenResolver } from './ApiTokenResolver';

const isDev = import.meta.env.DEV;

export class AuthError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AuthError';
  }
}

type ExcludedMethods =
  | 'refreshAccessTokenApiAuthRefreshPost'
  | 'loginApiAuthLoginPost'
  | 'signupApiAuthSignupPost'
  | 'logoutApiAuthLogoutPost'
  | 'spaFallbackFullPathGet';

type DefaultServiceMethodNames = {
  [K in keyof typeof DefaultService]:
    K extends ExcludedMethods ? never :
    (typeof DefaultService)[K] extends (...args: any[]) => CancelablePromise<any> ? K : never
}[keyof typeof DefaultService];

export type AuthenticatedService = {
  [K in DefaultServiceMethodNames]: (typeof DefaultService)[K];
};

const getCurrentToken = (): string | undefined => {
  return localStorage.getItem(USER_ACCESS_TOKEN_KEY) || undefined;
};

export const setAuthToken = (token: string): void => {
  installApiTokenResolver();
  localStorage.setItem(USER_ACCESS_TOKEN_KEY, token);
  if (isDev) {
    console.log('User token updated');
  }
};

export const clearAuthToken = (): void => {
  installApiTokenResolver();
  localStorage.removeItem(USER_ACCESS_TOKEN_KEY);
};

export const initAuthToken = (): void => {
  installApiTokenResolver();
};

export function withAuthMethod<T extends any[], R>(
  apiMethod: (...args: T) => CancelablePromise<R>
): (...args: T) => CancelablePromise<R> {
  return (...args: T): CancelablePromise<R> => {
    const executeWithAuth = async (retryCount = 0): Promise<R> => {
      try {
        return await apiMethod(...args);
      } catch (error: any) {
        console.error(`API request failed (${apiMethod.name}):`, error);

        if (error.status === 401 && retryCount < 1) {
          try {
            const tokenResponse = await DefaultService.refreshAccessTokenApiAuthRefreshPost();

            if (tokenResponse.access_token) {
              setAuthToken(tokenResponse.access_token);
              return await executeWithAuth(retryCount + 1);
            }
          } catch (refreshError) {
            console.error('User token refresh failed:', refreshError);
            clearAuthToken();
            throw new AuthError(`User token refresh failed: ${refreshError}`);
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

export function createAuthenticatedService(): AuthenticatedService {
  initAuthToken();

  const authenticatedService = {} as AuthenticatedService;
  const excludedMethods: ExcludedMethods[] = [
    'refreshAccessTokenApiAuthRefreshPost',
    'loginApiAuthLoginPost',
    'signupApiAuthSignupPost',
    'logoutApiAuthLogoutPost',
    'spaFallbackFullPathGet',
  ];

  const methodNames = getStaticMethodNames(DefaultService)
    .filter(methodName => !excludedMethods.includes(methodName as ExcludedMethods));

  methodNames.forEach(methodName => {
    try {
      (authenticatedService as any)[methodName] = withAuthMethod(
        (DefaultService as any)[methodName]
      );
    } catch (error) {
      console.error(`Failed to wrap authenticated method ${methodName}:`, error);
    }
  });

  return authenticatedService;
}

export function getServiceStatus(service: AuthenticatedService) {
  const hasToken = !!getCurrentToken();
  return {
    serviceAvailable: !!service,
    methodCount: Object.keys(service || {}).length,
    hasToken,
    tokenSource: hasToken ? 'localStorage' : 'none',
    methods: Object.keys(service || {}).filter(key => typeof service[key] === 'function'),
  };
}
