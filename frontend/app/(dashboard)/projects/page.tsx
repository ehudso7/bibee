'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api, ApiError } from '@/lib/api';

interface Project {
  id: string;
  name: string;
  description: string | null;
  status: string;
  vocal_mode: string;
  duration_seconds: number | null;
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
  created: 'bg-gray-600',
  uploading: 'bg-blue-600',
  processing_stems: 'bg-yellow-600',
  stems_ready: 'bg-green-600',
  generating_vocals: 'bg-purple-600',
  vocals_ready: 'bg-green-600',
  mixing: 'bg-orange-600',
  completed: 'bg-green-500',
  failed: 'bg-red-600',
};

const statusLabels: Record<string, string> = {
  created: 'Created',
  uploading: 'Uploading',
  processing_stems: 'Processing Stems',
  stems_ready: 'Stems Ready',
  generating_vocals: 'Generating Vocals',
  vocals_ready: 'Vocals Ready',
  mixing: 'Mixing',
  completed: 'Completed',
  failed: 'Failed',
};

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function formatDuration(seconds: number | null): string {
  if (!seconds) return '--:--';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [pagination, setPagination] = useState<PaginationState>({
    page: 1,
    pageSize: 20,
    total: 0,
    pages: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = async (page: number) => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.projects.list(page, pagination.pageSize);
      setProjects(data.items);
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
        setError('Failed to load projects');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects(1);
  }, []);

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return;

    try {
      await api.projects.delete(id);
      fetchProjects(pagination.page);
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
          <h1 className="text-3xl font-bold">Projects</h1>
          <Link
            href="/projects/new"
            className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold transition"
          >
            New Project
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
        ) : projects.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-400 mb-4">No projects yet. Create your first project to get started!</p>
            <Link
              href="/projects/new"
              className="inline-block px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold transition"
            >
              Create Project
            </Link>
          </div>
        ) : (
          <>
            <div className="grid gap-4">
              {projects.map((project) => (
                <div
                  key={project.id}
                  className="bg-gray-900 rounded-lg p-6 border border-gray-800 hover:border-gray-700 transition"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <Link href={`/projects/${project.id}`}>
                        <h2 className="text-xl font-semibold hover:text-purple-400 transition">
                          {project.name}
                        </h2>
                      </Link>
                      {project.description && (
                        <p className="text-gray-400 mt-1">{project.description}</p>
                      )}
                      <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                        <span>{formatDate(project.created_at)}</span>
                        <span>•</span>
                        <span className="capitalize">{project.vocal_mode}</span>
                        <span>•</span>
                        <span>{formatDuration(project.duration_seconds)}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[project.status] || 'bg-gray-600'}`}
                      >
                        {statusLabels[project.status] || project.status}
                      </span>
                      <button
                        onClick={() => handleDelete(project.id, project.name)}
                        className="p-2 text-gray-400 hover:text-red-500 transition"
                        title="Delete project"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {pagination.pages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-8">
                <button
                  onClick={() => fetchProjects(pagination.page - 1)}
                  disabled={pagination.page === 1}
                  className="px-4 py-2 bg-gray-800 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-700 transition"
                >
                  Previous
                </button>
                <span className="px-4 py-2 text-gray-400">
                  Page {pagination.page} of {pagination.pages}
                </span>
                <button
                  onClick={() => fetchProjects(pagination.page + 1)}
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
