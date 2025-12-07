'use client';

import Link from 'next/link';

export default function VoicesPage() {
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
        <p className="text-gray-400">No voice personas yet. Create your first voice persona!</p>
      </div>
    </main>
  );
}
