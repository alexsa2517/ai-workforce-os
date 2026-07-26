import React from 'react';
import { useApi } from '../hooks/useApi';
import api from '../services/api';
import { HealthStatus } from '../types';

export default function Dashboard() {
  const { data: health, loading, error } = useApi(healthFetcher);

  function healthFetcher() {
    return api.health();
  }

  return (
    <div>
      <h2 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '1.5rem' }}>Dashboard</h2>

      {/* System Status */}
      <section style={{ background: '#1e293b', borderRadius: '12px', padding: '1.5rem', marginBottom: '1.5rem' }}>
        <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem' }}>System Status</h3>
        {loading && <p>Loading...</p>}
        {error && <p style={{ color: '#ef4444' }}>Error: {error}</p>}
        {health && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <StatusCard label="Status" value={health.status} color="#22c55e" />
            <StatusCard label="Version" value={health.version} color="#3b82f6" />
            {Object.entries(health.services).map(([key, value]) => (
              <StatusCard key={key} label={key} value={value} color={value === 'healthy' ? '#22c55e' : '#ef4444'} />
            ))}
          </div>
        )}
      </section>

      {/* Quick Stats */}
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
        <QuickCard title="AI Agents" value="1" subtitle="DirectorAI Active" />
        <QuickCard title="API Endpoints" value="12" subtitle="v1 API Available" />
        <QuickCard title="LLM Providers" value="3" subtitle="OpenAI, Gemini, DeepSeek" />
        <QuickCard title="Uptime" value="99.9%" subtitle="System Health" />
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
    <div style={{ background: '#1e293b', borderRadius: '12px', padding: '1.5rem' }}>
      <div style={{ fontSize: '0.875rem', color: '#94a3b8', marginBottom: '0.5rem' }}>{title}</div>
      <div style={{ fontSize: '2rem', fontWeight: 700, color: '#f8fafc' }}>{value}</div>
      <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.5rem' }}>{subtitle}</div>
    </div>
  );
}
