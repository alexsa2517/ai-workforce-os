import React, { useState } from 'react';
import Dashboard from './pages/Dashboard';
import ChatInterface from './pages/ChatInterface';
import AgentsView from './pages/AgentsView';

function App() {
  const [currentPage, setCurrentPage] = useState<'dashboard' | 'chat' | 'agents'>('dashboard');

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

  return (
    <div style={{ fontFamily: 'system-ui, -apple-system, sans-serif', minHeight: '100vh', background: '#0f172a', color: '#e2e8f0' }}>
      {/* Header */}
      <header style={{ padding: '1rem 2rem', borderBottom: '1px solid #1e293b', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 700 }}>AI Workforce OS</h1>
        <nav style={{ display: 'flex', gap: '1rem' }}>
          <button onClick={() => setCurrentPage('dashboard')} style={navBtnStyle(currentPage === 'dashboard')}>Dashboard</button>
          <button onClick={() => setCurrentPage('chat')} style={navBtnStyle(currentPage === 'chat')}>Chat</button>
          <button onClick={() => setCurrentPage('agents')} style={navBtnStyle(currentPage === 'agents')}>Agents</button>
        </nav>
      </header>

      {/* Main Content */}
      <main style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
        {renderPage()}
      </main>
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

export default App;
