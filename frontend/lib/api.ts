const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

export async function apiRequest<T = unknown>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token =
    typeof document !== 'undefined'
      ? document.cookie
          .split('; ')
          .find((row) => row.startsWith('token='))
          ?.split('=')[1]
      : null;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const res = await fetch(`${API_URL}${endpoint}`, { ...options, headers });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const errorData = await res.json();
      detail = errorData.detail || errorData.message || detail;
    } catch {
      // Response is not JSON, use status text
      detail = res.statusText || detail;
    }

    // Handle specific status codes
    if (res.status === 401) {
      // Clear invalid token and redirect to login
      if (typeof document !== 'undefined') {
        document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
        if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
      }
    }

    throw new ApiError(res.status, detail);
  }

  // Handle empty responses (204 No Content, etc.)
  const contentType = res.headers.get('content-type');
  if (!contentType || !contentType.includes('application/json')) {
    return {} as T;
  }

  return res.json();
}

export const api = {
  auth: {
    login: (email: string, password: string) =>
      apiRequest<{ access_token: string; refresh_token: string; token_type: string }>(
        '/api/auth/login',
        { method: 'POST', body: JSON.stringify({ email, password }) }
      ),
    register: (data: { email: string; password: string; name?: string }) =>
      apiRequest<{ id: string; email: string; name: string | null }>(
        '/api/auth/register',
        { method: 'POST', body: JSON.stringify(data) }
      ),
    logout: () => apiRequest<{ message: string }>('/api/auth/logout', { method: 'POST' }),
  },
  user: {
    me: () =>
      apiRequest<{
        id: string;
        email: string;
        name: string | null;
        plan: string;
        usage_seconds: number;
      }>('/api/users/me'),
  },
  projects: {
    list: () =>
      apiRequest<
        Array<{
          id: string;
          name: string;
          description: string | null;
          status: string;
          created_at: string;
        }>
      >('/api/projects'),
    get: (id: string) => apiRequest(`/api/projects/${id}`),
    create: (data: { name: string; description?: string }) =>
      apiRequest('/api/projects', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: string, data: { name?: string; description?: string }) =>
      apiRequest(`/api/projects/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id: string) => apiRequest(`/api/projects/${id}`, { method: 'DELETE' }),
  },
  voices: {
    list: () =>
      apiRequest<
        Array<{
          id: string;
          name: string;
          description: string | null;
          status: string;
          created_at: string;
        }>
      >('/api/voices'),
    get: (id: string) => apiRequest(`/api/voices/${id}`),
    create: (data: { name: string; description?: string }) =>
      apiRequest('/api/voices', { method: 'POST', body: JSON.stringify(data) }),
    delete: (id: string) => apiRequest(`/api/voices/${id}`, { method: 'DELETE' }),
  },
};
