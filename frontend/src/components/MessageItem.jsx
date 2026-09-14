import React from 'react';
import SourceViewer from './SourceViewer';

export default function MessageItem({ message }) {
  const isUser = message.role === 'user';

  const formatTimestamp = (ts) => {
    if (!ts) return '';
    try {
      const date = new Date(ts);
      return date.toLocaleTimeString();
    } catch {
      return ts;
    }
  };

  return (
    <div className={isUser ? 'message-bubble-user' : 'message-bubble-assistant'}>
      <div className={`message-meta ${isUser ? 'message-meta-user' : 'message-meta-assistant'}`}>
        <span>{isUser ? '// USER ACCESS TERMINAL' : '// RETROMIND AI KNOWLEDGE MATRIX'}</span>
        <span>{formatTimestamp(message.timestamp)}</span>
      </div>

      <div className="message-text">
        {message.content}
      </div>

      {!isUser && message.sources && message.sources.length > 0 && (
        <SourceViewer sources={message.sources} />
      )}
    </div>
  );
}
