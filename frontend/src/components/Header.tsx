import React from 'react';

interface HeaderProps {
  currentPage: 'dashboard' | 'chat' | 'agents';
  onNavigate: (page: 'dashboard' | 'chat' | 'agents') => void;
}

export default function Header({ currentPage, onNavigate }: HeaderProps) {
  const navItems: Array<{ id: 'dashboard' | 'chat' | 'agents'; label: string }> = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'chat', label: 'Chat' },
    { id: 'agents', label: 'Agents' },
  ];

  return (
    <header style={{
      padding: '1rem 2rem',
      borderBottom: '1px solid #1e293b',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      background: '#0f172a',
      position: 'sticky',
      top: 0,
      zIndex: 50,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '8px',
          background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontWeight: 700,
          color: '#fff',
          fontSize: '0.875rem',
        }}>
          AI
        </div>
        <h1 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc' }}>
          AI Workforce OS
        </h1>
      </div>
      <nav style={{ display: 'flex', gap: '0.5rem' }}>
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onNavigate(item.id)}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              border: 'none',
              background: currentPage === item.id ? '#3b82f6' : 'transparent',
              color: currentPage === item.id ? '#fff' : '#94a3b8',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: 500,
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              if (currentPage !== item.id) {
                (e.target as HTMLButtonElement).style.background = '#1e293b';
                (e.target as HTMLButtonElement).style.color = '#e2e8f0';
              }
            }}
            onMouseLeave={(e) => {
              if (currentPage !== item.id) {
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
  );
}
