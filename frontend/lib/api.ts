/**
 * API Client - Secure Backend-for-Frontend (BFF) Pattern
 *
 * All API requests go through /api/proxy which handles:
 * - Token storage in HttpOnly cookies (not accessible to JavaScript)
 * - Automatic token refresh on 401 responses
 * - Protection against XSS token theft
 */

export class ApiError extends Error {
  status: number;
  detail: string;
  errorCode?: string;

  constructor(status: number, detail: string, errorCode?: string) {
    super(detail);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
    this.errorCode = errorCode;
  }
}

let isRefreshing = false;
let refreshPromise: Promise<boolean> | null = null;

async function refreshToken(): Promise<boolean> {
  try {
    const res = await fetch('/api/auth/refresh', {
      method: 'POST',
      credentials: 'include',
    });
    return res.ok;
  } catch {
    return false;
  }
}

function getToken(): string | null {
  if (typeof document === 'undefined') return null;
  return document.cookie
    .split('; ')
    .find((row) => row.startsWith('token='))
    ?.split('=')
    .slice(1)
    .join('=') || null; // Handle tokens containing '='
}

export async function apiRequest<T = unknown>(
  endpoint: string,
  options: RequestInit = {},
  retryOnUnauth = true
): Promise<T> {
  // Route through proxy for secure token handling
  // Remove leading /api if present since proxy adds it
  const path = endpoint.startsWith('/api/') ? endpoint.slice(5) : endpoint.replace(/^\//, '');
  const proxyUrl = `/api/proxy/${path}`;
  const token = getToken();

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const res = await fetch(proxyUrl, {
  const res = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
    credentials: 'include',
  });

  // Handle 401 - proxy handles refresh, but if it still fails, redirect
  if (res.status === 401) {
    if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
      window.location.href = '/login';
  // Handle 401 with token refresh
  if (res.status === 401 && retryOnUnauth) {
    // Prevent multiple simultaneous refresh attempts
    if (!isRefreshing) {
      isRefreshing = true;
      refreshPromise = refreshToken();
    }
    throw new ApiError(401, 'Session expired. Please log in again.', 'SESSION_EXPIRED');
  }

    const refreshed = await refreshPromise;
    isRefreshing = false;
    refreshPromise = null;

    if (refreshed) {
      // Retry the request with new token
      return apiRequest<T>(endpoint, options, false);
    }

    // Refresh failed, redirect to login
    if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
      window.location.href = '/login';
    }
    throw new ApiError(401, 'Session expired. Please log in again.', 'SESSION_EXPIRED');
  }

  if (!res.ok) {
    // Try to parse error detail from response
    let detail = `API error: ${res.status}`;
    let errorCode: string | undefined;

    try {
      const errorData = await res.json();
      if (errorData.detail) {
        detail = typeof errorData.detail === 'string'
          ? errorData.detail
          : JSON.stringify(errorData.detail);
      }
      errorCode = errorData.error_code;
    } catch {
      // Use default error message
    }

    throw new ApiError(res.status, detail, errorCode);
  }

  // Handle empty responses (204 No Content, etc.)
  const contentType = res.headers.get('content-type');
  if (!contentType || !contentType.includes('application/json')) {
    return {} as T;
  }

  return res.json();
}

// Type definitions
interface UserResponse {
  id: string;
  email: string;
  name: string | null;
  plan: 'free' | 'pro' | 'admin';
  usage_seconds: number;
  created_at: string;
}

interface ProjectResponse {
  id: string;
  name: string;
  description: string | null;
  status: 'created' | 'uploading' | 'processing_stems' | 'stems_ready' | 'generating_vocals' | 'vocals_ready' | 'mixing' | 'completed' | 'failed';
  vocal_mode: 'remove' | 'replace' | 'blend';
  duration_seconds: number | null;
  mix_settings: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

interface ProjectListResponse {
  items: ProjectResponse[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

interface VoicePersonaResponse {
  id: string;
  name: string;
  description: string | null;
  status: 'pending' | 'training' | 'ready' | 'failed';
  created_at: string;
  updated_at: string;
}

interface VoicePersonaListResponse {
  items: VoicePersonaResponse[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

interface MessageResponse {
  message: string;
}

interface HealthResponse {
  status: string;
  database: string;
  redis: string;
  version: string;
}

export const api = {
  auth: {
    login: async (email: string, password: string) => {
      // Use Next.js API route for secure cookie handling
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
        credentials: 'include',
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new ApiError(res.status, errorData.detail || 'Login failed');
      }

      return res.json();
    },
    register: (data: { email: string; password: string; name?: string }) =>
      apiRequest<UserResponse>('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    logout: async () => {
      // Use Next.js API route for secure cookie handling
      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include',
      });
      return { message: 'Successfully logged out' };
    },
    refresh: () =>
      fetch('/api/auth/refresh', {
        method: 'POST',
        credentials: 'include',
      }),
  },
  user: {
    me: () => apiRequest<UserResponse>('/api/users/me'),
  },
  projects: {
    list: (page = 1, pageSize = 20) =>
      apiRequest<ProjectListResponse>(`/api/projects?page=${page}&page_size=${pageSize}`),
    get: (id: string) => apiRequest<ProjectResponse>(`/api/projects/${id}`),
    create: (data: { name: string; description?: string }) =>
      apiRequest<ProjectResponse>('/api/projects', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: string, data: { name?: string; description?: string }) =>
      apiRequest<ProjectResponse>(`/api/projects/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      apiRequest<MessageResponse>(`/api/projects/${id}`, { method: 'DELETE' }),
    upload: async (id: string, file: File) => {
      const formData = new FormData();
      formData.append('file', file);

      // Use proxy for secure token handling
      const res = await fetch(`/api/proxy/projects/${id}/upload`, {
        method: 'POST',
        body: formData,
        credentials: 'include',
      const token = getToken();
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch(`${API_URL}/api/projects/${id}/upload`, {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new ApiError(res.status, errorData.detail || 'Upload failed');
      }

      return res.json();
    },
  },
  voices: {
    list: (page = 1, pageSize = 20) =>
      apiRequest<VoicePersonaListResponse>(`/api/voices?page=${page}&page_size=${pageSize}`),
    get: (id: string) => apiRequest<VoicePersonaResponse>(`/api/voices/${id}`),
    create: (data: { name: string; description?: string }) =>
      apiRequest<VoicePersonaResponse>('/api/voices', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      apiRequest<MessageResponse>(`/api/voices/${id}`, { method: 'DELETE' }),
    uploadSample: async (id: string, file: File) => {
      const formData = new FormData();
      formData.append('file', file);

      // Use proxy for secure token handling
      const res = await fetch(`/api/proxy/voices/${id}/samples`, {
        method: 'POST',
        body: formData,
        credentials: 'include',
      const token = getToken();
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch(`${API_URL}/api/voices/${id}/samples`, {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new ApiError(res.status, errorData.detail || 'Upload failed');
      }

      return res.json();
    },
  },
  health: {
    check: () => apiRequest<HealthResponse>('/api/health'),
    detailed: () => apiRequest<HealthResponse & { database_latency_ms: number; redis_latency_ms: number }>('/api/health/detailed'),
  },
};
