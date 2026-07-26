import { HealthStatus, AgentInfo, ChatResponse } from '../types';

const API_BASE = '/api/v1';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || error.error || 'Request failed');
  }
  return response.json();
}

export const api = {
  health: (): Promise<HealthStatus> => request('/health/'),

  agents: (): Promise<AgentInfo[]> => request('/agents/'),

  agent: (agentId: string): Promise<AgentInfo> => request(`/agents/${agentId}`),

  chat: (message: string, provider: string = 'openai'): Promise<ChatResponse> =>
    request('/chat/', {
      method: 'POST',
      body: JSON.stringify({ message, provider }),
    }),

  voices: (): Promise<{ voices: { name: string; description: string }[] }> =>
    request('/voice/voices'),
};

export default api;
