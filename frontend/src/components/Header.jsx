import React, { useState, useEffect } from 'react';

export default function Header({ enableCRT, setEnableCRT, systemStatus }) {
  const [timeStr, setTimeStr] = useState('');

  useEffect(() => {
    const updateClock = () => {
      const now = new Date();
      setTimeStr(now.toTimeString().split(' ')[0] + ' SYSTEM TIME');
    };
    updateClock();
    const interval = setInterval(updateClock, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="retro-panel" style={{ padding: '12px 20px', flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <h1 className="chrome-text" style={{ fontSize: '22px', margin: 0 }}>RETROMIND</h1>
        <span style={{ fontFamily: 'VT323', fontSize: '18px', color: 'var(--color-neon-magenta)' }}>
          // RAG KNOWLEDGE BASE V1.0
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        <div style={{ fontFamily: 'Share Tech Mono', fontSize: '13px', color: 'var(--color-neon-cyan)' }}>
          {timeStr}
        </div>

        <button 
          onClick={() => setEnableCRT(!enableCRT)} 
          className="retro-btn"
          style={{ fontSize: '11px', padding: '6px 12px' }}
        >
          CRT SCANLINES: {enableCRT ? '[ON]' : '[OFF]'}
        </button>

        <span className={`status-badge ${systemStatus === 'ONLINE' ? 'status-badge-green' : 'status-badge-magenta'}`}>
          STATUS: {systemStatus}
        </span>
      </div>
    </header>
  );
}
