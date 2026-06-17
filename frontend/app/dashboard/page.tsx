```typescript
'use client';

import { useState, useEffect } from 'react';
import { Inter } from 'next/font/google';
import { listSessions } from '@/lib/api';

const inter = Inter({ subsets: ['latin'] });

interface Session {
  id: string;
  name: string;
  created_at: string;
}

interface DashboardStats {
  sessionCount: number;
  uploadCount: number;
  aiQueryCount: number;
}

interface RecentItem {
  id: string;
  type: 'session' | 'upload' | 'query';
  name: string;
  timestamp: string;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({
    sessionCount: 0,
    uploadCount: 0,
    aiQueryCount: 0
  });
  const [recentItems, setRecentItems] = useState<RecentItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch sessions to get session count and recent sessions
        const sessions = await listSessions();
        
        // For now, we'll use mock data for uploads and AI queries
        // In a real app, these would come from their respective API endpoints
        const mockUploadCount = 12;
        const mockAiQueryCount = 47;
        
        // Create recent items from sessions and mock data
        const sessionItems: RecentItem[] = sessions.slice(0, 3).map((session: Session) => ({
          id: session.id,
          type: 'session' as const,
          name: session.name,
          timestamp: session.created_at
        }));

        const mockRecentItems: RecentItem[] = [
          ...sessionItems,
          {
            id: 'upload-1',
            type: 'upload',
            name: 'financial_report.xlsx',
            timestamp: new Date(Date.now() - 3600000).toISOString() // 1 hour ago
          },
          {
            id: 'query-1',
            type: 'query',
            name: 'Q: What were Q3 sales figures?',
            timestamp: new Date(Date.now() - 7200000).toISOString() // 2 hours ago
          },
          {
            id: 'upload-2',
            type: 'upload',
            name: 'customer_feedback.pdf',
            timestamp: new Date(Date.now() - 86400000).toISOString() // 1 day ago
          }
        ];

        setStats({
          sessionCount: sessions.length,
          uploadCount: mockUploadCount,
          aiQueryCount: mockAiQueryCount
        });

        setRecentItems(mockRecentItems);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTypeColor = (type: RecentItem['type']) => {
    switch (type) {
      case 'session':
        return 'bg-blue-100 text-blue-800';
      case 'upload':
        return 'bg-green-100 text-green-800';
      case 'query':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeLabel = (type: RecentItem['type']) => {
    switch (type) {
      case 'session':
        return 'Session';
      case 'upload':
        return 'File Upload';
      case 'query':
        return 'AI Query';
      default:
        return type;
    }
  };

  if (loading) {
    return (
      <div className={`min-h-screen bg-gray-50 ${inter.className}`}>
        <div className="p-8">
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-600">Loading dashboard data...</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-gray-50 ${inter.className}`}>
      <div className="p-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">Overview of your AI assistant activity</p>
        </header>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error loading dashboard</h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>{error}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Sessions Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                  </svg>
                </div>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900">Sessions</h3>
                <p className="text-3xl font-bold text-gray-900 mt-1">{stats.sessionCount}</p>
                <p className="text-sm text-gray-500">Active conversation threads</p>
              </div>
            </div>
          </div>

          {/* Upload Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                  </svg>
                </div>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900">Files Uploaded</h3>
                <p className="text-3xl font-bold text-gray-900 mt-1">{stats.uploadCount}</p>
                <p className="text-sm text-gray-500">Documents processed</p>
              </div>
            </div>
          </div>

          {/* AI Queries Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                  </svg>
                </div>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900">AI Queries</h3>
                <p className="text-3xl font-bold text-gray-900 mt-1">{stats.aiQueryCount}</p>
                <p className="text-sm text-gray-500">Questions answered</p>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity Table */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Recent Activity</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name / Description
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Time
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recentItems.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTypeColor(item.type)}`}>
                        {getTypeLabel(item.type)}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">{item.name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">{formatDate(item.timestamp)}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      {item.type === 'session' && (
                        <a
                          href={`/sessions/${item.id}`}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          View Session
                        </a>
                      )}
                      {item.type === 'upload' && (
                        <button
                          className="text-gray-600 hover:text-gray-900"
                          onClick={() => {/* Handle view upload */}}
                        >
                          View Details
                        </button>
                      )}
                      {item.type === 'query' && (
                        <button
                          className="text-gray-600 hover:text-gray-900"
                          onClick={() => {/* Handle view query */}}
                        >
                          View Response
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {recentItems.length === 0 && (
            <div className="px-6 py-12 text-center">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No recent activity</h3>
              <p className="mt-1 text-sm text-gray-500">Get started by creating a session or uploading a file.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```