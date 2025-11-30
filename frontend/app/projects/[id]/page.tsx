'use client';

export default function ProjectDetailPage({ params }: { params: { id: string } }) {
  return (
    <main className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Project Details</h1>
        <p className="text-gray-400">Project ID: {params.id}</p>

        <div className="mt-8 space-y-6">
          <section className="p-6 bg-gray-900 rounded-xl">
            <h2 className="text-xl font-semibold mb-4">Upload Audio</h2>
            <div className="border-2 border-dashed border-gray-700 rounded-lg p-8 text-center">
              <p className="text-gray-400">Drag and drop an audio file or click to browse</p>
            </div>
          </section>

          <section className="p-6 bg-gray-900 rounded-xl">
            <h2 className="text-xl font-semibold mb-4">Processing</h2>
            <div className="space-y-2">
              <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg mr-2">
                Separate Stems
              </button>
              <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg mr-2">
                Generate Vocals
              </button>
              <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg">
                Mix & Export
              </button>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
