import { Message } from '@/types/chat';

export interface Session {
  id: string;
  user_id: string;
  name: string;
  created_at: string;
}

export interface SessionCreateRequest {
  name: string;
}

export interface UploadFileRequest {
  file: File;
  session_id: string;
}

export interface UploadFileResponse {
  id: string;
  session_id: string;
  filename: string;
  file_path: string;
  uploaded_at: string;
}

export interface IngestDocumentsRequest {
  session_id: string;
  file_ids: string[];
}

export interface IngestDocumentsResponse {
  message: string;
  chunk_count: number;
}

export interface AIQueryRequest {
  query: string;
  session_id: string;
}

export interface Citation {
  id: string;
  file_id: string;
  content: string;
  row_start: number;
  row_end: number;
  chunk_index: number;
}

export interface AIQueryResponse {
  answer: string;
  citations: Citation[];
}

export interface MessageResponse {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  citations: Citation[];
  created_at: string;
}

export async function createSession(sessionData: SessionCreateRequest): Promise<Session> {
  const response = await fetch('/api/sessions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(sessionData),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create session');
  }
  return response.json();
}

export async function listSessions(): Promise<Session[]> {
  const response = await fetch('/api/sessions');
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch sessions');
  }
  return response.json();
}

export async function getSession(sessionId: string): Promise<Session> {
  const response = await fetch(`/api/sessions/${sessionId}`);
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch session');
  }
  return response.json();
}

export async function getMessages(sessionId: string): Promise<MessageResponse[]> {
  const response = await fetch(`/api/sessions/${sessionId}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch messages');
  }
  return response.json();
}

export async function uploadFile(formData: FormData): Promise<UploadFileResponse> {
  const response = await fetch('/api/upload', {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to upload file');
  }
  return response.json();
}

export async function ingestDocuments(request: IngestDocumentsRequest): Promise<IngestDocumentsResponse> {
  const response = await fetch('/api/ai/ingest', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to ingest documents');
  }
  return response.json();
}

export async function aiQuery(request: AIQueryRequest): Promise<AIQueryResponse> {
  const response = await fetch('/api/ai/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to query AI');
  }
  return response.json();
}