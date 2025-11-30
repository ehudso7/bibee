import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'bibee - AI Vocal Replacement',
  description: 'Replace vocals in any song with AI',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-950 text-white">{children}</body>
    </html>
  );
}
