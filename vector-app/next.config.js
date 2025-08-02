/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:8080',
  },
  async rewrites() {
    return [
      {
        // Proxy all API routes EXCEPT /api/auth/* to the backend
        source: '/api/((?!auth).*)',
        destination: `${process.env.BACKEND_URL || 'http://localhost:8080'}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;