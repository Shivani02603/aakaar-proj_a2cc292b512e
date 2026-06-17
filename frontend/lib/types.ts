export interface Session {
  id: string;
  user_id: string;
  name: string;
  created_at: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  citations: string[];
  created_at: string;
}

export interface UploadedFile {
  id: string;
  session_id: string;
  filename: string;
  file_path: string;
  uploaded_at: string;
}