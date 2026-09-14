import React from 'react';

export default function CRTOverlay({ enableCRT = true }) {
  return (
    <>
      <div className="retro-background" />
      <div className="perspective-grid" />
      {enableCRT && (
        <>
          <div className="crt-overlay" />
          <div className="crt-vignette" />
        </>
      )}
    </>
  );
}
