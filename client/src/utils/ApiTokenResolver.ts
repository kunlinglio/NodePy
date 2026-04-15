import type { ApiRequestOptions } from './api/core/ApiRequestOptions';
import { OpenAPI } from './api/core/OpenAPI';

export const USER_ACCESS_TOKEN_KEY = 'access_token';
export const ADMIN_ACCESS_TOKEN_KEY = 'admin_access_token';

const getStorageItem = (key: string): string => {
  if (typeof window === 'undefined') {
    return '';
  }
  return window.localStorage.getItem(key) ?? '';
};

const getTokenKeyForRequest = (options: ApiRequestOptions): string => {
  return options.url.startsWith('/api/admin/')
    ? ADMIN_ACCESS_TOKEN_KEY
    : USER_ACCESS_TOKEN_KEY;
};

export const resolveTokenForRequest = async (options: ApiRequestOptions): Promise<string> => {
  return getStorageItem(getTokenKeyForRequest(options));
};

export const installApiTokenResolver = (): void => {
  if (OpenAPI.TOKEN !== resolveTokenForRequest) {
    OpenAPI.TOKEN = resolveTokenForRequest;
  }
};
