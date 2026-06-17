'use client';

import { useState, useRef } from 'react';
import { Session, createSession, uploadFile, ingestDocuments } from '@/lib/api';

interface SidebarProps {
  sessions: Session[];
  selectedSessionId: string | null;
  onSessionSelect: (sessionId: string) => void;
  onSessionCreated: (session: Session) => void;
  onSessionDeleted: (sessionId: string) => void;
  isLoading: boolean;
  error: string | null;
}

export default function Sidebar({
  sessions,
  selectedSessionId,
  onSessionSelect,
  onSessionCreated,
  onSessionDeleted,
  isLoading,
  error,
}: SidebarProps) {
  const [isCreatingSession, setIsCreatingSession] = useState<boolean>(false);
  const [newSessionName, setNewSessionName] = useState<string>('');
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [isIngesting, setIsIngesting] = useState<boolean>(false);
  const [ingestError, setIngestError] = useState<string | null>(null);
  const [ingestSuccess, setIngestSuccess] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleCreateSession = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSessionName.trim()) return;

    setIsCreatingSession(true);
    try {
      const session = await createSession({ name: newSessionName });
      onSessionCreated(session);
      setNewSessionName('');
    } catch (err) {
      console.error('Failed to create session:', err);
    } finally {
      setIsCreatingSession(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0 || !selectedSessionId) return;

    setIsUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    const formData = new FormData();
    formData.append('file', files[0]);
    formData.append('session_id', selectedSessionId);

    try {
      const response = await uploadFile(formData);
      setUploadSuccess(`File "${response.filename}" uploaded successfully.`);
      e.target.value = '';
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleIngestDocuments = async () => {
    if (!selectedSessionId) return;

    setIsIngesting(true);
    setIngestError(null);
    setIngestSuccess(null);

    try {
      const response = await ingestDocuments({
        session_id: selectedSessionId,
        file_ids: [], // This would need to be populated with actual file IDs from uploaded files
      });
      setIngestSuccess(`Ingested ${response.chunk_count} chunks successfully.`);
    } catch (err) {
      setIngestError(err instanceof Error ? err.message : 'Ingestion failed');
    } finally {
      setIsIngesting(false);
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    if (!confirm('Are you sure you want to delete this session?')) return;

    try {
      const response = await fetch(`/api/sessions/${sessionId}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        onSessionDeleted(sessionId);
      } else {
        console.error('Failed to delete session');
      }
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <h1 className="text-xl font-bold text-gray-800">Aakaar AI</h1>
        <p className="text-sm text-gray-500">Chat with your documents</p>
      </div>

      <div className="p-4 border-b border-gray-200">
        <form onSubmit={handleCreateSession} className="space-y-3">
          <div>
            <label htmlFor="sessionName" className="block text-sm font-medium text-gray-700 mb-1">
              New Session
            </label>
            <input
              type="text"
              id="sessionName"
              value={newSessionName}
              onChange={(e) => setNewSessionName(e.target.value)}
              placeholder="Enter session name"
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isCreatingSession}
            />
          </div>
          <button
            type="submit"
            disabled={isCreatingSession || !newSessionName.trim()}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isCreatingSession ? 'Creating...' : 'Create Session'}
          </button>
        </form>
      </div>

      <div className="p-4 border-b border-gray-200">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Upload Documents</h2>
        <div className="space-y-3">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            className="hidden"
            accept=".pdf,.txt,.doc,.docx,.xls,.xlsx"
            disabled={!selectedSessionId || isUploading}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={!selectedSessionId || isUploading}
            className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-md text-sm font-medium hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isUploading ? 'Uploading...' : 'Choose File'}
          </button>
          <button
            onClick={handleIngestDocuments}
            disabled={!selectedSessionId || isIngesting}
            className="w-full bg-green-600 text-white py-2 px-4 rounded-md text-sm font-medium hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isIngesting ? 'Ingesting...' : 'Ingest Documents'}
          </button>
        </div>
        {uploadError && (
          <p className="mt-2 text-sm text-red-600">{uploadError}</p>
        )}
        {uploadSuccess && (
          <p className="mt-2 text-sm text-green-600">{uploadSuccess}</p>
        )}
        {ingestError && (
          <p className="mt-2 text-sm text-red-600">{ingestError}</p>
        )}
        {ingestSuccess && (
          <p className="mt-2 text-sm text-green-600">{ingestSuccess}</p>
        )}
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Sessions</h2>
          {isLoading ? (
            <div className="text-center py-4">
              <p className="text-sm text-gray-500">Loading sessions...</p>
            </div>
          ) : error ? (
            <div className="text-center py-4">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          ) : sessions.length === 0 ? (
            <div className="text-center py-4">
              <p className="text-sm text-gray-500">No sessions yet</p>
            </div>
          ) : (
            <ul className="space-y-2">
              {sessions.map((session) => (
                <li key={session.id}>
                  <div className={`flex items-center justify-between p-3 rounded-lg cursor-pointer ${selectedSessionId === session.id ? 'bg-blue-50 border border-blue-200' : 'hover:bg-gray-50'}`}>
                    <button
                      onClick={() => onSessionSelect(session.id)}
                      className="flex-1 text-left"
                    >
                      <h3 className="text-sm font-medium text-gray-900 truncate">{session.name}</h3>
                      <p className="text-xs text-gray-500">
                        {new Date(session.created_at).toLocaleDateString()}
                      </p>
                    </button>
                    <button
                      onClick={() => handleDeleteSession(session.id)}
                      className="ml-2 text-red-600 hover:text-red-800 text-sm"
                      title="Delete session"
                    >
                      Delete
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}