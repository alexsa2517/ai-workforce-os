import React from 'react';
import { ChatMessage } from '../types';

interface ChatBubbleProps {
  message: ChatMessage;
}

export default function ChatBubble({ message }: ChatBubbleProps) {
  const isUser = message.role === 'user';
  const time = message.timestamp
    ? new Date(message.timestamp).toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })
    : '';

  return (
    <div style={{
      display: 'flex',
      justifyContent: isUser ? 'flex-end' : 'flex-start',
      marginBottom: '1rem',
    }}>
      <div style={{
        maxWidth: '70%',
        padding: '0.75rem 1rem',
        borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
        background: isUser ? '#3b82f6' : '#1e293b',
        color: isUser ? '#fff' : '#e2e8f0',
        position: 'relative',
      }}>
        <p style={{ margin: 0, fontSize: '0.9rem', lineHeight: 1.5, whiteSpace: 'pre-wrap' }}>
          {message.content}
        </p>
        {time && (
          <span style={{
            fontSize: '0.7rem',
            color: isUser ? 'rgba(255,255,255,0.7)' : '#64748b',
            marginTop: '0.25rem',
            display: 'block',
            textAlign: isUser ? 'right' : 'left',
          }}>
            {time}
          </span>
        )}
      </div>
    </div>
  );
}
