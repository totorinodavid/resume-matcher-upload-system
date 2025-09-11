const path = require('path')
/** @type {import('next').NextConfig} */
const nextConfig = {
  serverExternalPackages: ['@prisma/client', 'prisma'],
  outputFileTracingRoot: __dirname,
  typescript: { ignoreBuildErrors: false }
}
module.exports = nextConfig
