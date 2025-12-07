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
    // Handle 401 by clearing token and redirecting
    if (res.status === 401) {
      if (typeof document !== 'undefined') {
        document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
        if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
      }
    }

    // Try to parse error detail from response
    let detail = `API error: ${res.status}`;
    try {
      const errorData = await res.json();
      if (errorData.detail) {
        detail = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
      }
    } catch {
      // Use default error message
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

interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

interface UserResponse {
  id: string;
  email: string;
  name: string | null;
  plan: string;
  usage_seconds: number;
  created_at: string;
}

interface ProjectResponse {
  id: string;
  name: string;
  description: string | null;
  status: string;
  vocal_mode: string;
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

export const api = {
  auth: {
    login: (email: string, password: string) =>
      apiRequest<Token>('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }),
    register: (data: { email: string; password: string; name?: string }) =>
      apiRequest<UserResponse>('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    logout: () => apiRequest<{ message: string }>('/api/auth/logout', { method: 'POST' }),
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
      apiRequest<{ message: string }>(`/api/projects/${id}`, { method: 'DELETE' }),
  },
  voices: {
    list: () =>
      apiRequest<
        Array<{
          id: string;
          name: string;
          description: string | null;
        }>
      >('/api/voices'),
    get: (id: string) => apiRequest(`/api/voices/${id}`),
    create: (data: { name: string; description?: string }) =>
      apiRequest('/api/voices', { method: 'POST', body: JSON.stringify(data) }),
    delete: (id: string) => apiRequest(`/api/voices/${id}`, { method: 'DELETE' }),
  },
};
