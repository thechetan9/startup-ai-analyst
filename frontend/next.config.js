/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  // Removed deprecated swcMinify (enabled by default in Next.js 15+)
  // Removed deprecated experimental.esmExternals

  // Removed outputFileTracingRoot to fix import path issues in GitHub Actions

  // Disable TypeScript checking during build for deployment
  typescript: {
    ignoreBuildErrors: true,
  },

  // Enable static export for Firebase hosting
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },

  webpack: (config, { dev }) => {
    if (dev) {
      config.watchOptions = {
        poll: 1000,
        aggregateTimeout: 300,
      }
    }
    config.externals = [...config.externals, { canvas: 'canvas' }]
    return config
  }
}

module.exports = nextConfig
