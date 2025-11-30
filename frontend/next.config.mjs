/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Enable standalone output for Docker builds only
  // Vercel sets the VERCEL env var, so we skip standalone mode there
  ...(process.env.VERCEL ? {} : { output: 'standalone' }),
};

export default nextConfig;
