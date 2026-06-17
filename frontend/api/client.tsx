```typescript
import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

// Base URL for API requests
const baseURL = process.env.NEXT_PUBLIC_API_URL || '';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token from localStorage
api.interceptors.request.use(
  (config) => {
    // Only run in browser environment
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// TypeScript interfaces for API requests and responses

// Session related interfaces
export interface SessionCreateRequest {
  name: string;
  user_id?: number;
}

export interface SessionResponse {
  id: number;
  user_id: number;
  name: string;
  created_at: string;
}

export interface SessionListResponse {
  sessions: SessionResponse[];
}

// Message related interfaces
export interface MessageCreateRequest {
  role: 'user' | 'assistant';
  content: string;
  citations?: string[];
}

export interface MessageResponse {
  id: number;
  session_id: number;
  role: 'user' | 'assistant';
  content: string;
  citations: string[];
  created_at: string;
}

export interface MessageListResponse {
  messages: MessageResponse[];
}

// File upload related interfaces
export interface UploadFileRequest {
  file: File;
  session_id: number;
}

export interface UploadedFileResponse {
  id: number;
  session_id: number;
  filename: string;
  file_path: string;
  uploaded_at: string;
}

// AI related interfaces
export interface IngestDocumentsRequest {
  session_id: number;
  file_ids: number[];
}

export interface IngestDocumentsResponse {
  message: string;
  chunk_count: number;
  file_ids: number[];
}

export interface AIQueryRequest {
  query: string;
  session_id: number;
}

export interface SourceCitation {
  id: number;
  file_id: number;
  content: string;
  row_start: number;
  row_end: number;
  chunk_index: number;
  similarity_score: number;
}

export interface AIQueryResponse {
  answer: string;
  citations: SourceCitation[];
  session_id: number;
  query: string;
}

// API functions

// Sessions API
export const createSession = async (data: SessionCreateRequest): Promise<SessionResponse> => {
  const response: AxiosResponse<SessionResponse> = await api.post('/api/sessions', data);
  return response.data;
};

export const listSessions = async (): Promise<SessionListResponse> => {
  const response: AxiosResponse<SessionListResponse> = await api.get('/api/sessions');
  return response.data;
};

export const getSession = async (sessionId: number): Promise<SessionResponse> => {
  const response: AxiosResponse<SessionResponse> = await api.get(`/api/sessions/${sessionId}`);
  return response.data;
};

// Messages API
export const getMessages = async (sessionId: number): Promise<MessageListResponse> => {
  const response: AxiosResponse<MessageListResponse> = await api.post(`/api/sessions/${sessionId}/messages`);
  return response.data;
};

// File upload API
export const uploadFile = async (data: FormData): Promise<UploadedFileResponse> => {
  const response: AxiosResponse<UploadedFileResponse> = await api.post('/api/upload', data, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// AI API
export const ingestDocuments = async (data: IngestDocumentsRequest): Promise<IngestDocumentsResponse> => {
  const response: AxiosResponse<IngestDocumentsResponse> = await api.post('/api/ai/ingest', data);
  return response.data;
};

export const aiQuery = async (data: AIQueryRequest): Promise<AIQueryResponse> => {
  const response: AxiosResponse<AIQueryResponse> = await api.post('/api/ai/query', data);
  return response.data;
};

// Helper function to create FormData for file upload
export const createUploadFormData = (file: File, sessionId: number): FormData => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('session_id', sessionId.toString());
  return formData;
};

// Export the axios instance for custom requests
export default api;
```