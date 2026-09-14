import React, { useState } from 'react';

export default function SourceViewer({ sources }) {
  const [expanded, setExpanded] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="source-card">
      <div 
        onClick={() => setExpanded(!expanded)} 
        style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}
      >
        <span className="source-header">
          [RETRIEVED SOURCES: {sources.length} CHUNK{sources.length > 1 ? 'S' : ''}]
        </span>
        <span style={{ color: 'var(--color-neon-yellow)', fontSize: '11px', fontFamily: 'Share Tech Mono' }}>
          {expanded ? '[ HIDE DETAILS ]' : '[ INSPECT CITATIONS ]'}
        </span>
      </div>

      {expanded && (
        <div style={{ marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {sources.map((src, idx) => (
            <div 
              key={src.chunk_id || idx}
              style={{
                background: 'rgba(9, 2, 24, 0.8)',
                border: '1px solid rgba(0, 255, 255, 0.3)',
                padding: '8px',
                borderRadius: '2px',
                fontSize: '12px'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--color-neon-cyan)', fontWeight: 'bold', marginBottom: '4px' }}>
                <span>SRC {idx + 1}: {src.filename} (PAGE {src.page_number})</span>
                <span>MATCH SCORE: {(src.similarity_score * 100).toFixed(1)}%</span>
              </div>
              <div style={{ color: '#d0d7de', fontFamily: 'VT323', fontSize: '15px', lineHeight: '1.3' }}>
                "{src.text_snippet}"
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
