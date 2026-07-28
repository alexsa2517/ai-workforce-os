import React, { useState, useRef, useEffect } from 'react';
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
