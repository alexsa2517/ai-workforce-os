import React from 'react';
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
