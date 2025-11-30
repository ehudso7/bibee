const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const token = typeof document !== 'undefined'
    ? document.cookie.split('; ').find(row => row.startsWith('token='))?.split('=')[1]
    : null;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const res = await fetch(`${API_URL}${endpoint}`, { ...options, headers });

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }

  return res.json();
}

export const api = {
  auth: {
    login: (email: string, password: string) =>
      apiRequest('/api/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
    register: (data: { email: string; password: string; name?: string }) =>
      apiRequest('/api/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  },
  projects: {
    list: () => apiRequest('/api/projects'),
    get: (id: string) => apiRequest(`/api/projects/${id}`),
    create: (data: { name: string; description?: string }) =>
      apiRequest('/api/projects', { method: 'POST', body: JSON.stringify(data) }),
    delete: (id: string) => apiRequest(`/api/projects/${id}`, { method: 'DELETE' }),
  },
  voices: {
    list: () => apiRequest('/api/voices'),
    get: (id: string) => apiRequest(`/api/voices/${id}`),
    create: (data: { name: string; description?: string }) =>
      apiRequest('/api/voices', { method: 'POST', body: JSON.stringify(data) }),
    delete: (id: string) => apiRequest(`/api/voices/${id}`, { method: 'DELETE' }),
  },
};
