import type { NextConfig } from 'next';
import path from 'path';
import createNextIntlPlugin from 'next-intl/plugin';
import { withSentryConfig } from '@sentry/nextjs';

// Explicitly point plugin to the config to avoid path resolution issues in some runtimes
const withNextIntl = createNextIntlPlugin(path.join(__dirname, './i18n.ts'));

// Ensure build-time environment variables
if (!process.env.DATABASE_URL && process.env.NEXT_PHASE === 'phase-production-build') {
	process.env.DATABASE_URL = 'postgresql://dummy:dummy@dummy:5432/dummy'
}
if (!process.env.NEXTAUTH_SECRET && process.env.NEXT_PHASE === 'phase-production-build') {
	process.env.NEXTAUTH_SECRET = 'dummy-secret-for-build'
}
// Provide a build-time fallback for AUTH_SECRET too (Auth.js v5 default)
if (!process.env.AUTH_SECRET && process.env.NEXT_PHASE === 'phase-production-build') {
	process.env.AUTH_SECRET = process.env.NEXTAUTH_SECRET || 'dummy-secret-for-build'
}

const nextConfig: NextConfig = {
	// Fix workspace root detection issue
	outputFileTracingRoot: path.join(__dirname, '../../'),
	// Remove any experimental turbo configuration to avoid conflicts
	experimental: {
		// Remove any experimental.turbo config if it exists
	},
	webpack: (config) => {
		config.resolve.alias = {
			...(config.resolve.alias ?? {}),
			'@': path.resolve(__dirname),
		};
		return config;
	},
	async rewrites() {
		// Default to Render backend URL in production if no env is set; keep localhost in dev
		const defaultBackend = process.env.NODE_ENV === 'development'
			? 'http://localhost:8000'
			: 'https://resume-matcher-backend-j06k.onrender.com';
		const backend = process.env.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_URL || defaultBackend;
		return [
			{
				source: '/api_be/:path*',
				destination: `${backend}/:path*`,
			},
		];
	},
};

const intlWrapped = withNextIntl(nextConfig);
const maybeSentry = process.env.SENTRY_DSN_FRONTEND
	? withSentryConfig(intlWrapped, { silent: true })
	: intlWrapped;

export default maybeSentry;

