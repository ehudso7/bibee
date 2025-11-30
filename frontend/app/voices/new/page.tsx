'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function NewVoicePage() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    router.push('/voices');
  };

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">New Voice Persona</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            placeholder="Voice persona name"
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
            className="w-full p-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold"
          >
            Create Voice Persona
          </button>
        </form>
      </div>
    </main>
  );
}
