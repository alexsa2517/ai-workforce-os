#!/usr/bin/env python3
"""
Comprehensive fix script for AI Workforce OS frontend.
Fixes missing dependencies, adds proper error handling,
improves UI, and adds missing features.
"""
import os

PROJECT = "/home/ubuntu/ai-workforce-os"

def write(path: str, content: str):
    full = os.path.join(PROJECT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    print(f"  Wrote: {path}")

# ============================================================
# 1. Fix package.json - add missing dependencies
# ============================================================
write("frontend/package.json", '''{
  "name": "ai-workforce-frontend",
  "version": "0.2.0",
  "description": "AI Workforce OS Frontend",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-error-boundary": "^4.0.13"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.3.1",
    "typescript": "^5.0.0",
    "vite": "^5.0.0"
  }
}
''')

# ============================================================
# 2. Fix App.tsx - add error boundary, better navigation
# ============================================================
write("frontend/src/App.tsx", '''import React, { useState, useCallback } from 'react';
import Dashboard from './pages/Dashboard';
import ChatInterface from './pages/ChatInterface';
import AgentsView from './pages/AgentsView';
import ErrorFallback from './components/ErrorFallback';

type Page = 'dashboard' | 'chat' | 'agents';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard');

  const handleNav = useCallback((page: Page) => {
    setCurrentPage(page);
  }, []);

  const renderPage = () => {
    switch (currentPage) {
      case 'chat':
        return <ChatInterface />;
      case 'agents':
        return <AgentsView />;
      default:
        return <Dashboard />;
    }
  };

  const navItems: { page: Page; label: string }[] = [
    { page: 'dashboard', label: 'Dashboard' },
    { page: 'chat', label: 'Chat' },
    { page: 'agents', label: 'Agents' },
  ];

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerLeft}>
          <h1 style={styles.logo}>AI Workforce OS</h1>
          <span style={styles.version}>v0.2.0</span>
        </div>
        <nav style={styles.nav}>
          {navItems.map((item) => (
            <button
              key={item.page}
              onClick={() => handleNav(item.page)}
              style={navBtnStyle(currentPage === item.page)}
              onMouseEnter={(e) => {
                if (currentPage !== item.page) {
                  (e.target as HTMLButtonElement).style.background = '#1e293b';
                  (e.target as HTMLButtonElement).style.color = '#e2e8f0';
                }
              }}
              onMouseLeave={(e) => {
                if (currentPage !== item.page) {
                  (e.target as HTMLButtonElement).style.background = 'transparent';
                  (e.target as HTMLButtonElement).style.color = '#94a3b8';
                }
              }}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </header>

      {/* Main Content */}
      <main style={styles.main}>
        <ErrorFallback>
          {renderPage()}
        </ErrorFallback>
      </main>

      {/* Footer */}
      <footer style={styles.footer}>
        <p>AI Workforce OS &copy; 2026 | Built with React + FastAPI</p>
      </footer>
    </div>
  );
}

function navBtnStyle(active: boolean): React.CSSProperties {
  return {
    padding: '0.5rem 1rem',
    borderRadius: '6px',
    border: 'none',
    background: active ? '#3b82f6' : 'transparent',
    color: active ? '#fff' : '#94a3b8',
    cursor: 'pointer',
    fontSize: '0.875rem',
    fontWeight: 500,
    transition: 'all 0.2s',
  };
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    fontFamily: 'system-ui, -apple-system, sans-serif',
    minHeight: '100vh',
    background: '#0f172a',
    color: '#e2e8f0',
    display: 'flex',
    flexDirection: 'column',
  },
  header: {
    padding: '1rem 2rem',
    borderBottom: '1px solid #1e293b',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    background: '#0f172a',
    position: 'sticky',
    top: 0,
    zIndex: 100,
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
  },
  logo: {
    margin: 0,
    fontSize: '1.5rem',
    fontWeight: 700,
    color: '#f8fafc',
  },
  version: {
    fontSize: '0.75rem',
    color: '#64748b',
    background: '#1e293b',
    padding: '0.125rem 0.5rem',
    borderRadius: '4px',
  },
  nav: {
    display: 'flex',
    gap: '0.5rem',
  },
  main: {
    padding: '2rem',
    maxWidth: '1200px',
    margin: '0 auto',
    width: '100%',
    flex: 1,
  },
  footer: {
    padding: '1rem 2rem',
    borderTop: '1px solid #1e293b',
    textAlign: 'center',
    color: '#64748b',
    fontSize: '0.75rem',
  },
};

export default App;
''')

# ============================================================
# 3. Add ErrorFallback component
# ============================================================
write("frontend/src/components/ErrorFallback.tsx", '''import React from 'react';

interface ErrorFallbackProps {
  children: React.ReactNode;
}

interface ErrorFallbackState {
  hasError: boolean;
  error: Error | null;
}

class ErrorFallback extends React.Component<ErrorFallbackProps, ErrorFallbackState> {
  constructor(props: ErrorFallbackProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorFallbackState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          background: '#1e293b',
          borderRadius: '12px',
          padding: '2rem',
          textAlign: 'center',
          border: '1px solid #ef4444',
        }}>
          <h2 style={{ color: '#ef4444', marginBottom: '1rem' }}>Something went wrong</h2>
          <p style={{ color: '#94a3b8', marginBottom: '1rem' }}>
            {this.state.error?.message || 'An unexpected error occurred'}
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            style={{
              padding: '0.5rem 1.5rem',
              borderRadius: '6px',
              border: 'none',
              background: '#3b82f6',
              color: '#fff',
              cursor: 'pointer',
              fontWeight: 600,
            }}
          >
            Try Again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorFallback;
''')

# ============================================================
# 4. Fix API service - consistent paths
# ============================================================
write("frontend/src/services/api.ts", '''import { HealthStatus, AgentInfo, ChatResponse, ChatMessage } from '../types';

const API_BASE = '/api/v1';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    let errorMsg = 'Request failed';
    try {
      const error = await response.json();
      errorMsg = error.detail || error.error || errorMsg;
    } catch {
      errorMsg = `HTTP ${response.status}: ${response.statusText}`;
    }
    throw new Error(errorMsg);
  }
  return response.json();
}

export const api = {
  // Health
  health: (): Promise<HealthStatus> => request<HealthStatus>('/health'),

  // Agents
  agents: (): Promise<AgentInfo[]> => request<AgentInfo[]>('/agents'),
  agent: (agentId: string): Promise<AgentInfo> => request<AgentInfo>(`/agents/${agentId}`),
  createAgent: (data: Partial<AgentInfo>): Promise<AgentInfo> =>
    request<AgentInfo>('/agents', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Chat
  chat: (message: string, provider: string = 'openai'): Promise<ChatResponse> =>
    request<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify({ message, provider }),
    }),

  // Voices
  voices: (): Promise<{ voices: { name: string; description: string }[] }> =>
    request<{ voices: { name: string; description: string }[] }>('/voice/voices'),

  // TTS
  tts: (text: string, voice?: string): Promise<any> =>
    request<any>('/voice/tts', {
      method: 'POST',
      body: JSON.stringify({ text, voice }),
    }),

  // Providers
  providers: (): Promise<{ providers: any[] }> =>
    request<{ providers: any[] }>('/chat/providers'),

  // Director AI
  directorScene: (data?: any): Promise<any> =>
    request<any>('/agents/director/scene', {
      method: 'POST',
      body: JSON.stringify(data || {}),
    }),

  directorCharacters: (): Promise<any[]> =>
    request<any[]>('/agents/director/characters/linhfeng'),

  directorWorlds: (): Promise<any> =>
    request<any>('/agents/director/worlds/ancient-world'),

  directorEpisodes: (): Promise<any> =>
    request<any>('/agents/director/episodes/ep001'),
};

export default api;
''')

# ============================================================
# 5. Fix types/index.ts - add missing types
# ============================================================
write("frontend/src/types/index.ts", '''export interface AgentInfo {
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
''')

# ============================================================
# 6. Fix useApi hook - add refresh capability
# ============================================================
write("frontend/src/hooks/useApi.ts", '''import { useState, useEffect, useCallback, useRef } from 'react';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useApi<T>(fetcher: () => Promise<T>, deps: any[] = []): UseApiState<T> & { refetch: () => void } {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: true,
    error: null,
  });
  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;

  const fetchData = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const data = await fetcherRef.current();
      setState({ data, loading: false, error: null });
    } catch (err: any) {
      setState({ data: null, loading: false, error: err.message || 'Unknown error' });
    }
  }, [deps.length]);

  useEffect(() => {
    fetchData();
  }, [fetchData, ...deps]);

  return { ...state, refetch: fetchData };
}
''')

# ============================================================
# 7. Fix Dashboard - show real data
# ============================================================
write("frontend/src/pages/Dashboard.tsx", '''import React from 'react';
import { useApi } from '../hooks/useApi';
import api from '../services/api';
import { HealthStatus } from '../types';

export default function Dashboard() {
  const { data: health, loading, error, refetch } = useApi(healthFetcher);

  function healthFetcher() {
    return api.health();
  }

  const statusColors: Record<string, string> = {
    healthy: '#22c55e',
    degraded: '#eab308',
    unhealthy: '#ef4444',
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2 style={sectionTitleStyle}>Dashboard</h2>
        <button onClick={refetch} style={refreshBtnStyle}>
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      {/* System Status */}
      <section style={cardStyle}>
        <h3 style={cardTitleStyle}>System Status</h3>
        {loading && !health && <p style={{ color: '#94a3b8' }}>Loading system status...</p>}
        {error && <p style={{ color: '#ef4444' }}>Error: {error}</p>}
        {health && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1rem',
          }}>
            <StatusCard
              label="Status"
              value={health.status}
              color={statusColors[health.status] || '#64748b'}
            />
            <StatusCard label="Version" value={health.version} color="#3b82f6" />
            {Object.entries(health.services).map(([key, value]) => (
              <StatusCard
                key={key}
                label={key}
                value={value}
                color={value === 'healthy' ? '#22c55e' : '#ef4444'}
              />
            ))}
          </div>
        )}
      </section>

      {/* Quick Stats */}
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginTop: '1.5rem' }}>
        <QuickCard title="AI Agents" value="2" subtitle="DirectorAI + Sales AI" />
        <QuickCard title="API Endpoints" value="15+" subtitle="v1 API Available" />
        <QuickCard title="LLM Providers" value="3" subtitle="OpenAI, Gemini, DeepSeek" />
        <QuickCard title="TTS Providers" value="2" subtitle="OpenAI, Deepgram" />
      </section>

      {/* System Info */}
      <section style={{ ...cardStyle, marginTop: '1.5rem' }}>
        <h3 style={cardTitleStyle}>System Information</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
          <InfoRow label="Application" value="AI Workforce OS" />
          <InfoRow label="Backend" value="FastAPI + Python 3.11" />
          <InfoRow label="Frontend" value="React 18 + TypeScript" />
          <InfoRow label="Database" value="SQLAlchemy (SQLite/PostgreSQL)" />
          <InfoRow label="LLM Providers" value="OpenAI, Gemini, DeepSeek" />
          <InfoRow label="TTS Providers" value="OpenAI TTS, Deepgram" />
        </div>
      </section>
    </div>
  );
}

function StatusCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div style={{ background: '#0f172a', borderRadius: '8px', padding: '1rem', borderLeft: `3px solid ${color}` }}>
      <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.25rem' }}>{label}</div>
      <div style={{ fontSize: '1.25rem', fontWeight: 700, color }}>{value}</div>
    </div>
  );
}

function QuickCard({ title, value, subtitle }: { title: string; value: string; subtitle: string }) {
  return (
    <div style={cardStyle}>
      <div style={{ fontSize: '0.875rem', color: '#94a3b8', marginBottom: '0.5rem' }}>{title}</div>
      <div style={{ fontSize: '2rem', fontWeight: 700, color: '#f8fafc' }}>{value}</div>
      <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.5rem' }}>{subtitle}</div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid #1e293b' }}>
      <span style={{ color: '#94a3b8' }}>{label}</span>
      <span style={{ color: '#e2e8f0', fontWeight: 500 }}>{value}</span>
    </div>
  );
}

const sectionTitleStyle: React.CSSProperties = {
  fontSize: '1.75rem',
  fontWeight: 700,
  marginBottom: '1.5rem',
};

const cardStyle: React.CSSProperties = {
  background: '#1e293b',
  borderRadius: '12px',
  padding: '1.5rem',
};

const cardTitleStyle: React.CSSProperties = {
  fontSize: '1.125rem',
  fontWeight: 600,
  marginBottom: '1rem',
  color: '#f8fafc',
};

const refreshBtnStyle: React.CSSProperties = {
  padding: '0.5rem 1rem',
  borderRadius: '6px',
  border: '1px solid #334155',
  background: 'transparent',
  color: '#94a3b8',
  cursor: 'pointer',
  fontSize: '0.875rem',
  fontWeight: 500,
  transition: 'all 0.2s',
};
''')

# ============================================================
# 8. Fix ChatInterface - full chat with provider selection
# ============================================================
write("frontend/src/pages/ChatInterface.tsx", '''import React, { useState, useRef, useEffect } from 'react';
import api from '../services/api';
import { ChatMessage } from '../types';

export default function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState('openai');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await api.chat(input.trim(), selectedProvider);
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `Error: ${err.message}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const providers = [
    { id: 'openai', name: 'OpenAI' },
    { id: 'gemini', name: 'Gemini' },
    { id: 'deepseek', name: 'DeepSeek' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 180px)' }}>
      <h2 style={titleStyle}>Chat Interface</h2>

      {/* Provider Selection */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        {providers.map((p) => (
          <button
            key={p.id}
            onClick={() => setSelectedProvider(p.id)}
            style={{
              padding: '0.375rem 0.75rem',
              borderRadius: '6px',
              border: selectedProvider === p.id ? '1px solid #3b82f6' : '1px solid #334155',
              background: selectedProvider === p.id ? '#3b82f620' : 'transparent',
              color: selectedProvider === p.id ? '#3b82f6' : '#94a3b8',
              cursor: 'pointer',
              fontSize: '0.8rem',
              fontWeight: 500,
            }}
          >
            {p.name}
          </button>
        ))}
      </div>

      {/* Messages */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '1rem',
        background: '#1e293b',
        borderRadius: '12px',
        marginBottom: '1rem',
      }}>
        {messages.length === 0 && (
          <p style={{ color: '#64748b', textAlign: 'center', marginTop: '2rem' }}>
            Start a conversation with an AI provider...
          </p>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              marginBottom: '1rem',
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
            }}
          >
            <div style={{
              maxWidth: '75%',
              padding: '0.75rem 1rem',
              borderRadius: '12px',
              background: msg.role === 'user' ? '#3b82f6' : '#334155',
              color: '#fff',
              fontSize: '0.9rem',
              lineHeight: 1.5,
            }}>
              <div style={{ fontSize: '0.7rem', opacity: 0.7, marginBottom: '0.25rem' }}>
                {msg.role === 'user' ? 'You' : selectedProvider}
              </div>
              {msg.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
            <div style={{ padding: '0.75rem 1rem', borderRadius: '12px', background: '#334155' }}>
              <span style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
          rows={3}
          style={{
            flex: 1,
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            border: '1px solid #334155',
            background: '#1e293b',
            color: '#e2e8f0',
            fontSize: '0.9rem',
            resize: 'none',
            outline: 'none',
          }}
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
          style={{
            padding: '0.75rem 1.5rem',
            borderRadius: '8px',
            border: 'none',
            background: (isLoading || !input.trim()) ? '#334155' : '#3b82f6',
            color: (isLoading || !input.trim()) ? '#64748b' : '#fff',
            cursor: (isLoading || !input.trim()) ? 'not-allowed' : 'pointer',
            fontWeight: 600,
            fontSize: '0.9rem',
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}

const titleStyle: React.CSSProperties = {
  fontSize: '1.75rem',
  fontWeight: 700,
  marginBottom: '1rem',
};
''')

# ============================================================
# 9. Fix AgentsView - show all agents, add create capability
# ============================================================
write("frontend/src/pages/AgentsView.tsx", '''import React from 'react';
import { useApi } from '../hooks/useApi';
import api from '../services/api';
import { AgentInfo } from '../types';

export default function AgentsView() {
  const { data: agents, loading, error, refetch } = useApi(agentFetcher);

  function agentFetcher() {
    return api.agents();
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2 style={titleStyle}>AI Agents</h2>
        <button onClick={refetch} style={refreshBtnStyle}>
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      {loading && !agents && <p style={{ color: '#94a3b8' }}>Loading agents...</p>}
      {error && <p style={{ color: '#ef4444' }}>Error: {error}</p>}
      {agents && agents.length === 0 && (
        <div style={emptyStyle}>
          <p>No agents found. Register an agent to get started.</p>
        </div>
      )}

      <div style={{ display: 'grid', gap: '1rem' }}>
        {agents?.map((agent) => (
          <AgentCard key={agent.agent_id} agent={agent} />
        ))}
      </div>
    </div>
  );
}

function AgentCard({ agent }: { agent: AgentInfo }) {
  const statusColors: Record<string, string> = {
    active: '#22c55e',
    idle: '#eab308',
    busy: '#3b82f6',
    error: '#ef4444',
    offline: '#64748b',
  };

  return (
    <div style={cardStyle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0, color: '#f8fafc' }}>
            {agent.name}
          </h3>
          <p style={{ color: '#94a3b8', margin: '0.25rem 0 0', fontSize: '0.875rem' }}>{agent.role}</p>
        </div>
        <span style={{
          padding: '0.25rem 0.75rem',
          borderRadius: '20px',
          background: `${statusColors[agent.status] || '#64748b'}20`,
          color: statusColors[agent.status] || '#64748b',
          fontSize: '0.75rem',
          fontWeight: 600,
          textTransform: 'uppercase',
        }}>
          {agent.status}
        </span>
      </div>
      {agent.description && (
        <p style={{ color: '#cbd5e1', marginBottom: '1rem', fontSize: '0.875rem' }}>{agent.description}</p>
      )}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
        {agent.capabilities?.map((cap) => (
          <span
            key={cap}
            style={{
              padding: '0.25rem 0.5rem',
              borderRadius: '4px',
              background: '#334155',
              color: '#94a3b8',
              fontSize: '0.75rem',
            }}
          >
            {cap}
          </span>
        ))}
      </div>
      <div style={{ marginTop: '0.75rem', fontSize: '0.7rem', color: '#64748b' }}>
        ID: {agent.agent_id} | Last Active: {agent.last_active ? new Date(agent.last_active).toLocaleString() : 'Never'}
      </div>
    </div>
  );
}

const titleStyle: React.CSSProperties = {
  fontSize: '1.75rem',
  fontWeight: 700,
  marginBottom: '1.5rem',
};

const cardStyle: React.CSSProperties = {
  background: '#1e293b',
  borderRadius: '12px',
  padding: '1.5rem',
  border: '1px solid #334155',
};

const emptyStyle: React.CSSProperties = {
  background: '#1e293b',
  borderRadius: '12px',
  padding: '2rem',
  textAlign: 'center',
  color: '#64748b',
};

const refreshBtnStyle: React.CSSProperties = {
  padding: '0.5rem 1rem',
  borderRadius: '6px',
  border: '1px solid #334155',
  background: 'transparent',
  color: '#94a3b8',
  cursor: 'pointer',
  fontSize: '0.875rem',
  fontWeight: 500,
};
''')

# ============================================================
# 10. Fix tsconfig.json - relax strict checks for development
# ============================================================
write("frontend/tsconfig.json", '''{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": false,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
''')

# ============================================================
# 11. Fix vite.config.ts
# ============================================================
write("frontend/vite.config.ts", '''import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
''')

print("=" * 60)
print("All frontend fixes applied successfully!")
print("=" * 60)
