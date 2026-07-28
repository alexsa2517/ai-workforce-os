import React from 'react';

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
