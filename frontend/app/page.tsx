'use client';

import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="text-center max-w-3xl">
        <h1 className="text-6xl font-bold mb-6 bg-gradient-to-r from-purple-500 to-cyan-500 bg-clip-text text-transparent">
          bibee
        </h1>
        <p className="text-xl text-gray-400 mb-8">
          AI-powered vocal replacement for any song. Upload a track, separate stems,
          and replace vocals with your own voice or an AI persona.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/register"
            className="px-8 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold transition"
          >
            Get Started
          </Link>
          <Link
            href="/login"
            className="px-8 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg font-semibold transition"
          >
            Sign In
          </Link>
        </div>
      </div>

      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl">
        <div className="p-6 bg-gray-900 rounded-xl">
          <h3 className="text-xl font-semibold mb-3">Stem Separation</h3>
          <p className="text-gray-400">
            Automatically separate vocals, drums, bass, and instrumentals using Demucs AI.
          </p>
        </div>
        <div className="p-6 bg-gray-900 rounded-xl">
          <h3 className="text-xl font-semibold mb-3">Voice Conversion</h3>
          <p className="text-gray-400">
            Replace original vocals with your voice or create AI voice personas.
          </p>
        </div>
        <div className="p-6 bg-gray-900 rounded-xl">
          <h3 className="text-xl font-semibold mb-3">Pro Mixing</h3>
          <p className="text-gray-400">
            Mix and master your track with professional audio processing tools.
          </p>
        </div>
      </div>
    </main>
  );
}
