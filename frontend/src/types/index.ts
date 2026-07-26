export interface AgentInfo {
  agent_id: string;
  name: string;
  role: string;
  status: 'active' | 'idle' | 'busy' | 'error' | 'offline';
  description?: string;
  capabilities: string[];
  created_at: string;
  last_active?: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

export interface ChatResponse {
  provider: string;
  model: string;
  response: string;
  usage: Record<string, number>;
  timestamp: string;
}

export interface HealthStatus {
  status: string;
  version: string;
  services: Record<string, string>;
  timestamp: string;
}

export interface TaskInfo {
  task_id: string;
  agent_id: string;
  task_type: string;
  description: string;
  priority: number;
  status: string;
}
