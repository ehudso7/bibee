'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';

export default function NewProjectPage() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await api.projects.create({ name, description: description || undefined });
      router.push('/projects');
    } catch (err) {
      setError('Failed to create project. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">New Project</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <p className="text-red-500 text-center">{error}</p>}
          <input
            type="text"
            placeholder="Project name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full p-3 bg-gray-900 rounded-lg border border-gray-800 focus:border-purple-500 outline-none"
            required
          />
          <textarea
            placeholder="Description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full p-3 bg-gray-900 rounded-lg border border-gray-800 focus:border-purple-500 outline-none h-32"
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full p-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold disabled:opacity-50"
          >
            {loading ? 'Creating...' : 'Create Project'}
          </button>
        </form>
      </div>
    </main>
  );
}
