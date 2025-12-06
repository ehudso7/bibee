'use client';

import Link from 'next/link';

export default function DashboardPage() {
  return (
    <main className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Link href="/projects" className="p-6 bg-gray-900 rounded-xl hover:bg-gray-800 transition">
            <h2 className="text-xl font-semibold mb-2">Projects</h2>
            <p className="text-gray-400">Manage your vocal replacement projects</p>
          </Link>
          <Link href="/voices" className="p-6 bg-gray-900 rounded-xl hover:bg-gray-800 transition">
            <h2 className="text-xl font-semibold mb-2">Voice Personas</h2>
            <p className="text-gray-400">Create and manage your voice personas</p>
          </Link>
        </div>

        <div className="flex gap-4">
          <Link
            href="/projects/new"
            className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold transition"
          >
            New Project
          </Link>
          <Link
            href="/voices/new"
            className="px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg font-semibold transition"
          >
            New Voice Persona
          </Link>
        </div>
      </div>
    </main>
  );
}
