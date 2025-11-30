import { Navbar } from '@/components/layout';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-950">
      <Navbar />
      {children}
    </div>
  );
}
