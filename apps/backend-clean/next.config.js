const path = require('path')
/** @type {import('next').NextConfig} */
const nextConfig = {
  serverExternalPackages: ['@prisma/client', 'prisma'],
  outputFileTracingRoot: __dirname,
  // Render often builds with NODE_ENV=production and omits devDependencies.
  // Disable TS type checking in build to avoid requiring typescript/@types packages.
  typescript: { ignoreBuildErrors: true }
}
module.exports = nextConfig
