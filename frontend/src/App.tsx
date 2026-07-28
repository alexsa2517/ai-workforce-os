import React, { useState, useCallback } from 'react';
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
