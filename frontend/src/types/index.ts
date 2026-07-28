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
  timestamp?: string;
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

export interface LLMProvider {
  id: string;
  name: string;
  models: string[];
}

export interface CharacterInfo {
  name: string;
  role: string;
  appearance: Record<string, any>;
  voice: Record<string, any>;
  costume: Record<string, any>;
}

export interface WorldInfo {
  name: string;
  description: string;
  atmosphere?: string;
  time_period?: string;
}

export interface EpisodeInfo {
  title: string;
  scenes: any[];
  summary?: string;
}

export interface PipelineStatus {
  status: string;
  movies_dir: string;
  scenes_per_episode: number;
  max_parallel_jobs: number;
}
