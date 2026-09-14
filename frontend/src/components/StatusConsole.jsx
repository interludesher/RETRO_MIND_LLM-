import React from 'react';

export default function StatusConsole({ healthData, docCount, sessionCount }) {
  return (
    <div className="retro-panel" style={{ padding: '10px 14px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', textAlign: 'center', fontSize: '12px' }}>
        <div>
          <div style={{ color: 'var(--color-text-dim)', fontSize: '10px', fontFamily: 'Press Start 2P' }}>LLM ENGINE</div>
          <div style={{ color: 'var(--color-neon-cyan)', marginTop: '4px', fontWeight: 'bold' }}>
            {healthData?.llm_provider ? healthData.llm_provider.toUpperCase() : 'GROQ MATRIX'}
          </div>
        </div>

        <div>
          <div style={{ color: 'var(--color-text-dim)', fontSize: '10px', fontFamily: 'Press Start 2P' }}>VECTOR STORE</div>
          <div style={{ color: 'var(--color-neon-magenta)', marginTop: '4px', fontWeight: 'bold' }}>
            CHROMADB INDEX
          </div>
        </div>

        <div>
          <div style={{ color: 'var(--color-text-dim)', fontSize: '10px', fontFamily: 'Press Start 2P' }}>DOCUMENTS</div>
          <div style={{ color: 'var(--color-neon-yellow)', marginTop: '4px', fontWeight: 'bold' }}>
            {docCount} LOADED
          </div>
        </div>

        <div>
          <div style={{ color: 'var(--color-text-dim)', fontSize: '10px', fontFamily: 'Press Start 2P' }}>CHAT SESSIONS</div>
          <div style={{ color: 'var(--color-text-green)', marginTop: '4px', fontWeight: 'bold' }}>
            {sessionCount} ACTIVE
          </div>
        </div>
      </div>
    </div>
  );
}
