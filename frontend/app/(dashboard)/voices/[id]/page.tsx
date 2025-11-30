'use client';

export default function VoiceDetailPage({ params }: { params: { id: string } }) {
  return (
    <main className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Voice Persona Details</h1>
        <p className="text-gray-400 mb-8">Voice ID: {params.id}</p>

        <section className="p-6 bg-gray-900 rounded-xl">
          <h2 className="text-xl font-semibold mb-4">Upload Voice Samples</h2>
          <div className="border-2 border-dashed border-gray-700 rounded-lg p-8 text-center">
            <p className="text-gray-400">Upload 3-10 voice samples (30 seconds each)</p>
          </div>
          <button className="mt-4 px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold">
            Start Training
          </button>
        </section>
      </div>
    </main>
  );
}
