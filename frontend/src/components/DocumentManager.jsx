import React, { useState } from 'react';

export default function DocumentManager({ documents, onUpload, onDelete, uploading }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadError, setUploadError] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setUploadError('');
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;
    try {
      await onUpload(selectedFile);
      setSelectedFile(null);
      setUploadError('');
      // Reset input element
      e.target.reset();
    } catch (err) {
      setUploadError(err.message || 'INGESTION ERROR');
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  return (
    <div className="retro-panel-magenta" style={{ height: '100%' }}>
      <div className="panel-header-magenta">
        <span>KNOWLEDGE MATRIX // DOCUMENTS</span>
        <span>[{documents.length}]</span>
      </div>

      <div className="panel-body">
        {/* Upload Form */}
        <form onSubmit={handleUploadSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <label style={{ fontSize: '11px', fontFamily: 'Share Tech Mono', color: 'var(--color-neon-magenta)' }}>
            INGEST NEW DOCUMENT (PDF / TXT / MD):
          </label>
          <input
            type="file"
            accept=".pdf,.txt,.md,.markdown"
            onChange={handleFileChange}
            disabled={uploading}
            style={{
              fontFamily: 'Share Tech Mono',
              fontSize: '12px',
              color: 'var(--color-text-cyan)',
              background: '#090218',
              border: '1px solid var(--color-neon-magenta)',
              padding: '6px',
              cursor: 'pointer'
            }}
          />
          
          <button
            type="submit"
            disabled={!selectedFile || uploading}
            className="retro-btn-magenta"
            style={{ width: '100%', marginTop: '4px' }}
          >
            {uploading ? '[ INGESTING MATRIX... ]' : '[ MOUNT DOCUMENT ]'}
          </button>
        </form>

        {uploadError && (
          <div style={{ color: '#ff3366', fontSize: '12px', background: 'rgba(255,51,102,0.1)', padding: '6px', border: '1px solid #ff3366' }}>
            [ERROR] {uploadError}
          </div>
        )}

        <hr style={{ borderColor: 'rgba(255,0,127,0.3)', margin: '4px 0' }} />

        {/* Document List */}
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {documents.length === 0 ? (
            <div style={{ color: 'var(--color-text-dim)', fontSize: '13px', textAlign: 'center', padding: '20px 0', fontFamily: 'VT323' }}>
              NO DOCUMENTS INGESTED. UPLOAD A FILE TO BEGIN VECTOR SEARCH.
            </div>
          ) : (
            documents.map((doc) => (
              <div
                key={doc.id}
                style={{
                  background: 'rgba(255, 0, 127, 0.05)',
                  border: '1px solid rgba(255, 0, 127, 0.3)',
                  padding: '8px 10px',
                  borderRadius: '2px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '4px'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: 'var(--color-text-cyan)', fontWeight: 'bold', fontSize: '13px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '200px' }}>
                    {doc.filename}
                  </span>
                  <button
                    onClick={() => onDelete(doc.id)}
                    style={{
                      background: 'none',
                      border: '1px solid #ff3366',
                      color: '#ff3366',
                      fontSize: '10px',
                      padding: '2px 6px',
                      cursor: 'pointer',
                      fontFamily: 'Share Tech Mono'
                    }}
                  >
                    [PURGE]
                  </button>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--color-text-dim)' }}>
                  <span>TYPE: {doc.file_type.toUpperCase()}</span>
                  <span>SIZE: {formatBytes(doc.file_size)}</span>
                  <span>CHUNKS: {doc.chunk_count}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
