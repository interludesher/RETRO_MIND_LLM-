import React, { useState, useEffect, useRef } from 'react';
import MessageItem from './MessageItem';

export default function ChatWindow({ 
  sessions, 
  activeSessionId, 
  onSelectSession, 
  onCreateSession, 
  messages, 
  onSendQuery, 
  querying 
}) {
  const [inputQuery, setInputQuery] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, querying]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputQuery.trim() || querying) return;
    onSendQuery(inputQuery);
    setInputQuery('');
  };

  return (
    <div className="retro-panel" style={{ height: '100%' }}>
      {/* Panel Header */}
      <div className="panel-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span>CHAT TERMINAL MATRIX</span>
          {sessions.length > 0 && (
            <select
              value={activeSessionId || ''}
              onChange={(e) => onSelectSession(e.target.value)}
              style={{
                fontFamily: 'Share Tech Mono',
                fontSize: '12px',
                background: '#090218',
                color: 'var(--color-neon-cyan)',
                border: '1px solid var(--color-neon-cyan)',
                padding: '2px 6px',
                outline: 'none'
              }}
            >
              {sessions.map((sess) => (
                <option key={sess.id} value={sess.id}>
                  THREAD: {sess.title}
                </option>
              ))}
            </select>
          )}
        </div>

        <button
          onClick={onCreateSession}
          className="retro-btn"
          style={{ fontSize: '10px', padding: '4px 8px' }}
        >
          [+ NEW SESSION]
        </button>
      </div>

      {/* Message List Body */}
      <div className="panel-body">
        {messages.length === 0 ? (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--color-text-dim)', textAlign: 'center', gap: '12px' }}>
            <div style={{ fontFamily: 'Press Start 2P', fontSize: '14px', color: 'var(--color-neon-cyan)' }}>
              RETROMIND KNOWLEDGE MATRIX READY
            </div>
            <div style={{ fontFamily: 'VT323', fontSize: '18px', maxWidth: '500px' }}>
              Upload documents using the left panel, then type your natural language question below to initiate RAG vector retrieval and grounded AI analysis.
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <MessageItem key={msg.id} message={msg} />
          ))
        )}

        {/* Loading Indicator */}
        {querying && (
          <div className="message-bubble-assistant" style={{ opacity: 0.85 }}>
            <div className="message-meta message-meta-assistant">
              <span>// RETROMIND AI CORE</span>
              <span>PROCESSING...</span>
            </div>
            <div style={{ fontFamily: 'VT323', fontSize: '18px', color: 'var(--color-neon-magenta)' }}>
              [SEARCHING VECTOR DATABASE AND GENERATING GROUNDED RESPONSE...]
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Query Form Footer */}
      <div style={{ padding: '12px', borderTop: '1px solid var(--color-neon-cyan)', background: '#090218' }}>
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '10px' }}>
          <input
            type="text"
            className="retro-input"
            placeholder="ENTER QUERY FOR RETROMIND VECTOR MATRIX..."
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            disabled={querying || !activeSessionId}
          />
          <button
            type="submit"
            className="retro-btn"
            disabled={!inputQuery.trim() || querying || !activeSessionId}
            style={{ whiteSpace: 'nowrap', padding: '0 20px' }}
          >
            {querying ? '[ RUNNING... ]' : '[ TRANSMIT ]'}
          </button>
        </form>
      </div>
    </div>
  );
}
