import React, { useState } from 'react';
import api from '../services/api';
import { ChatMessage } from '../types';

export default function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [provider, setProvider] = useState('openai');

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMsg: ChatMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.chat(input, provider);
      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        role: 'assistant',
        content: `Error: ${err.message}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 140px)' }}>
      <h2 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '1rem' }}>Chat</h2>

      {/* Provider Selection */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        {['openai', 'gemini', 'deepseek'].map((p) => (
          <button
            key={p}
            onClick={() => setProvider(p)}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              border: '1px solid',
              borderColor: provider === p ? '#3b82f6' : '#334155',
              background: provider === p ? '#1e3a5f' : '#1e293b',
              color: provider === p ? '#60a5fa' : '#94a3b8',
              cursor: 'pointer',
              fontSize: '0.875rem',
            }}
          >
            {p}
          </button>
        ))}
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflow: 'auto', background: '#1e293b', borderRadius: '12px', padding: '1.5rem', marginBottom: '1rem' }}>
        {messages.length === 0 && (
          <p style={{ color: '#64748b', textAlign: 'center', marginTop: '2rem' }}>Send a message to start chatting</p>
        )}
        {messages.map((msg, i) => (
          <div key={i} style={{ marginBottom: '1rem', display: 'flex', flexDirection: msg.role === 'user' ? 'row-reverse' : 'row' }}>
            <div
              style={{
                maxWidth: '75%',
                padding: '0.75rem 1rem',
                borderRadius: '12px',
                background: msg.role === 'user' ? '#3b82f6' : '#334155',
                color: '#fff',
              }}
            >
              <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.25rem' }}>{msg.role === 'user' ? 'You' : 'AI'}</div>
              <div>{msg.content}</div>
            </div>
          </div>
        ))}
        {loading && <p style={{ color: '#60a5fa' }}>AI is thinking...</p>}
      </div>

      {/* Input */}
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Type your message..."
          style={{
            flex: 1,
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            border: '1px solid #334155',
            background: '#0f172a',
            color: '#e2e8f0',
            fontSize: '0.875rem',
            outline: 'none',
          }}
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          style={{
            padding: '0.75rem 1.5rem',
            borderRadius: '8px',
            border: 'none',
            background: '#3b82f6',
            color: '#fff',
            cursor: 'pointer',
            fontWeight: 600,
            opacity: loading || !input.trim() ? 0.5 : 1,
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}
