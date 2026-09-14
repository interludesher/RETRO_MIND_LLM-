import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import StatusConsole from './components/StatusConsole';
import DocumentManager from './components/DocumentManager';
import ChatWindow from './components/ChatWindow';
import CRTOverlay from './components/CRTOverlay';

export default function App() {
  const [enableCRT, setEnableCRT] = useState(true);
  const [healthData, setHealthData] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  
  const [uploading, setUploading] = useState(false);
  const [querying, setQuerying] = useState(false);

  // Fetch health telemetry on startup
  useEffect(() => {
    fetch('/api/v1/health')
      .then((res) => res.json())
      .then((data) => setHealthData(data))
      .catch(() => setHealthData({ status: 'OFFLINE' }));

    fetchDocuments();
    fetchSessions();
  }, []);

  // Fetch session messages when activeSessionId changes
  useEffect(() => {
    if (activeSessionId) {
      fetchSessionMessages(activeSessionId);
    } else {
      setMessages([]);
    }
  }, [activeSessionId]);

  const fetchDocuments = async () => {
    try {
      const res = await fetch('/api/v1/documents');
      if (res.ok) {
        const data = await res.json();
        setDocuments(data);
      }
    } catch (err) {
      console.error('Failed to fetch documents:', err);
    }
  };

  const fetchSessions = async () => {
    try {
      const res = await fetch('/api/v1/chat/sessions');
      if (res.ok) {
        const data = await res.json();
        setSessions(data);
        if (data.length > 0) {
          setActiveSessionId(data[0].id);
        } else {
          // Create initial session if none exists
          handleCreateSession();
        }
      }
    } catch (err) {
      console.error('Failed to fetch chat sessions:', err);
    }
  };

  const fetchSessionMessages = async (sessionId) => {
    try {
      const res = await fetch(`/api/v1/chat/sessions/${sessionId}/messages`);
      if (res.ok) {
        const data = await res.json();
        setMessages(data);
      }
    } catch (err) {
      console.error('Failed to fetch messages:', err);
    }
  };

  const handleCreateSession = async () => {
    try {
      const title = `Matrix Session #${sessions.length + 1}`;
      const res = await fetch('/api/v1/chat/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
      });
      if (res.ok) {
        const newSession = await res.json();
        setSessions((prev) => [newSession, ...prev]);
        setActiveSessionId(newSession.id);
      }
    } catch (err) {
      console.error('Failed to create session:', err);
    }
  };

  const handleUploadDocument = async (file) => {
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch('/api/v1/documents/upload', {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Upload failed');
      }

      await fetchDocuments();
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteDocument = async (docId) => {
    try {
      const res = await fetch(`/api/v1/documents/${docId}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        await fetchDocuments();
      }
    } catch (err) {
      console.error('Failed to delete document:', err);
    }
  };

  const handleSendQuery = async (queryText) => {
    if (!activeSessionId) return;
    setQuerying(true);

    // Optimistically add user query to UI state
    const tempUserMsg = {
      id: `temp_${Date.now()}`,
      role: 'user',
      content: queryText,
      timestamp: new Date().toISOString()
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const res = await fetch('/api/v1/chat/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: activeSessionId,
          query: queryText
        })
      });

      if (res.ok) {
        const data = await res.json();
        // Refresh session messages from DB backend
        await fetchSessionMessages(activeSessionId);
      } else {
        const errData = await res.json();
        const errorAssistantMsg = {
          id: `err_${Date.now()}`,
          role: 'assistant',
          content: `[SYSTEM ERROR] ${errData.detail || 'Query processing failed.'}`,
          timestamp: new Date().toISOString()
        };
        setMessages((prev) => [...prev, errorAssistantMsg]);
      }
    } catch (err) {
      const errorAssistantMsg = {
        id: `err_${Date.now()}`,
        role: 'assistant',
        content: `[NETWORK ERROR] Failed to reach RetroMind backend matrix.`,
        timestamp: new Date().toISOString()
      };
      setMessages((prev) => [...prev, errorAssistantMsg]);
    } finally {
      setQuerying(false);
    }
  };

  return (
    <>
      <CRTOverlay enableCRT={enableCRT} />
      
      <div className="app-viewport">
        {/* Header Banner */}
        <Header 
          enableCRT={enableCRT} 
          setEnableCRT={setEnableCRT} 
          systemStatus={healthData?.status || 'OFFLINE'} 
        />

        {/* System Telemetry Console */}
        <StatusConsole 
          healthData={healthData} 
          docCount={documents.length} 
          sessionCount={sessions.length} 
        />

        {/* Main Interface Grid */}
        <div className="main-content-grid">
          <DocumentManager
            documents={documents}
            onUpload={handleUploadDocument}
            onDelete={handleDeleteDocument}
            uploading={uploading}
          />

          <ChatWindow
            sessions={sessions}
            activeSessionId={activeSessionId}
            onSelectSession={setActiveSessionId}
            onCreateSession={handleCreateSession}
            messages={messages}
            onSendQuery={handleSendQuery}
            querying={querying}
          />
        </div>
      </div>
    </>
  );
}
