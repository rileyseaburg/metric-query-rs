import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  eslint: {
    // Don't run ESLint during build
    ignoreDuringBuilds: true
  },
  typescript: {
    // Don't run TypeScript type checking during build
    ignoreBuildErrors: true
  },
  // Add API rewrites to proxy requests in development
  async rewrites() {
    // Determine the API destination based on environment
    let apiDestination = 'http://localhost:5000/:path*'; // Default for local development
    
    if (process.env.DOCKER_ENV === 'true') {
      apiDestination = 'http://api:5000/:path*';  // Docker environment
    } else if (process.env.NODE_ENV === 'production') {
      // In production, use the API domain
      apiDestination = 'https://api-metrics-demandbase.rileyseaburg.com/:path*';
    }
    
    return [
      {
        source: '/api/:path*',
        destination: apiDestination
      }
    ];
  }
};

export default nextConfig;
