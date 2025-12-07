'use client';

import { useCallback, useEffect, useState } from 'react';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api, ApiError } from '@/lib/api';

interface VoicePersona {
  id: string;
  name: string;
  description: string | null;
  status: 'pending' | 'training' | 'ready' | 'failed';
  sample_paths?: string[];  // Optional - not included in list responses
  sample_paths: string[];
  created_at: string;
  updated_at: string;
}

interface PaginationState {
  page: number;
  pageSize: number;
  total: number;
  pages: number;
}

const statusColors: Record<string, string> = {
  pending: 'bg-gray-600',
  training: 'bg-yellow-600',
  ready: 'bg-green-500',
  failed: 'bg-red-600',
};

const statusLabels: Record<string, string> = {
  pending: 'Pending',
  training: 'Training',
  ready: 'Ready',
  failed: 'Failed',
};

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export default function VoicesPage() {
  const [voices, setVoices] = useState<VoicePersona[]>([]);
  const [pagination, setPagination] = useState<PaginationState>({
    page: 1,
    pageSize: 20,
    total: 0,
    pages: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchVoices = useCallback(async (page: number) => {
  const fetchVoices = async (page: number) => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.voices.list(page, pagination.pageSize);
      setVoices(data.items);
      setPagination({
        page: data.page,
        pageSize: data.page_size,
        total: data.total,
        pages: data.pages,
      });
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError('Failed to load voice personas');
      }
    } finally {
      setLoading(false);
    }
  }, [pagination.pageSize]);

  useEffect(() => {
    fetchVoices(1);
  }, [fetchVoices]);
  };

  useEffect(() => {
    fetchVoices(1);
  }, []);

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return;

    try {
      await api.voices.delete(id);
      fetchVoices(pagination.page);
    } catch (err) {
      if (err instanceof ApiError) {
        alert(`Failed to delete: ${err.detail}`);
      }
    }
  };

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Voice Personas</h1>
          <Link
            href="/voices/new"
            className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold transition"
          >
            New Voice Persona
          </Link>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
            <p className="text-red-500">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
          </div>
        ) : voices.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-400 mb-4">No voice personas yet. Create your first voice persona!</p>
            <Link
              href="/voices/new"
              className="inline-block px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold transition"
            >
              Create Voice Persona
            </Link>
          </div>
        ) : (
          <>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {voices.map((voice) => (
                <div
                  key={voice.id}
                  className="bg-gray-900 rounded-lg p-6 border border-gray-800 hover:border-gray-700 transition"
                >
                  <div className="flex items-start justify-between mb-4">
                    <Link href={`/voices/${voice.id}`}>
                      <h2 className="text-xl font-semibold hover:text-purple-400 transition">
                        {voice.name}
                      </h2>
                    </Link>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[voice.status] || 'bg-gray-600'}`}
                    >
                      {statusLabels[voice.status] || voice.status}
                    </span>
                  </div>

                  {voice.description && (
                    <p className="text-gray-400 text-sm mb-4 line-clamp-2">{voice.description}</p>
                  )}

                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>{voice.sample_paths?.length || 0} samples</span>
                    <span>{formatDate(voice.created_at)}</span>
                  </div>

                  <div className="flex items-center gap-2 mt-4 pt-4 border-t border-gray-800">
                    <Link
                      href={`/voices/${voice.id}`}
                      className="flex-1 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-center text-sm transition"
                    >
                      View Details
                    </Link>
                    <button
                      onClick={() => handleDelete(voice.id, voice.name)}
                      className="p-2 text-gray-400 hover:text-red-500 transition"
                      title="Delete voice persona"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {pagination.pages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-8">
                <button
                  onClick={() => fetchVoices(pagination.page - 1)}
                  disabled={pagination.page === 1}
                  className="px-4 py-2 bg-gray-800 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-700 transition"
                >
                  Previous
                </button>
                <span className="px-4 py-2 text-gray-400">
                  Page {pagination.page} of {pagination.pages}
                </span>
                <button
                  onClick={() => fetchVoices(pagination.page + 1)}
                  disabled={pagination.page === pagination.pages}
                  className="px-4 py-2 bg-gray-800 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-700 transition"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
}
